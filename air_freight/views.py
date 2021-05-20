from django.shortcuts import render

# Create your views here.

from decimal import *
from django.views import View

from menu.views import get_user_grant_list
from .models import Const, Zone24Detail, Zone48Detail, Charge24, Charge48, CustomProfitRate, GeneralCharge

MY_MENU_LOCAL = 'AIR'


def get_calcVolumeWeight(quote_type, volume, weight):
    """计算体积重"""
    if quote_type == "24HOURS":
        try:
            FixUnit = float(Const.objects.all().filter(unit_item__iexact='CMB24HR')[0].unit_change)
        except:
            FixUnit = 0
        Compare_Volume = volume * FixUnit
        calcVolumeWeight = Compare_Volume
        if Compare_Volume < weight:
            calcVolumeWeight = weight
    else:
        try:
            FixUnit = float(Const.objects.all().filter(unit_item__iexact='CMB48HR')[0].unit_change)
        except:
            FixUnit = 0
        Compare_Volume = weight / FixUnit
        calcVolumeWeight = volume
        if Compare_Volume > volume:
            calcVolumeWeight = Compare_Volume

    return Decimal(calcVolumeWeight)


def get_custom_profit_rate(quote_type, calc_volume_weight):
    profit = {"fix_profit": 0, "percent_profit": 0}
    if quote_type == "24HOURS":
        item_name = "24Hours"
    else:
        item_name = "48Hours"
    query_set = CustomProfitRate.objects.filter(volume_minimum__lt=calc_volume_weight,
                                                volume_maximum__gte=calc_volume_weight,
                                                item_name=item_name,
                                                )
    for record in query_set:
        profit["fix_profit"] = Decimal(record.fix_profit)
        profit["percent_profit"] = Decimal(record.percent_profit / 100)
    return profit


def CalcResult(volume, weight, zone_id, quote_type):
    result = {}
    # 计算体积重
    CalcVolumeWeight = get_calcVolumeWeight(quote_type, volume, weight)

    CalcVolumeWeight24 = get_calcVolumeWeight("24HOURS", volume, weight)

    # 查询该体积重的价格
    get_price_list = SeekPrice(quote_type, CalcVolumeWeight, zone_id)

    # 获取利润的方式
    Profit = get_custom_profit_rate(quote_type, CalcVolumeWeight)

    # Fuel Surcharge
    try:
        Fuel_Surcharge = 1 + Const.objects.all().filter(unit_item__iexact='FUEL')[0].unit_change
    except:
        Fuel_Surcharge = 1

    # 计算总价格
    cost_price = 0
    Delivery_Price = 0
    if get_price_list["BasePrice"] != 0 or get_price_list["PlusPrice"] != 0:
        plus_profit = 0
        if quote_type == "24HOURS":
            cost_price = (get_price_list["BasePrice"] + get_price_list["PlusPrice"] * (CalcVolumeWeight - 10)) \
                         * Fuel_Surcharge
            if Profit["fix_profit"] > 0:
                # Calculate as Fix Charges
                Delivery_Price = cost_price + Profit["fix_profit"] + plus_profit
            else:
                # Calculate as Percent
                Delivery_Price = cost_price * (1 + Profit["percent_profit"]) + plus_profit

        else:  # quote_type == "48HOURS"
            if CalcVolumeWeight > 10:
                cost_price = (get_price_list["BasePrice"] + get_price_list["PlusPrice"] * (CalcVolumeWeight - 10)) \
                             * Fuel_Surcharge
                plus_profit = Profit["fix_profit"] * (CalcVolumeWeight - 10)
            else:
                cost_price = (get_price_list["BasePrice"] + get_price_list["PlusPrice"]) * Fuel_Surcharge
            if Profit["fix_profit"] > 0:
                # Calculate as Fix Charges
                Delivery_Price = cost_price + Profit["fix_profit"] + plus_profit
            else:
                # Calculate as Percent
                Delivery_Price = cost_price * (1 + Profit["percent_profit"]) + plus_profit

    # 查询附加费
    Surcharge = surcharge_calculate(Delivery_Price, CalcVolumeWeight24)

    result["ServiceTimes"] = get_price_list["ServiceTimes"]
    result["CalcVolumeWeight"] = CalcVolumeWeight
    result["Delivery_Price"] = Delivery_Price
    result["cost_price"] = cost_price
    result["Airline_Handing_Fee"] = Surcharge["Airline_Handing_Fee"]
    result["Clearance_Fee"] = Surcharge["Clearance_Fee"]
    result["Agency_Fee"] = Surcharge["Agency_Fee"]
    result["COVID19_Fee"] = Surcharge["COVID19_Fee"]
    result["Total_amount"] = result["Delivery_Price"] + result["Airline_Handing_Fee"] + \
                             result["Clearance_Fee"] + result["Agency_Fee"] + result["COVID19_Fee"]
    result["Total_amount_cost"] = result["cost_price"] + result["Airline_Handing_Fee"] + \
                                  result["Clearance_Fee"] + result["COVID19_Fee"]

    return result


