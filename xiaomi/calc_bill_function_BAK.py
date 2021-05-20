#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   calc_bill_function.py    
@Contact :   thomaslzb@hotmail.com
@License :   (C)Copyright 2020-2022, Zibin Li

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
15/03/2021 12:16   lzb       1.0         None
"""

# 分离 postcode 字符及数字
import datetime
import decimal
import time

from django.db import transaction

from xiaomi.models import MiAccountBillDetailModel, CalculateItemModel, MiAccountBillMainModel, UpsBillDetailModel, \
    DPDBillDetailModel, DPDCongestionPostcodeModel, FuelSurchargeModel
from xiaomi.models import DcgBillDetailTotalModel, DcgBillModel, DcgBillDetailHandleModel
from xiaomi.models import DcgBillDetailUPSModel, DcgBillDetailDPDModel
from xiaomi.models import SpecialItemModel, PostcodeModel
from xiaomi.sql_const import MI_BILL_DPD_SQL, UPS_FILTER_ITEM_LIST, MI_BILL_UPS_SQL, DPD_DELIVERY_MAX_PRICE, \
    UPS_BILL_MI_SQL, UPS_RESIDENTIAL_FEE, DPD_VAT_RATE
from xiaomi.sql_const import DPD_STANDARD_ITEM, DPD_ADDITIONAL_ITEM


# 分离postcode 的字符串及数字
def return_char_number(input_string):
    input_list = list(input_string)
    max_len = len(input_string) - 1
    try:
        number = int(input_string[max_len])
    except:
        number = -1

    if number == -1:
        return input_string, 0
    number_str = ''
    for i in range(max_len):
        char = input_list[max_len - i]
        if char.isdigit():
            number_str = char + number_str
        else:
            break
    char_str = ''.join(input_list[:-len(number_str)])
    if number_str == '':
        number_int = 0
    else:
        number_int = int(number_str)
    return char_str, number_int


# 检查是否是偏远地区的邮编
def check_zone(postcode, zone_queryset):
    short_postcode = postcode[:-3].strip().upper()
    result = return_char_number(short_postcode)
    postcode_char_str = result[0]
    get_number = result[1]

    for record in zone_queryset:
        result = return_char_number(record.postcode_begin)
        char_str = result[0]
        begin_number = result[1]
        result = return_char_number(record.postcode_end)
        end_number = result[1]
        if begin_number <= get_number <= end_number and char_str == postcode_char_str:
            return True

    return False


# 判断是否是特殊的快递item
def is_special_item(special_item_queryset, goods_id):
    for record in special_item_queryset:
        if goods_id.find(record.item_code) != -1:
            return True
    return False


# 获取当前的燃油费率
def get_fuel_charge_rate(queryset, input_date, ):
    fuel_charge_rate = 0
    input_date = datetime.datetime.strftime(input_date, '%Y-%m-%d')
    for record in queryset:
        if datetime.datetime.strftime(record.begin_date, '%Y-%m-%d') <= \
                input_date <= datetime.datetime.strftime(record.end_date, '%Y-%m-%d'):
            fuel_charge_rate = record.fuel_surcharge
            break
    return fuel_charge_rate


# 计算 handle 的费用
def handle_fee(total_handle_dict, record, item_queryset, special_item_queryset):
    item_detail = {}
    for rec in item_queryset:
        if rec.item_desc.strip() != "":
            dict_desc = rec.item.strip() + ' - ' + rec.item_desc.strip()
        else:
            dict_desc = rec.item.strip()
        if rec.item == 'Package Fee':
            total_handle_dict[dict_desc][0] += 1
            total_handle_dict[dict_desc][1] += 1
            total_handle_dict[dict_desc][2] = rec.unit_price
            total_handle_dict[dict_desc][3] += rec.unit_price * 1  # 每一单收一次包装的费用
            total_handle_dict[dict_desc][4] = rec.order_by
            item_detail[dict_desc] = rec.unit_price

        if is_special_item(special_item_queryset, record.goods_id):
            if record.total_qty == 1 and rec.max_qty == 1 and rec.max_weight == 1 and rec.max_weight == 1:
                total_handle_dict[dict_desc][0] += 1
                total_handle_dict[dict_desc][1] += record.total_qty
                total_handle_dict[dict_desc][2] = rec.unit_price
                total_handle_dict[dict_desc][3] += rec.unit_price * record.total_qty
                total_handle_dict[dict_desc][4] = rec.order_by
                item_detail[dict_desc] = rec.unit_price
            else:
                if record.total_qty >= 2 and rec.max_qty == 2 and rec.max_weight == 2 and rec.max_weight == 2:
                    total_handle_dict[dict_desc][0] += 1
                    total_handle_dict[dict_desc][1] += record.total_qty
                    total_handle_dict[dict_desc][2] = rec.unit_price
                    total_handle_dict[dict_desc][3] += rec.unit_price * record.total_qty
                    total_handle_dict[dict_desc][4] = rec.order_by
                    item_detail[dict_desc] = rec.unit_price
        else:
            if rec.min_weight < record.weight <= rec.max_weight:
                if record.total_qty <= 3:
                    qty = record.total_qty
                else:
                    qty = 3
                if rec.item == 'Standard Handle Fee':
                    total_handle_dict[dict_desc][0] += 1
                    total_handle_dict[dict_desc][1] += qty
                    total_handle_dict[dict_desc][2] = rec.unit_price
                    total_handle_dict[dict_desc][3] += rec.unit_price * qty
                    total_handle_dict[dict_desc][4] = rec.order_by
                    item_detail[dict_desc] = rec.unit_price
                elif rec.item == 'Middle Products Handle Fee':
                    total_handle_dict[dict_desc][0] += 1
                    total_handle_dict[dict_desc][1] += qty
                    total_handle_dict[dict_desc][2] = rec.unit_price
                    total_handle_dict[dict_desc][3] += rec.unit_price * qty
                    total_handle_dict[dict_desc][4] = rec.order_by
                    item_detail[dict_desc] = rec.unit_price
                elif rec.item == 'Large products Handle Fee':
                    total_handle_dict[dict_desc][0] += 1
                    total_handle_dict[dict_desc][1] += qty
                    total_handle_dict[dict_desc][2] = rec.unit_price
                    total_handle_dict[dict_desc][3] += rec.unit_price * qty
                    total_handle_dict[dict_desc][4] = rec.order_by
                    item_detail[dict_desc] = rec.unit_price

        if rec.item == 'Extra Handle Fee From forth' and record.total_qty > 3:
            qty = record.total_qty - 3
            total_handle_dict[dict_desc][0] += 0
            total_handle_dict[dict_desc][1] += qty
            total_handle_dict[dict_desc][2] = rec.unit_price
            total_handle_dict[dict_desc][3] += rec.unit_price * qty
            total_handle_dict[dict_desc][4] = rec.order_by
            item_detail[dict_desc] = rec.unit_price

    return [total_handle_dict, item_detail]


# 计算 UPS delivery 的费用
def ups_delivery_fee(total_delivery, record, item_queryset, is_uk_zone2, fuel_charge_rate):
    # [0, 0, 0, 0]   record_num, qty, unit_price, amount
    item_detail = {}
    fee_desc = record.ups_fee_desc.strip()
    item_detail['delivery_cost'] = record.ups_fee_amount
    total_delivery['delivery_cost'][3] += record.ups_fee_amount

    fuel_charge_rate_percent = decimal.Decimal(1 + fuel_charge_rate / 100)
    if fee_desc in UPS_FILTER_ITEM_LIST:
        if fee_desc == '20.000 % Tax':
            item_detail['vat'] = record.ups_fee_amount
            total_delivery['vat'][3] += record.ups_fee_amount
        return total_delivery, item_detail
    if fee_desc == 'Dom. Standard':
        for rec in item_queryset:
            amount = round(rec.unit_price * fuel_charge_rate_percent, 2)
            if rec.zone:
                if is_uk_zone2:
                    if rec.min_weight < record.weight <= rec.max_weight and rec.zone == 'ZONE2':
                        dic_item = rec.item.strip() + ' - ' + rec.item_desc.strip()
                        total_delivery[dic_item][0] += 1
                        total_delivery[dic_item][1] += record.total_qty
                        total_delivery[dic_item][2] = rec.unit_price
                        total_delivery[dic_item][3] += amount
                        total_delivery[dic_item][4] = rec.order_by
                        item_detail[dic_item] = rec.unit_price
                else:
                    if rec.min_weight < record.weight <= rec.max_weight and rec.zone == 'ZONE1':
                        dic_item = rec.item.strip() + ' - ' + rec.item_desc.strip()
                        total_delivery[dic_item][0] += 1
                        total_delivery[dic_item][1] += record.total_qty
                        total_delivery[dic_item][2] = rec.unit_price
                        total_delivery[dic_item][3] += amount
                        total_delivery[dic_item][4] = rec.order_by
                        item_detail[dic_item] = rec.unit_price
    else:
        amount = record.ups_fee_amount * fuel_charge_rate_percent
        if fee_desc == 'Residential':
            total_delivery[fee_desc][0] += 1
            total_delivery[fee_desc][1] += record.total_qty
            total_delivery[fee_desc][2] = decimal.Decimal(UPS_RESIDENTIAL_FEE)
            total_delivery[fee_desc][3] += round(decimal.Decimal(UPS_RESIDENTIAL_FEE) * fuel_charge_rate_percent, 2)
            total_delivery[fee_desc][4] = 90
            item_detail[fee_desc] = decimal.Decimal(UPS_RESIDENTIAL_FEE)
        if fee_desc == 'Dom. Standard Undeliverable Return':
            total_delivery[fee_desc][0] += 1
            total_delivery[fee_desc][1] += record.total_qty
            total_delivery[fee_desc][2] = record.ups_fee_amount
            total_delivery[fee_desc][3] += amount
            total_delivery[fee_desc][4] = 91
            item_detail[fee_desc] = record.ups_fee_amount
        if fee_desc == 'Extended Area Surcharge-Destination':
            total_delivery[fee_desc][0] += 1
            total_delivery[fee_desc][1] += record.total_qty
            total_delivery[fee_desc][2] = record.ups_fee_amount
            total_delivery[fee_desc][3] += amount
            total_delivery[fee_desc][4] = 92
            item_detail[fee_desc] = record.ups_fee_amount
        if fee_desc == 'UK Border Fee':
            total_delivery[fee_desc][0] += 1
            total_delivery[fee_desc][1] += record.total_qty
            total_delivery[fee_desc][2] = record.ups_fee_amount
            total_delivery[fee_desc][3] += amount
            total_delivery[fee_desc][4] = 93
            item_detail[fee_desc] = record.ups_fee_amount
        if fee_desc == 'Additional Handling':
            total_delivery[fee_desc][0] += 1
            total_delivery[fee_desc][1] += record.total_qty
            total_delivery[fee_desc][2] = record.ups_fee_amount
            total_delivery[fee_desc][3] += amount
            total_delivery[fee_desc][4] = 94
            item_detail[fee_desc] = record.ups_fee_amount
        if fee_desc == 'Peak Surcharge- Additional Handling':
            total_delivery[fee_desc][0] += 1
            total_delivery[fee_desc][1] += record.total_qty
            total_delivery[fee_desc][2] = record.ups_fee_amount
            total_delivery[fee_desc][3] += amount
            total_delivery[fee_desc][4] = 95
            item_detail[fee_desc] = record.ups_fee_amount
        if fee_desc == 'Address Correction Dom. Standard':
            total_delivery[fee_desc][0] += 1
            total_delivery[fee_desc][1] += record.total_qty
            total_delivery[fee_desc][2] = record.ups_fee_amount
            total_delivery[fee_desc][3] += amount
            total_delivery[fee_desc][4] = 96
            item_detail[fee_desc] = record.ups_fee_amount
        if fee_desc == 'Dom. Standard Adjustment':
            fee_desc = 'Residential'
            total_delivery[fee_desc][0] += 1
            total_delivery[fee_desc][1] += record.total_qty
            total_delivery[fee_desc][2] = decimal.Decimal(UPS_RESIDENTIAL_FEE)
            total_delivery[fee_desc][3] += round(decimal.Decimal(UPS_RESIDENTIAL_FEE) * fuel_charge_rate_percent, 2)
            total_delivery[fee_desc][4] = 90
            item_detail[fee_desc] = decimal.Decimal(UPS_RESIDENTIAL_FEE)

    return [total_delivery, item_detail]


# 计算 DPD delivery 的费用
def dpd_delivery_fee(total_delivery, record, item_queryset, is_uk_zone2, is_dpd_congestion_zone,
                     congestion_fee, fuel_charge_rate):
    price = record.revenue / record.qty
    additional_fee = record.third_party_collection + record.fourth_party_collection + \
                     record.congestion + record.eu_clearance + record.return_charge + record.failed_collection + \
                     record.scottish_zone + record.tax_prepaid + record.handling + record.contractual_liability + \
                     record.oversize_exports + record.unsuccessful_eu_export + record.eu_export_return

    cost = record.revenue + record.fuel_surcharge + additional_fee

    vat_value = round(decimal.Decimal(cost * decimal.Decimal(DPD_VAT_RATE)), 2)
    item_detail = {'delivery_cost': cost, 'vat': vat_value}
    total_delivery['delivery_cost'][3] += cost

    total_delivery['vat'][3] += vat_value

    fuel_charge_rate_percent = 1 + fuel_charge_rate / 100
    compare_number = int(DPD_DELIVERY_MAX_PRICE - float(price))
    for rec in item_queryset:
        if compare_number >= 0:
            if not is_uk_zone2:
                if rec.zone == 'ZONE_UK':
                    total_delivery[DPD_STANDARD_ITEM][0] += 1
                    total_delivery[DPD_STANDARD_ITEM][1] += record.total_qty
                    total_delivery[DPD_STANDARD_ITEM][2] = rec.unit_price
                    total_delivery[DPD_STANDARD_ITEM][3] += rec.unit_price * fuel_charge_rate_percent
                    total_delivery[DPD_STANDARD_ITEM][4] = rec.order_by
                    item_detail[DPD_STANDARD_ITEM] = rec.unit_price
            else:
                if rec.zone == 'OFFSHORE':
                    total_delivery[DPD_STANDARD_ITEM][0] += 1
                    total_delivery[DPD_STANDARD_ITEM][1] += record.total_qty
                    total_delivery[DPD_STANDARD_ITEM][2] = rec.unit_price
                    total_delivery[DPD_STANDARD_ITEM][3] += rec.unit_price * fuel_charge_rate_percent
                    total_delivery[DPD_STANDARD_ITEM][4] = rec.order_by
                    item_detail[DPD_STANDARD_ITEM] = rec.unit_price
        else:
            if rec.item == DPD_ADDITIONAL_ITEM:
                total_delivery[DPD_STANDARD_ITEM][0] += 1
                total_delivery[DPD_STANDARD_ITEM][1] += record.total_qty
                total_delivery[DPD_STANDARD_ITEM][2] = (rec.unit_price + record.revenue) / record.total_qty
                total_delivery[DPD_STANDARD_ITEM][3] += (rec.unit_price + record.revenue) * fuel_charge_rate_percent
                total_delivery[DPD_STANDARD_ITEM][4] = rec.order_by
                item_detail[DPD_STANDARD_ITEM] = rec.unit_price + record.revenue

    if is_dpd_congestion_zone:
        additional_fee += congestion_fee
    if additional_fee != 0:
        if record.congestion > 0:  # 如果原来的账单有拥堵费的话，先减掉，以免重复计费
            additional_fee = additional_fee - record.congestion

        total_delivery[DPD_ADDITIONAL_ITEM][0] += 1
        total_delivery[DPD_ADDITIONAL_ITEM][1] += 0
        total_delivery[DPD_ADDITIONAL_ITEM][2] = 0
        total_delivery[DPD_ADDITIONAL_ITEM][3] += additional_fee * fuel_charge_rate_percent
        total_delivery[DPD_ADDITIONAL_ITEM][4] = 999
        item_detail[DPD_ADDITIONAL_ITEM] = additional_fee

    return [total_delivery, item_detail]


# 计算DCG账单的 订单处理费 Handle 详细
def calc_handle_bill(self, bill_year, bill_month, handle_detail_record):
    handle_recode_queryset = MiAccountBillDetailModel.objects.filter(bill_year=bill_year, bill_month=bill_month) \
        .order_by('bill_year', 'bill_month', 'mi_code')

    item_handle_queryset = CalculateItemModel.objects.filter(item_type__icontains='Handle')
    special_item_queryset = SpecialItemModel.objects.all()
    # 这个字典用于记录处理费用的情况
    total_handle_dict = {}
    for record in item_handle_queryset:
        # record_num, qty, unit_price, amount, order_by
        if record.item_desc.strip() != "":
            total_handle_dict[record.item.strip() + ' - ' + record.item_desc.strip()] = [0, 0, 0, 0, 0]
        else:
            total_handle_dict[record.item.strip()] = [0, 0, 0, 0, 0]

    for record in handle_recode_queryset:
        handleFee = 0
        extraFee = 0
        special_itemFee = 0
        packageFee = 0

        # 计算处理费用
        handle_dict = handle_fee(total_handle_dict, record, item_handle_queryset, special_item_queryset)
        total_handle_dict = handle_dict[0]
        item_detail = handle_dict[1]

        for key, value in item_detail.items():
            if key.find('Standard Handle Fee') >= 0:
                handleFee += value
            if key.find('Middle Products Handle Fee') >= 0:
                handleFee += value
            if key.find('Large products Handle Fee') >= 0:
                handleFee += value
            if key.find('Extra Handle Fee From forth') >= 0:
                extraFee += value
            if key.find('Handle Fee-Special Item') >= 0:
                special_itemFee += value
            if key.find('Handle Fee-Special Item') >= 0:
                special_itemFee += value
            if key.find('Package Fee') >= 0:
                packageFee += value

        total_amount = handleFee + extraFee + special_itemFee + packageFee
        handle_detail_record.append(DcgBillDetailHandleModel(bill_year=record.bill_year, bill_month=record.bill_month,
                                                             mi_code=record.mi_code,
                                                             package_code=record.package_code,
                                                             express_company=record.express_company,
                                                             parcel_id=record.parcel_id,
                                                             postcode=record.postcode,
                                                             ready_datetime=record.ready_datetime,
                                                             goods_id=record.goods_id,
                                                             total_qty=record.total_qty,
                                                             weight=record.weight,
                                                             handle_fee=handleFee,
                                                             extra_handle_fee=extraFee,
                                                             special_item_fee=special_itemFee,
                                                             package_fee=packageFee,
                                                             total_amount=total_amount,
                                                             ))

    # 计算完毕 end for

    insert_HandleBillDetailTotal = []
    handle_total_amount = 0

    # 插入处理费用的明细汇总
    for key, value in total_handle_dict.items():
        if value[3] > 0:
            handle_total_amount += value[3]
            insert_HandleBillDetailTotal.append(DcgBillDetailTotalModel(bill_year=bill_year, bill_month=bill_month,
                                                                        item_type='Handle', item=key,
                                                                        record_num=value[0],
                                                                        qty=value[1],
                                                                        display_order=value[4],
                                                                        express_company='DCG',
                                                                        op_datetime=datetime.datetime.now(),
                                                                        op_user_id=self.request.user.id,
                                                                        ))

    return [insert_HandleBillDetailTotal, handle_detail_record, '', handle_recode_queryset.count(), handle_total_amount]


# 计算DCG账单的快递公司的费用明细的列表
def update_insert_sql(self, insert_sql_list, record, express_company, calc, mi_code,
                      update_year, update_month, fuel_surcharge_rate):
    total_amount = 0
    nett_cost = 0
    total_vat = 0
    i = 0
    for value in calc:
        if i < 9:
            total_amount += value
        elif i == 9:  # cost
            nett_cost = value
        else:  # vat
            total_vat = value
        i += 1

    fuel_surcharge = round(total_amount * fuel_surcharge_rate / 100, 2)
    total_amount += fuel_surcharge
    if express_company == 'DPD':
        insert_sql_list.append(DcgBillDetailDPDModel(bill_year=record.bill_year,
                                                     bill_month=record.bill_month,
                                                     mi_code=mi_code,
                                                     package_code=record.package_code,
                                                     express_company=record.express_company,
                                                     parcel_id=record.parcel_id,
                                                     postcode=record.postcode,
                                                     ready_datetime=record.ready_datetime,
                                                     goods_id=record.goods_id,
                                                     total_qty=record.total_qty,
                                                     weight=record.weight,
                                                     standard_delivery_fee=calc[0],
                                                     additional_fee=calc[1],
                                                     fuel_surcharge_rate=fuel_surcharge_rate,
                                                     fuel_surcharge=fuel_surcharge,
                                                     total_vat=total_vat,
                                                     nett_cost=nett_cost,
                                                     total_cost=nett_cost + total_vat,
                                                     total_amount=total_amount,
                                                     total_profit=total_amount - nett_cost,
                                                     update_year=update_year,
                                                     update_month=update_month,
                                                     op_datetime=datetime.datetime.now(),
                                                     op_user_id=self.request.user.id,
                                                     ))
    if express_company == 'UPS':
        insert_sql_list.append(DcgBillDetailUPSModel(bill_year=record.bill_year,
                                                     bill_month=record.bill_month,
                                                     mi_code=mi_code,
                                                     package_code=record.package_code,
                                                     express_company=record.express_company,
                                                     parcel_id=record.parcel_id,
                                                     postcode=record.postcode,
                                                     ready_datetime=record.ready_datetime,
                                                     goods_id=record.goods_id,
                                                     total_qty=record.total_qty,
                                                     weight=record.weight,
                                                     standard_delivery_fee=calc[0],
                                                     residential=calc[2],
                                                     dom_standard_undeliverable_return=calc[3],
                                                     extended_area_surcharge_destination=calc[4],
                                                     uk_border_fee=calc[5],
                                                     additional_handling=calc[6],
                                                     peak_surcharge_additional_handling=calc[7],
                                                     address_correction_dom_standard=calc[8],
                                                     fuel_surcharge_rate=fuel_surcharge_rate,
                                                     fuel_surcharge=fuel_surcharge,
                                                     total_vat=total_vat,
                                                     nett_cost=nett_cost,
                                                     total_amount=total_amount,
                                                     total_cost=nett_cost + total_vat,
                                                     total_profit=total_amount - nett_cost,
                                                     update_year=update_year,
                                                     update_month=update_month,
                                                     op_datetime=datetime.datetime.now(),
                                                     op_user_id=self.request.user.id,
                                                     ))
    return insert_sql_list, total_amount, nett_cost, total_vat


# 根据账单计算快递费用的明细及成本
def calc_express_bill(self, bill_year, bill_month, express_company, recode_queryset, is_insert_fuel_record=True):
    # 获取需要计算item 的 queryset
    item_delivery_queryset = CalculateItemModel.objects.filter(item_type__icontains='Delivery',
                                                               express_company=express_company,
                                                               is_used=1,
                                                               )
    # 这个字典用于记录快递费用之和的情况
    total_delivery_dict = {}
    for record in item_delivery_queryset:
        # record_num, qty, unit_price, amount, order_by
        if record.item_desc.strip() != "":
            total_delivery_dict[record.item.strip() + ' - ' + record.item_desc.strip()] = [0, 0, 0, 0, 0]
        else:
            total_delivery_dict[record.item.strip()] = [0, 0, 0, 0, 0]

    total_delivery_dict['delivery_cost'] = [0, 0, 0, 0, 0]  # 记录快递成本之和
    total_delivery_dict['vat'] = [0, 0, 0, 0, 0]  # 记录快递成本之和

    # 获取 Fuel Charge Rate
    if bill_month == 1:
        seek_begin_year = bill_year - 1
        seek_begin_month = 12
        seek_end_year = bill_year
        seek_end_month = bill_month + 2
    elif bill_month == 12:
        seek_begin_year = bill_year
        seek_begin_month = bill_month - 1
        seek_end_year = bill_year + 1
        seek_end_month = 2
    elif bill_month == 11:
        seek_begin_year = bill_year
        seek_begin_month = bill_month - 1
        seek_end_year = bill_year + 1
        seek_end_month = 1
    else:
        seek_begin_year = bill_year
        seek_begin_month = bill_month - 1
        seek_end_year = bill_year
        seek_end_month = bill_month + 2
    seek_begin_date = datetime.datetime.strptime(str(seek_begin_year) + '/' + str(seek_begin_month) + '/01', '%Y/%m/%d')
    seek_end_date = datetime.datetime.strptime(str(seek_end_year) + '/' + str(seek_end_month) + '/01', '%Y/%m/%d')
    final_date = datetime.datetime.strptime('2030/12/31', '%Y/%m/%d')
    fuel_surcharge_queryset = FuelSurchargeModel.objects.filter(express_company=express_company,
                                                                begin_date__gte=seek_begin_date,
                                                                end_date__lte=seek_end_date,
                                                                range__exact='UK',
                                                                )
    fuel_surcharge_queryset = fuel_surcharge_queryset.union(
        FuelSurchargeModel.objects.filter(express_company=express_company,
                                          end_date=final_date,
                                          range__exact='UK', ))

    # 获取 express company 的 zone 范围
    zone_queryset = PostcodeModel.objects.filter(express_company=express_company, )

    dpd_congestion_zone_queryset = ''
    dpd_congestion_fee = 0
    if express_company == 'DPD':
        # 获取  DPD Congestion postcode 范围
        dpd_congestion_zone_queryset = DPDCongestionPostcodeModel.objects.filter(express_company=express_company, )
        for item in item_delivery_queryset:
            if item.item == 'Congestion Fee':
                dpd_congestion_fee = item.unit_price
                break

    this_month_delivery_list = []  # 本月的记录数量
    last_month_delivery_list = []  # 上月的记录数量

    express_bill_string = ""
    total_records_num = 0
    for_count = 0
    total_count = len(list(recode_queryset))

    express_detail_record = []
    current_mi_code = ""
    deliver_mi_code = ''
    fuel_charge_rate = 0
    standard_delivery_fee = 0
    additional_fee = 0
    residential = 0
    dom_standard_undeliverable_return = 0
    extended_area_surcharge_destination = 0
    uk_border_fee = 0
    additional_handling = 0
    peak_surcharge_additional_handling = 0
    address_correction_dom_standard = 0
    delivery_cost = 0
    delivery_vat = 0

    bill_total_amount = 0
    bill_total_cost = 0
    bill_total_vat = 0

    last_recode = ''

    is_uk_zone2 = False
    is_dpd_congestion_zone = False
    first_entry = True

    for record in recode_queryset:
        for_count += 1
        if first_entry:
            deliver_mi_code = record.mi_code
            last_recode = record
            is_uk_zone2 = check_zone(record.postcode, zone_queryset)
            first_entry = False
            fuel_charge_rate = get_fuel_charge_rate(fuel_surcharge_queryset, record.ready_datetime)

        if record.bill_no:  # 记录快递公司的账单号，查找到改 mi_code
            if express_bill_string.find(record.bill_no) == -1:
                express_bill_string += ''.join(record.bill_no) + '-'
        if current_mi_code != record.mi_code:
            is_uk_zone2 = check_zone(record.postcode, zone_queryset)
            if express_company == 'DPD':
                is_dpd_congestion_zone = check_zone(record.postcode, dpd_congestion_zone_queryset)
            total_records_num += 1
            if record.bill_year == bill_year and record.bill_month == bill_month:
                this_month_delivery_list.append(record.mi_code)
            else:
                last_month_delivery_list.append(record.mi_code)

            fuel_charge_rate = get_fuel_charge_rate(fuel_surcharge_queryset, record.ready_datetime)
            current_mi_code = record.mi_code

        # 计算快递费用费用
        result_list = []
        if express_company == 'UPS':
            result_list = ups_delivery_fee(total_delivery_dict, record, item_delivery_queryset,
                                           is_uk_zone2, fuel_charge_rate)
        if express_company == 'DPD':
            result_list = dpd_delivery_fee(total_delivery_dict, record, item_delivery_queryset,
                                           is_uk_zone2, is_dpd_congestion_zone, dpd_congestion_fee, fuel_charge_rate)

        if deliver_mi_code != record.mi_code and for_count <= total_count:  # 总结上一个 mi_code , 并初始化下一个
            calc = [standard_delivery_fee, additional_fee, residential, dom_standard_undeliverable_return,
                    extended_area_surcharge_destination, uk_border_fee, additional_handling,
                    peak_surcharge_additional_handling, address_correction_dom_standard, delivery_cost, delivery_vat]

            if express_company == 'UPS':
                fuel_charge_rate = get_fuel_charge_rate(fuel_surcharge_queryset, last_recode.ready_datetime)
                calc_result = update_insert_sql(self, express_detail_record, last_recode,
                                                'UPS', calc, deliver_mi_code, bill_year, bill_month,
                                                fuel_charge_rate, )
            else:  # express_company == 'DPD':
                calc_result = update_insert_sql(self, express_detail_record, last_recode,
                                                'DPD', calc, deliver_mi_code, bill_year, bill_month,
                                                fuel_charge_rate, )
            # 汇总计算结果
            express_detail_record = calc_result[0]
            bill_total_amount += calc_result[1]  # 汇总整个快递公司账单的总和
            bill_total_cost += calc_result[2]  # 汇总整个快递公司账单的净成本总和
            bill_total_vat += calc_result[3]  # 汇总整个快递公司账单的VAT总和

            # 初始化下一个 mi_code
            deliver_mi_code = record.mi_code
            last_recode = record

            standard_delivery_fee = 0
            additional_fee = 0
            residential = 0
            dom_standard_undeliverable_return = 0
            extended_area_surcharge_destination = 0
            uk_border_fee = 0
            additional_handling = 0
            peak_surcharge_additional_handling = 0
            address_correction_dom_standard = 0
            delivery_cost = 0
            delivery_vat = 0

        if result_list:
            total_delivery_dict = result_list[0]  # 记录总数
            item_detail = result_list[1]  # 记录单个mi-code的情况
            if express_company == 'UPS':
                for key, value in item_detail.items():
                    if key.find('Standard Delivery Fee') >= 0:
                        standard_delivery_fee += value
                    if key.find('Residential') >= 0:
                        residential += value
                    if key.find('Dom. Standard Undeliverable Return') >= 0:
                        dom_standard_undeliverable_return += value
                    if key.find('Extended Area Surcharge-Destination') >= 0:
                        extended_area_surcharge_destination += value
                    if key.find('UK Border Fee') >= 0:
                        uk_border_fee += value
                    if key.find('Additional Handling') >= 0:
                        additional_handling += value
                    if key.find('Peak Surcharge- Additional Handling') >= 0:
                        peak_surcharge_additional_handling += value
                    if key.find('Address Correction Dom. Standard') >= 0:
                        address_correction_dom_standard += value
                    if key.find('delivery_cost') >= 0:
                        delivery_cost += value
                    if key.find('vat') >= 0:
                        delivery_vat += value

            if express_company == 'DPD':
                for key, value in item_detail.items():
                    if key.find('Standard Delivery Fee') >= 0:
                        standard_delivery_fee += value
                    if key.find('Additional Fee') >= 0:
                        additional_fee += value
                    if key.find('delivery_cost') >= 0:
                        delivery_cost += value
                    if key.find('vat') >= 0:
                        delivery_vat += value

        if for_count == total_count and deliver_mi_code == record.mi_code:  # 处理最后一个 mi_code
            calc = [standard_delivery_fee, additional_fee, residential, additional_fee,
                    extended_area_surcharge_destination, extended_area_surcharge_destination, additional_handling,
                    peak_surcharge_additional_handling, address_correction_dom_standard, delivery_cost, delivery_vat]

            if express_company == 'UPS':
                fuel_charge_rate = get_fuel_charge_rate(fuel_surcharge_queryset, record.ready_datetime)
                calc_result = update_insert_sql(self, express_detail_record, record,
                                                'UPS', calc, record.mi_code, bill_year, bill_month,
                                                fuel_charge_rate)
            else:  # express_company == 'DPD':
                calc_result = update_insert_sql(self, express_detail_record, record,
                                                'DPD', calc, record.mi_code, bill_year, bill_month,
                                                fuel_charge_rate)
            express_detail_record = calc_result[0]
            bill_total_amount += calc_result[1]
            bill_total_cost += calc_result[2]
            bill_total_vat += calc_result[3]

    # 计算完毕 end for

    if express_bill_string:
        express_bill_string = express_bill_string[:-1]

    return [total_delivery_dict, express_detail_record, express_bill_string, this_month_delivery_list,
            last_month_delivery_list, bill_total_amount, bill_total_cost, bill_total_vat, ]


def calc_dcg_bill(self, bill_year, bill_month):
    # # 计算 DCG Bill - UPS 账单 (根据小米的账单，查询ups账单，计算出所有的快递费明细及成本)
    recode_queryset = MiAccountBillDetailModel.objects.raw(MI_BILL_UPS_SQL, [bill_year, bill_month])  # 获取结果集
    ups_bill_result_count = len(list(recode_queryset))
    if ups_bill_result_count > 0:  # 发现有ups的账单
        ups_bill = calc_express_bill(self, bill_year, bill_month, express_company='UPS',
                                     recode_queryset=recode_queryset, is_insert_fuel_record=True)

    else:
        ups_bill = [[], [], '', [], [], 0, 0, 0, ]

    ups_sub_total_record = ups_bill[0]
    ups_detail_record = ups_bill[1]
    ups_detail_list = (*ups_bill[3], *ups_bill[4])  # 将本月的mi_code 列表 和 上月的 mi_code 列表合并

    # 根据快递公司的账单来反向计算小米账单有的数据，快递费用的明细及成本
    recode_queryset = UpsBillDetailModel.objects.raw(UPS_BILL_MI_SQL,
                                                     [tuple(UPS_FILTER_ITEM_LIST),  # 排除不要处理的 如 Fuel 等费用
                                                      tuple(ups_detail_list),  # 排除这次已经处理过的记录
                                                      bill_year, bill_month])  # 获取结果集

    ups_mi_bill_result_count = len(list(recode_queryset))
    if ups_mi_bill_result_count > 0:
        ups_mi_bill = calc_express_bill(self, bill_year, bill_month, express_company='UPS',
                                        recode_queryset=recode_queryset, is_insert_fuel_record=False)
        ups_mi_sub_total_record = ups_mi_bill[0]
        ups_mi_detail_record = ups_mi_bill[1]
        ups_detail_record = [*ups_detail_record, *ups_mi_detail_record]
        ups_bill_result_count += ups_mi_bill_result_count

        # DCG-UK 合并两个 sub total
        if ups_sub_total_record:
            for key, value in ups_sub_total_record.items():
                for i in range(4):
                    ups_sub_total_record[key][i] += ups_mi_sub_total_record[key][i]
        else:
            ups_sub_total_record = ups_mi_sub_total_record
    else:
        ups_mi_bill = [[], [], '', [], [], 0, 0, 0, ]

    # # 计算 DCG-UK Bill -  DPD 账单(根据小米的账单，查询ups账单，计算出所有的快递费明细及成本)
    recode_queryset = MiAccountBillDetailModel.objects.raw(MI_BILL_DPD_SQL, [bill_year, bill_month])  # 获取结果集
    dpd_bill_result_count = len(list(recode_queryset))
    if dpd_bill_result_count > 0:
        dpd_bill = calc_express_bill(self, bill_year, bill_month, express_company='DPD',
                                     recode_queryset=recode_queryset, is_insert_fuel_record=True)
    else:
        dpd_bill = [[], [], '', [], [], 0, 0, ]

    dpd_sub_total_record = dpd_bill[0]
    dpd_detail_record = dpd_bill[1]

    # 计算  DCG-UK Bill - Handle 账单(根据小米的账单，计算出所有的处理费用的明细)
    handle_Bill = calc_handle_bill(self, bill_year, bill_month, handle_detail_record=[])
    handle_detail_record = handle_Bill[1]

    # 更新数据库
    is_save = True
    with transaction.atomic():
        if ups_bill_result_count > 0:
            # 创建 DCG-UK - UPS 的主账单
            total_amount = ups_bill[5] + ups_mi_bill[5]
            nett_cost = ups_bill[6] + ups_mi_bill[6]
            total_vat = ups_bill[7] + ups_mi_bill[7]
            total_record = len(ups_bill[3]) + len(ups_bill[4]) + len(ups_mi_bill[3]) + len(ups_mi_bill[4])
            total_cost = ups_bill[6] + ups_mi_bill[6] + ups_bill[7] + ups_mi_bill[7]
            total_profit = total_amount - nett_cost + total_vat
            DcgBillModel.objects.create(bill_year=bill_year, bill_month=bill_month,
                                        express_company='UPS',
                                        company_bill_list=ups_bill[2],
                                        this_month_record=len(ups_bill[3]) + len(ups_mi_bill[3]),
                                        last_month_record=len(ups_bill[4]) + len(ups_mi_bill[4]),
                                        total_record=total_record,
                                        total_amount=total_amount,
                                        nett_cost=nett_cost,
                                        total_vat=total_vat,
                                        total_cost=total_cost,
                                        total_profit=total_profit,
                                        op_datetime=datetime.datetime.now(),
                                        op_user_id=self.request.user.id,
                                        )

        if dpd_bill_result_count > 0:
            # 创建 DCG-UK - DPD 的主账单
            total_amount = dpd_bill[5]
            nett_cost = dpd_bill[6]
            total_vat = dpd_bill[7]
            total_record = len(dpd_bill[3]) + len(dpd_bill[4])
            total_cost = dpd_bill[6] + dpd_bill[7]
            total_profit = total_amount - nett_cost + total_vat
            DcgBillModel.objects.create(bill_year=bill_year, bill_month=bill_month,
                                        express_company='DPD',
                                        company_bill_list=dpd_bill[2],
                                        this_month_record=len(dpd_bill[3]),
                                        last_month_record=len(dpd_bill[4]),
                                        total_record=total_record,
                                        total_amount=total_amount,
                                        nett_cost=nett_cost,
                                        total_vat=total_vat,
                                        total_cost=total_cost,
                                        total_profit=total_profit,
                                        op_datetime=datetime.datetime.now(),
                                        op_user_id=self.request.user.id,
                                        )

        # 创建 DCG-UK - Handle 的主账单
        DcgBillModel.objects.create(bill_year=bill_year, bill_month=bill_month,
                                    express_company='DCG',
                                    company_bill_list='',
                                    last_month_record=0,
                                    this_month_record=handle_Bill[3],
                                    total_record=handle_Bill[3],
                                    total_amount=handle_Bill[4],
                                    total_cost=0,
                                    total_profit=handle_Bill[4],
                                    op_datetime=datetime.datetime.now(),
                                    op_user_id=self.request.user.id,
                                    )

        # 批量创建 DCG-UK - UPS 的账单汇总处理费的详情
        insert_UPSBillSubTotalDetail = []
        if ups_sub_total_record:
            for key, value in ups_sub_total_record.items():
                if value[1] > 0:
                    # sub totsl 明细汇总
                    insert_UPSBillSubTotalDetail.append(DcgBillDetailTotalModel(bill_year=bill_year,
                                                                                bill_month=bill_month,
                                                                                item_type='Delivery',
                                                                                item=key,
                                                                                record_num=value[0], qty=value[1],
                                                                                express_company='UPS',
                                                                                display_order=value[4],
                                                                                op_datetime=datetime.datetime.now(),
                                                                                op_user_id=self.request.user.id,
                                                                                ))
        # 批量创建 DCG-UK - DPD 的账单 sub 汇总处理费的详情
        insert_DPDBillSubTotalDetail = []
        if dpd_sub_total_record:
            for key, value in dpd_sub_total_record.items():
                if value[1] > 0:
                    # 主账单明细汇总
                    insert_DPDBillSubTotalDetail.append(DcgBillDetailTotalModel(bill_year=bill_year,
                                                                                bill_month=bill_month,
                                                                                item_type='Delivery',
                                                                                item=key,
                                                                                record_num=value[0], qty=value[1],
                                                                                express_company='DPD',
                                                                                display_order=value[4],
                                                                                op_datetime=datetime.datetime.now(),
                                                                                op_user_id=self.request.user.id,
                                                                                ))

        express_detail_list = (*insert_UPSBillSubTotalDetail, *insert_DPDBillSubTotalDetail)
        DcgBillDetailTotalModel.objects.bulk_create(express_detail_list)

        # 批量创建 DCG - Handle 的账单汇总处理费的详情
        DcgBillDetailTotalModel.objects.bulk_create(handle_Bill[0])

        # 批量创建 DCG 的账单 Handle 明细的详情
        DcgBillDetailHandleModel.objects.bulk_create(handle_detail_record)

        # 批量创建 DCG 的账单 UPS 明细的详情
        if ups_bill_result_count > 0:
            DcgBillDetailUPSModel.objects.bulk_create(ups_detail_record)

        if dpd_bill_result_count > 0:
            # 批量创建 DCG 的账单 DPD 明细的详情
            DcgBillDetailDPDModel.objects.bulk_create(dpd_detail_record)

        # 批量更新 小米主账单的 标志位  is_used
        MiAccountBillMainModel.objects.filter(bill_year=bill_year,
                                              bill_month=bill_month,
                                              is_used=0,
                                              ).update(is_used=1)

        mi_code_list = (*ups_bill[3], *ups_bill[4], *dpd_bill[3], *dpd_bill[4])
        # 批量更新 小米明细账单的 标志位  delivery_fee_checked
        MiAccountBillDetailModel.objects.filter(delivery_fee_checked=0,
                                                mi_code__in=mi_code_list,
                                                ).update(delivery_fee_checked=1,
                                                         update_bill_year=bill_year,
                                                         update_bill_month=bill_month, )

        # 批量更新 UPS 明细账单的 标志位 is_use
        UpsBillDetailModel.objects.filter(is_use=0, mi_code__in=mi_code_list,
                                          ).update(is_use=1,
                                                   used_bill_year=bill_year,
                                                   used_bill_month=bill_month, )

        # 批量更新 UPS 明细账单的 标志位 is_use
        DPDBillDetailModel.objects.filter(is_use=0, mi_code__in=mi_code_list,
                                          ).update(is_use=1,
                                                   used_bill_year=bill_year,
                                                   used_bill_month=bill_month, )
    return is_save
