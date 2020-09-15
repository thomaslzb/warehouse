#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   public_func.py    
@Contact :   thomaslzb@hotmail.com
@License :   (C)Copyright 2020-2022, Zibin Li

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
07/09/2020 14:39   lzb       1.0         None
"""
import re
import decimal
import math

from .models import ServiceType, ZoneDetail, ZoneName, Surcharge, ZoneSurcharge, EuroPrice, Company
from users.models import UserProfile


def is_can_take(server_company_id, server_type_name, length, weight, girth, zonal_name):
    """
    查询快递公司能够接受最大的尺寸或重量
    :param server_company_id: 快递公司
    :param server_type_name: 快递公司的服务类型
    :param length: 最大的长度
    :param weight: 最大的宽度
    :param girth: 最大的周长
    :param zonal_name: 邮编所属地
    :return: True or False
    """
    # server_type_name = Express24 and postcode = 'OTHER', return False
    if zonal_name == 'OTHERS' and server_type_name == 'EXPRESS24':
        return False

    server_queryset = ServiceType.objects.filter(name__exact=server_type_name, company__id__exact=server_company_id)
    if server_queryset:
        max_weight = server_queryset[0].max_weight
        max_length = server_queryset[0].max_length
        max_girth = server_queryset[0].max_girth
        if length <= max_length and weight <= max_weight and girth <= max_girth:
            return True

    return False


def get_zonal_name(server_company_id, postcode):
    """
    查询是否在当前的zone里面
    :param server_company_id: 快递公司
    :param postcode: 需要查询的邮编
    :return: '' 无此邮编， 有返回当前邮编的所在的区域名称
    """
    postcode = postcode[0:len(postcode) - 3]
    # 提取字符
    str_postcode = ''
    for code in postcode:
        if code.isalpha():
            str_postcode = str_postcode + code

        if code.isdigit():
            break
    num_postcode = ''
    for code in postcode:
        if code.isdigit():
            num_postcode = num_postcode + code

        if code.isalpha() and len(num_postcode) > 0:
            break

    num_postcode = int(num_postcode)

    zonal_queryset = ZoneDetail.objects.filter(company__id__exact=server_company_id, begin__startswith=str_postcode)
    zonal_name = ''
    if zonal_queryset:
        zonal_id = 0
        # 遍历数据库，找到需要的zonal_name
        for zonal in zonal_queryset:
            p_begin = zonal.begin
            # 提取字符
            str_p_begin = ''.join(re.split(r'[^A-Za-z]', p_begin))
            if str_postcode == str_p_begin:
                # 提取数字
                begin_num = int(re.sub("\D", "", p_begin))
                p_end = zonal.end
                end_num = int(re.sub("\D", "", p_end))
                if begin_num <= num_postcode <= end_num:
                    zonal_id = zonal.zone_id
                    break
        zonal_queryset = ZoneName.objects.filter(id__exact=zonal_id)
        if zonal_queryset:
            zonal_name = ZoneName.objects.filter(id__exact=zonal_id)[0].zone_name

    return zonal_name


def hermes_calculate(server_company_id, zonal_name, weight, qty, user_id):
    """
    计算HERMES, 运输总价格
    :param server_company_id: 快递公司
    :param zonal_name: zonal名称
    :param qty: 数量
    :param user_id: 用户id
    :return: 总价格

    """
    if weight > 2:
        server_type_name = 'UK-15KG'
    else:
        server_type_name = 'UK-2KG'

    base_price_queryset = ServiceType.objects.filter(name__exact=server_type_name,
                                                     company__id__exact=server_company_id)
    base_price = 0
    if base_price_queryset:
        if zonal_name == 'ZONEUK':
            base_price = base_price_queryset[0].base_price
        else:
            base_price_queryset = ZoneSurcharge.objects.filter(company__id__exact=server_company_id,
                                                               zone__zone_name__exact=zonal_name,
                                                               )
            if base_price_queryset:
                base_price = base_price_queryset[0].minimum_price

    # 利润率
    profit_margin = 0
    profit_margin_queryset = UserProfile.objects.filter(user_id__exact=int(user_id))
    if profit_margin_queryset:
        profit_margin = 1 + profit_margin_queryset[0].profit_percent / 100

    total_amount = base_price * qty * profit_margin

    return total_amount


def parcelforce_calculate(server_company_id, server_type_name, zonal_name, qty, length, width, user_id, is_uk):
    """
    计算PARCELFORCE, 运输总价格
    :param server_company_id: 快递公司
    :param server_type_name: 快递公司的服务类型
    :param zonal_name: zonal名称
    :param qty: 数量
    :param length: 长
    :param width: 宽
    :param user_id: 用户id
    :param is_uk: 是否英国境内
    :return: 总价格
    """
    total_amount = 0
    london_congestion = 0
    zonal_surcharges = 0
    oversize_charge_per_item = 0
    if is_uk:
        base_price_queryset = ServiceType.objects.filter(name__exact=server_type_name,
                                                         company__id__exact=server_company_id)
    else:
        base_price_queryset = EuroPrice.objects.filter(country__country__exact=zonal_name,
                                                       company__id__exact=server_company_id)
    ISLE_FEE = 0
    if base_price_queryset:
        if is_uk:
            base_price = base_price_queryset[0].base_price
            # 计算是否征收拥堵费
            if zonal_name == 'LONDOZONE':
                london_congestion_queryset = Surcharge.objects.filter(company__id__exact=server_company_id,
                                                                      surcharge_name__exact='CongestionFee')
                london_congestion = 0
                if london_congestion_queryset:
                    london_congestion = london_congestion_queryset[0].price
            else:
                # 征收区域的费用
                zonal_charge_queryset = ZoneSurcharge.objects.filter(company__id__exact=server_company_id,
                                                                     service_type__name__exact=server_type_name,
                                                                     zone__zone_name=zonal_name
                                                                     )
                if zonal_name == 'OTHERS' and server_type_name == 'EXPRESS48':
                    ISLE_FEE = 5
                else:
                    if zonal_charge_queryset:
                        minimum_charges = zonal_charge_queryset[0].minimum_price
                        zonal_percent = zonal_charge_queryset[0].percent
                        zonal_surcharges = minimum_charges
                        minimum_charges = base_price * qty * zonal_percent / 100
                        if minimum_charges > zonal_surcharges:
                            zonal_surcharges = minimum_charges

            # 计算是否征超过尺寸：
            # parcels with length between 1.1m – 1.5m or with the second largest dimension greater than0.7m
            # if Server type is Express48Large, OverSizeCharge = 0
            oversize_charge_per_item = 0
            if server_type_name != 'EXPRESS48LARGE':
                if 110 <= length <= 150 or width > 70:
                    oversize_queryset = Surcharge.objects.filter(company__id__exact=server_company_id,
                                                                 surcharge_name__exact='OverCharge')
                    if oversize_queryset:
                        oversize_charge_per_item = oversize_queryset[0].price

        else:
            base_price = base_price_queryset[0].basic_price

        # 燃油费
        fuel_charges_percent = 0
        fuel_charges_queryset = Surcharge.objects.filter(company__id__exact=server_company_id,
                                                         surcharge_name__exact='FuelSurcharge')
        if fuel_charges_queryset:
            fuel_charges_percent = 1 + fuel_charges_queryset[0].percent / 100

        # 利润率
        profit_margin = 0
        profit_margin_queryset = UserProfile.objects.filter(user_id__exact=int(user_id))
        if profit_margin_queryset:
            profit_margin = 1 + profit_margin_queryset[0].profit_percent / 100

        total_amount = ((base_price * qty + oversize_charge_per_item * qty) + zonal_surcharges + ISLE_FEE +
                        london_congestion) * fuel_charges_percent * profit_margin

    return total_amount


def dhl_calculate(server_company_id, zonal_name, qty, length, width, high, user_id, is_uk):
    """
    计算DHL, 运输总价格
    :param server_company_id: 快递公司
    :param zonal_name: zonal名称
    :param qty: 数量
    :param length: 长
    :param width: 宽
    :param high: 高
    :param user_id: 用户id
    :param is_uk: 是否英国境内
    :return: 总价格

    """
    total_amount = 0
    london_congestion = 0
    zonal_surcharges = 0
    oversize_charge_per_item = 0
    # 获取基本价格, DHL 是根据不同的zone得到不同的价格， 根据体积重，超出部分按照体积重再计算另外的附加费
    if is_uk:
        base_price_queryset = ZoneSurcharge.objects.filter(zone__zone_name__exact=zonal_name,
                                                           company__id__exact=server_company_id)

    else:
        base_price_queryset = EuroPrice.objects.filter(country__country__exact=zonal_name,
                                                       company__id__exact=server_company_id)

    if zonal_name == 'Republic of Ireland':  # 爱尔兰需要特别处理， 当做英国本土处理
        zonal_name = 'ZONEE'
        is_uk = True
        base_price_queryset = ZoneSurcharge.objects.filter(zone__zone_name__exact=zonal_name,
                                                           company__id__exact=server_company_id)

    if base_price_queryset:
        over_weight_price = 0
        oversize_price = 0
        over_weight = math.ceil((length * width * high)/4000)
        ISLE_FEE = 0
        BFPO_FEE = 0
        if is_uk:
            base_price = base_price_queryset[0].minimum_price
            if zonal_name == 'ISLE':   # ISLE 需要加上额外的快递费用
                ISLE_FEE = base_price_queryset[0].percent

            if zonal_name == 'BFPO':   # BFPO 需要加上额外的快递费用
                BFPO_FEE = base_price_queryset[0].percent

            oversize_standard_price = 3
            over_weight_standard = 20
            get_fuel_name = 'UK-FuelSurcharge'
            # UK 超重的单价
            plus_price = base_price_queryset[0].plus_price
        else:  # Euro
            base_price = base_price_queryset[0].basic_price
            oversize_standard_price = 10
            plus_price = decimal.Decimal('1.30')
            get_fuel_name = 'EURO-FuelSurcharge'
            over_weight_standard = 31
            # Euro 超重的单价
            plus_price = decimal.Decimal('1.30')

        if zonal_name == 'ZONEE':  # 爱尔兰需要特别处理
            get_fuel_name = 'EURO-FuelSurcharge'
            oversize_standard_price = 10
            over_weight_standard = 31
            # Euro 超重的单价
            plus_price = decimal.Decimal('1.30')

        # 计算是否征超过尺寸：
        # long length items have either: two sides of 80cm or more; a single side of 140cm or more
        if length > 140 or (length > 80 and width > 80):
            oversize_price = oversize_standard_price

        # EURO计算是否超重，超重则计算超重部分的费用
        if over_weight > over_weight_standard:
            over_weight_price = (over_weight - over_weight_standard) * plus_price


        # 燃油费
        fuel_charges_percent = 0
        fuel_charges_queryset = Surcharge.objects.filter(company__id__exact=server_company_id,
                                                         surcharge_name__exact=get_fuel_name)
        if fuel_charges_queryset:
            fuel_charges_percent = 1 + fuel_charges_queryset[0].percent / 100

        # 利润率
        profit_margin = 0
        profit_margin_queryset = UserProfile.objects.filter(user_id__exact=int(user_id))
        if profit_margin_queryset:
            profit_margin = 1 + profit_margin_queryset[0].profit_percent / 100

        total_amount = (((base_price + over_weight_price + oversize_price) * qty +
                         oversize_charge_per_item * qty) + zonal_surcharges + BFPO_FEE + ISLE_FEE +
                        london_congestion) * fuel_charges_percent * profit_margin

    return total_amount


def dpd_calculate(server_company_id, server_type_name,  zonal_name, qty, length, width, high, weight, user_id, is_uk):
    """
    计算DPD, 运输总价格
    :param server_company_id: 快递公司
    :param server_type_name: 快递公司服务类型
    :param zonal_name: zonal名称
    :param qty: 数量
    :param length: 长
    :param width: 宽
    :param high: 高
    :param weight: 重量
    :param user_id: 用户id
    :param is_uk: 是否英国境内
    :return: 总价格
    """
    total_amount = 0
    london_congestion = 0
    zonal_surcharges = 0
    oversize_charge_per_item = 0
    clearance_charge = 0
    if is_uk:
        base_price_queryset = ServiceType.objects.filter(name__exact=server_type_name,
                                                         company__id__exact=server_company_id)
    else:
        base_price_queryset = EuroPrice.objects.filter(country__country__exact=zonal_name,
                                                       company__id__exact=server_company_id)

    if base_price_queryset:
        if is_uk:
            base_price = base_price_queryset[0].base_price
            # 取得最少需要收费的价格
            min_charge_query = ZoneSurcharge.objects.filter(company__id__exact=server_company_id,
                                                            service_type__name=server_type_name,
                                                            zone__zone_name=zonal_name, )
            if min_charge_query:
                minimum_charge = min_charge_query[0].minimum_price
                if qty == 1:
                    base_price = minimum_charge

            # 计算是否征收拥堵费
            if zonal_name == 'ZONE1':
                london_congestion_queryset = Surcharge.objects.filter(company__id__exact=server_company_id,
                                                                      surcharge_name__exact='CongestionFee')
                london_congestion = 0
                if london_congestion_queryset:
                    london_congestion = london_congestion_queryset[0].price

            plus_price = 0
            get_fuel_name = 'UK-FuelSurcharge'

        else:
            base_price = base_price_queryset[0].basic_price
            plus_price = base_price_queryset[0].over_weight_price
            clearance_charge = base_price_queryset[0].clearance_charge
            get_fuel_name = 'EURO-FuelSurcharge'
            # 超过5kg，超出部分需要加收超重费
            if weight > 5:
                plus_price = (weight - 5) * plus_price

        # 计算是否征超过尺寸：Over Size Charge Per Item, any sides (Length > 100, Width>70, High>60) or Girth >230
        if length > 100 or width > 70 or high > 70 or (length + width + high) > 230:
            oversize_queryset = Surcharge.objects.filter(company__id__exact=server_company_id,
                                                         surcharge_name__exact='OverCharge')
            if oversize_queryset:
                oversize_charge_per_item = oversize_queryset[0].price

        # 燃油费
        fuel_charges_percent = 0
        fuel_charges_queryset = Surcharge.objects.filter(company__id__exact=server_company_id,
                                                         surcharge_name__exact=get_fuel_name)
        if fuel_charges_queryset:
            fuel_charges_percent = 1 + fuel_charges_queryset[0].percent / 100

        # 利润率
        profit_margin = 0
        profit_margin_queryset = UserProfile.objects.filter(user_id__exact=int(user_id))
        if profit_margin_queryset:
            profit_margin = 1 + profit_margin_queryset[0].profit_percent / 100

        total_amount = (((base_price + plus_price) * qty + oversize_charge_per_item * qty) + zonal_surcharges +
                        london_congestion + clearance_charge) * fuel_charges_percent * profit_margin

    return total_amount


def parcel(server_company_code, length, width, high, weight, postcode, qty, user_id, is_uk,):
    server_company_queryset = Company.objects.filter(code__exact=server_company_code)
    server_company_id = server_company_queryset[0].id
    company_name = server_company_queryset[0].name
    server_type_name = 'ALLSERVICE'
    service_type = ""
    unit_price = 0
    int_qty = int(qty)
    amount = 0

    if not server_company_queryset[0].is_use:  # 快递公司没有启用
        list_return = [company_name, service_type, unit_price, qty, amount, False]
        return list_return

    if server_company_code == 'DPD':  # DPD 周长的计算方法特别
        # Girth = length + width + depth
        girth = length + width + high
    else:
        # Girth = 1 x length + 2 x width + 2 x depth
        girth = length * 1 + width * 2 + high * 2

    if is_uk:
        zonal_name = get_zonal_name(server_company_id, postcode)
        if zonal_name == '':
            # 找不到此邮编
            if server_company_code == 'HERM' or server_company_code == 'DPD' or server_company_code == 'PASC':
                zonal_name = 'ZONEUK'
            else:
                if server_company_code == 'DHL':
                    zonal_name = 'ZONEA'
                else:
                    if server_company_code == 'PASC':
                        zonal_name = 'ZONE1'
                    else:
                        return [company_name, service_type, unit_price, qty, amount, False]
    else:
        zonal_name = postcode

    if is_can_take(server_company_id, server_type_name, length, weight, girth, zonal_name):
        list_return = [company_name, service_type, unit_price, qty, amount, False]
        if is_uk:  # UK local
            if server_company_code == 'HERM':
                amount = hermes_calculate(server_company_id, zonal_name, weight, int_qty, user_id)
                unit_price = amount / qty
                service_queryset = ServiceType.objects.filter(name__exact=server_type_name,
                                                              company__id__exact=server_company_id)
                if service_queryset:
                    service_type = service_queryset[0].description

                list_return = [company_name, service_type, unit_price, qty, amount, True]
                list_return[2] = format(list_return[2], '.2f')
                list_return[4] = format(list_return[4], '.2f')

            if server_company_code == 'PASC':
                l_express24 = [company_name, service_type, unit_price, qty, amount, False]
                # Express24
                server_type_name = 'EXPRESS24'
                if is_can_take(server_company_id, server_type_name, length, weight, girth, zonal_name):
                    amount = parcelforce_calculate(server_company_id, server_type_name, zonal_name,
                                                   int_qty, length, width, user_id, is_uk)
                    unit_price = amount / qty
                    service_queryset = ServiceType.objects.filter(name__exact=server_type_name,
                                                                  company__id__exact=server_company_id)
                    if service_queryset:
                        service_type = service_queryset[0].description
                    l_express24 = [company_name, service_type, unit_price, qty, amount, True]
                # Express48
                server_type_name = 'EXPRESS48'
                if is_can_take(server_company_id, server_type_name, length, weight, girth, zonal_name):
                    amount = parcelforce_calculate(server_company_id, server_type_name, zonal_name,
                                                   int_qty, length, width, user_id, is_uk)
                    unit_price = amount / qty
                    service_queryset = ServiceType.objects.filter(name__exact=server_type_name,
                                                                  company__id__exact=server_company_id)
                    if service_queryset:
                        service_type = service_queryset[0].description
                    l_express48 = [company_name, service_type, unit_price, qty, amount, True]
                # Express48Large
                server_type_name = 'EXPRESS48LARGE'
                if is_can_take(server_company_id, server_type_name, length, weight, girth, zonal_name):
                    amount = parcelforce_calculate(server_company_id, server_type_name, zonal_name,
                                                   int_qty, length, width, user_id, is_uk)
                    unit_price = amount / qty
                    service_queryset = ServiceType.objects.filter(name__exact=server_type_name,
                                                                  company__id__exact=server_company_id)
                    if service_queryset:
                        service_type = service_queryset[0].description
                    l_express48_large = [company_name, service_type, unit_price, qty, amount, True]

                if l_express24[4] != 0:
                    list_return = l_express24
                elif l_express48[4] != 0:
                    list_return = l_express48
                else:
                    list_return = l_express48_large

                if list_return[4] > l_express48[4]:
                    list_return = l_express48

                if list_return[4] > l_express48_large[4]:
                    list_return = l_express48_large

            if server_company_code == 'DHL':
                server_type_name = 'UK-DHL'
                amount = dhl_calculate(server_company_id, zonal_name,
                                       int_qty, length, width, high, user_id, is_uk)
                unit_price = amount / qty
                service_queryset = ServiceType.objects.filter(name__exact=server_type_name,
                                                              company__id__exact=server_company_id)
                if service_queryset:
                    service_type = service_queryset[0].description

            if server_company_code == 'DPD':
                if zonal_name == 'OFFSHORE':
                    server_type_name = 'OFFSHORE'
                else:
                    server_type_name = 'UK-Mainlands'

                amount = dpd_calculate(server_company_id, server_type_name, zonal_name,
                                       int_qty, length, width, high, weight, user_id, is_uk)
                unit_price = amount / qty
                service_queryset = ServiceType.objects.filter(name__exact=server_type_name,
                                                              company__id__exact=server_company_id)
                if service_queryset:
                    service_type = service_queryset[0].description

            if server_company_code == 'UPS':
                amount = 0  # ups_calculate(server_company_id, zonal_name, int_qty, length, width, high, user_id, is_uk)
                unit_price = amount / qty
                service_queryset = ServiceType.objects.filter(name__exact=server_type_name,
                                                              company__id__exact=server_company_id)
                if service_queryset:
                    service_type = service_queryset[0].description

            if server_company_code != 'PASC':
                list_return[4] = unit_price
                list_return[4] = amount
                is_amount = True
                if list_return[4] == 0:
                    is_amount = False
                list_return = [company_name, service_type, unit_price, qty, amount, is_amount]

            list_return[2] = decimal.Decimal(format(list_return[2], '.2f'))
            list_return[4] = decimal.Decimal(format(list_return[4], '.2f'))

        else:  # Euro
            server_type_name = 'EURO'
            if is_can_take(server_company_id, server_type_name, length, weight, girth, zonal_name):
                if server_company_code == 'PASC':
                    amount = parcelforce_calculate(server_company_id, server_type_name, zonal_name,
                                                   int_qty, length, width, user_id, is_uk)
                if server_company_code == 'DHL':
                    amount = dhl_calculate(server_company_id, zonal_name,
                                           int_qty, length, width, high, user_id, is_uk)

                if server_company_code == 'DPD':
                    amount = dpd_calculate(server_company_id, server_type_name, zonal_name,
                                           int_qty, length, width, high, weight, user_id, is_uk)

                unit_price = amount / qty
                service_queryset = ServiceType.objects.filter(name__exact=server_type_name,
                                                              company__id__exact=server_company_id)
                if service_queryset:
                    service_type = service_queryset[0].description

                is_amount = True
                if amount == 0:
                    is_amount = False

                list_return = [company_name, service_type, unit_price, qty, amount, is_amount]
                list_return[2] = decimal.Decimal(format(list_return[2], '.2f'))
                list_return[4] = decimal.Decimal(format(list_return[4], '.2f'))

        return list_return
    else:
        # can not be taken
        return [company_name, service_type, unit_price, qty, amount, False]