def SeekPrice(quote_type, calc_volume_weight, zone_id):
    """ 获取价格 基本价格 - 附加价格 - 服务时间 """
    price_list = {"BasePrice": 0, "PlusPrice": 0, "ServiceTimes": 0}
    calc_volume_weight = Decimal(calc_volume_weight)

    if quote_type == "24HOURS":
        query_set = Charge24.objects.filter(minimum__lte=calc_volume_weight,
                                            maximum__gte=calc_volume_weight,
                                            zone_id=zone_id)
        for record in query_set:
            price_list["BasePrice"] = record.basic_price
            price_list["PlusPrice"] = record.plus_price
            price_list["ServiceTimes"] = "24Hours"
    else:
        if calc_volume_weight > 10:
            query_set = Charge48.objects.filter(minimum__lt=calc_volume_weight,
                                                maximum__gte=calc_volume_weight,
                                                zone_id=zone_id,
                                                service__exact=quote_type,
                                                )

            for record in query_set:
                if record.basic_price >= price_list["BasePrice"]:
                    price_list["PlusPrice"] = record.plus_price
            calc_volume_weight = 10

        query_set = Charge48.objects.filter(minimum__lt=calc_volume_weight,
                                            maximum__gte=calc_volume_weight,
                                            service__exact=quote_type,
                                            zone_id=zone_id,
                                            )

        for record in query_set:
            if record.basic_price >= price_list["BasePrice"]:
                price_list["BasePrice"] = record.basic_price
                price_list["ServiceTimes"] = record.service

        if price_list["ServiceTimes"] == "24Hours":
            price_list["ServiceTimes"] = "48Hours"
        else:
            price_list["ServiceTimes"] = "72Hours"
    return price_list


def surcharge_calculate(delivery_price, calc_volume_weight):
    """ 获取附加费 """
    surcharge = {"Airline_Handing_Fee": 0, "Clearance_Fee": 0, "Agency_Fee": 0, "COVID19_Fee": 0}

    if delivery_price == 0:
        return surcharge

    # 代理费用
    if calc_volume_weight <= 1000:
        query_set = GeneralCharge.objects.filter(charge_item__exact="Agent Fee1")
    else:
        query_set = GeneralCharge.objects.filter(charge_item__exact="Agent Fee2")
    for record in query_set:
        surcharge["Agency_Fee"] = Decimal(record.price)

    # 航空处理费
    query_set = GeneralCharge.objects.filter(charge_item__exact="Airline Handing")
    if query_set:
        surcharge["Airline_Handing_Fee"] = Decimal(query_set[0].price * calc_volume_weight)
        minimum_charge = query_set[0].minimum_charge

        if surcharge["Airline_Handing_Fee"] < minimum_charge:  # 最少也要收取 40.00
            surcharge["Airline_Handing_Fee"] = minimum_charge

    # 清关费用
    query_set = GeneralCharge.objects.filter(charge_item__exact="Clearance")
    for record in query_set:
        surcharge["Clearance_Fee"] = Decimal(record.price)

    # 病毒处理费用
    query_set = GeneralCharge.objects.filter(charge_item__exact="Covid19 Fee")
    minimum_charge = query_set[0].minimum_charge
    for record in query_set:
        surcharge["COVID19_Fee"] = Decimal(record.price * calc_volume_weight)
    if surcharge["COVID19_Fee"] < minimum_charge:  # 最少也要收取8.00
        surcharge["COVID19_Fee"] = minimum_charge

    return surcharge


def digit_postcode(postcode):
    """返回 postcode 的最后的数字"""
    index = len(postcode) - 1
    digit_str = ""
    while index >= 0:
        if postcode[index].isdigit():
            digit_str = postcode[index] + digit_str
        if postcode[index].isalpha():
            break
        index = index - 1

    if digit_str == "":
        return 0
    return int(digit_str)


def string_postcode(postcode):
    """返回 postcode 的去掉最后的数字后，前面的字符串"""
    index = len(postcode) - 1
    while index >= 0:
        if postcode[index].isalpha():
            break
        index = index - 1

    str_postcode = postcode[0:index + 1]
    return str_postcode


def get_zone_id(quote_type, postcode):
    """
    获取 zonal 的 zone_id
    """
    zone_id = 0
    postcode_digit = digit_postcode(postcode)
    str_postcode = string_postcode(postcode)

    if quote_type == "24HOURS":
        queryset = Zone24Detail.objects.filter(begin__icontains=str_postcode, end__icontains=str_postcode)
    else:
        queryset = Zone48Detail.objects.filter(begin__icontains=str_postcode, end__icontains=str_postcode)
    for record in queryset:
        if digit_postcode(record.begin) <= postcode_digit <= digit_postcode(record.end):
            zone_id = record.zone_id
            break

    return zone_id


def general_surcharge():
    general_item = {"general_item": 0}
    query_set = GeneralCharge.objects.all()
    for record in query_set:
        if record.charge_item == "Airline Handing":
            general_item["AirlineHanding"] = "£" + '%.2f' % record.price
            general_item["AirlineHanding_minimum"] = "£" + '%.2f' % record.minimum_charge
        if record.charge_item == "Clearance":
            general_item["Clearance"] = "£" + '%.2f' % record.price
        if record.charge_item == "Agent Fee1":
            general_item["Agent_Fee1"] = "£" + '%.2f' % record.price
        if record.charge_item == "Agent Fee2":
            general_item["Agent_Fee2"] = "£" + '%.2f' % record.price
        if record.charge_item == "Covid19 Fee":
            general_item["Covid19_Fee"] = "£" + '%.2f' % record.price
            general_item["Covid19_Fee_minimum"] = "£" + '%.2f' % record.minimum_charge
        if record.charge_item == "Use of deferment":
            general_item["Use_of_deferment"] = "£" + '%.2f' % record.price
    return general_item


class AirFreightView(View):
    def get(self, request):
        general_charge = general_surcharge()
        return render(request, 'air_freight_result.html',
                      {'menu_active': MY_MENU_LOCAL,
                       'menu_grant': get_user_grant_list(request.user.id),
                       "Airline_Handing": general_charge["AirlineHanding"],
                       "AirlineHanding_minimum": general_charge["AirlineHanding_minimum"],
                       "Clearance": general_charge["Clearance"],
                       "Agent_Fee1": general_charge["Agent_Fee1"],
                       "Agent_Fee2": general_charge["Agent_Fee2"],
                       "Covid19_Fee": general_charge["Covid19_Fee"],
                       "Covid19_Fee_minimum": general_charge["Covid19_Fee_minimum"],
                       "Use_of_deferment": general_charge["Use_of_deferment"],
                       'zone_id': 0,
                       }, )

    def post(self, request):
        general_charge = general_surcharge()
        quote_type = request.POST.get("quote_type", "")
        volume = float(request.POST.get("volume", 0))
        weight = float(request.POST.get("weight", 0))
        uk_postcode = request.POST.get("postcode", "")

        postcode = (uk_postcode[:-3]).strip().upper()
        zone_id = get_zone_id(quote_type, postcode)
        if zone_id == 0:
            # 返回错误，邮编不存在
            return render(request, 'air_freight_result.html', {'menu_active': MY_MENU_LOCAL,
                                                               'menu_grant': get_user_grant_list(request.user.id),
                                                               'quote_type': quote_type,
                                                               'volume': volume,
                                                               'weight': weight,
                                                               'uk_postcode': uk_postcode.upper(),
                                                               'error': 'Postcode can not be found.',
                                                               'zone_id': 0,
                                                               })

        # 计算主程序
        result = CalcResult(volume, weight, zone_id, quote_type)

        # 设置返回值
        cost_price = '%.2f' % result['cost_price']
        Service_Time_Limit = result["ServiceTimes"]
        Counted_CBM = '%.2f' % result['CalcVolumeWeight'] + "CBM"
        Delivery_Price = "£" + '%.2f' % result['Delivery_Price']
        Airline_Handing_Fee = "£" + '%.2f' % result['Airline_Handing_Fee']
        Clearance_Fee = "£" + '%.2f' % result['Clearance_Fee']
        Agency_Fee = "£" + '%.2f' % result['Agency_Fee']
        COVID19_Fee = "£" + '%.2f' % result['COVID19_Fee']
        Total_amount = "£" + '%.2f' % result['Total_amount']
        Total_amount_cost = "£" + '%.2f' % result['Total_amount_cost']
        return render(request, 'air_freight_result.html', {'menu_active': MY_MENU_LOCAL,
                                                           'menu_grant': get_user_grant_list(request.user.id),
                                                           'quote_type': quote_type,
                                                           'volume': volume,
                                                           'weight': weight,
                                                           'uk_postcode': uk_postcode.upper(),
                                                           'Service_Time_Limit': Service_Time_Limit,
                                                           'Counted_CBM': Counted_CBM,
                                                           'Delivery_Price': Delivery_Price,
                                                           'Airline_Handing_Fee': Airline_Handing_Fee,
                                                           'Clearance_Fee': Clearance_Fee,
                                                           'Agency_Fee': Agency_Fee,
                                                           'COVID19_Fee': COVID19_Fee,
                                                           'Total_amount': Total_amount,
                                                           "Airline_Handing": general_charge["AirlineHanding"],
                                                           "AirlineHanding_minimum": general_charge[
                                                               "AirlineHanding_minimum"],
                                                           "Clearance": general_charge["Clearance"],
                                                           "Agent_Fee1": general_charge["Agent_Fee1"],
                                                           "Agent_Fee2": general_charge["Agent_Fee2"],
                                                           "Covid19_Fee": general_charge["Covid19_Fee"],
                                                           "Covid19_Fee_minimum": general_charge["Covid19_Fee_minimum"],
                                                           "Use_of_deferment": general_charge["Use_of_deferment"],
                                                           "zone_id": zone_id,
                                                           "cost_price": cost_price,
                                                           "Total_amount_cost": Total_amount_cost,
                                                           }, )
