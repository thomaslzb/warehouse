#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   calculation.py
@Contact :   thomaslzb@hotmail.com
@License :   (C)Copyright 2020-2022, Zibin Li

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
08/05/2021 10:39   lzb       1.0         None
"""
import datetime
import decimal
import math

from ocean.models import AmazonPriceModel, ExchangeModel, FbaItemPriceModel, CabinetItemPriceModel
from ocean.models import ContainModel, PrivateItemPriceModel, LondonPostcodeModel, PostcodePriceModel
from utils.tools import format_postcode


# 生成查询的编码
def get_quote_ref_no(request, code):
    quote_ref_no = code + str(request.user.id) + datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d%H%M%S%f")
    return quote_ref_no


# 根据重量，体积来计算出所有pallets  的数量
def get_pallets_qty(volume, weight):
    pallets_qty = int(math.ceil(volume / 1.5))  # 向上取整
    # 每个托盘按照1.5CBM得出的托盘数预估派送费
    # 如单派送地址货物总重量除以得出的托盘总数的平局每托盘重量超过500kg则需要用总重量除以500来计算托盘数来计算派送费
    average_weight = weight/pallets_qty
    if average_weight > 500:
        pallets_qty = int(math.ceil(weight/500))
    return pallets_qty


# 派送费用
def pallets_fee(warehouse, volume, weight):
    delivery_fee = 0
    pallets_qty = get_pallets_qty(volume, weight)

    whole_vehicle_qty = pallets_qty // 24    # 获取整车的数量
    pallets_qty = pallets_qty - whole_vehicle_qty * 24
    queryset = AmazonPriceModel.objects.filter(amazon__fba_code=warehouse)
    if queryset:
        pallets_amt = pallets_qty * queryset[0].pallet_price
        if pallets_amt > queryset[0].whole_price:
            pallets_amt = queryset[0].whole_price
        delivery_fee = pallets_amt + whole_vehicle_qty * queryset[0].whole_price

    return delivery_fee


# 海运散货FBA计算
def calc_bulk_fba(request, data):
    result_data = {}
    queryset = FbaItemPriceModel.objects.filter(fee_type=0)
    customs_clearance = extra_codes = tax_minimum = handling_fee = booking_fee = 0
    for record in queryset:
        if record.fee_code == 'CUSTO':  # 清关费用
            customs_clearance = record.rate
        if record.fee_code == 'EXTRA':  # HS CODE 品名费单价
            extra_codes = record.rate
        if record.fee_code == 'USEOF':  # 关税的最低费用
            tax_minimum = record.minimum_charge
        if record.fee_code == 'HANDL':  # 操作费用
            handling_fee = record.rate
        if record.fee_code == 'FBABO':  # FBA预约费用
            booking_fee = record.rate

    result_data['total_amount'] = 0
    # 获取清关费用
    result_data['customs_clearance'] = customs_clearance
    result_data['total_amount'] += result_data['customs_clearance']

    # 计算品名费用
    if data['hs_code_number'] > 3:
        result_data['extra_codes'] = (data['hs_code_number'] - 3) * extra_codes
    else:
        result_data['extra_codes'] = 0
    result_data['total_amount'] += result_data['extra_codes']

    # 最低税金
    result_data['tax'] = tax_minimum
    result_data['total_amount'] += result_data['tax']

    # 操作费
    if data['first_delivery'] == '1':
        result_data['handling_fee'] = handling_fee
    else:
        result_data['handling_fee'] = 0
    result_data['total_amount'] += result_data['handling_fee']

    # FBA 预约费用
    result_data['booking_fee'] = booking_fee * data['fba_number']
    result_data['total_amount'] += result_data['booking_fee']

    # 计算每个体积转换成为的托数， 如果托数大于24， 则算整车费用，余下的部分，按照托数再行计算
    warehouse_data = []
    for warehouse, volume, weight in data['warehouse_data']:
        pallet_fee = pallets_fee(warehouse, float(volume), float(weight))
        warehouse_data.append([warehouse, volume, weight, pallet_fee, ])
        result_data['total_amount'] += pallet_fee

    result_data['warehouse_data'] = warehouse_data

    # 获取汇率
    qs_exchange_rate = ExchangeModel.objects.first()
    result_data['exchange_rate'] = qs_exchange_rate.exchange_rate
    result_data['total_rmb'] = result_data['total_amount'] * result_data['exchange_rate']

    result_data['quote_ref_no'] = get_quote_ref_no(request, 'P')
    result_data['quote_time'] = datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d %H:%M:%S")

    return result_data


# 海运散货私人仓计算
def calc_private(request, forms):
    result_data = {'port': forms.data['port']}
    try:
        result_data['first_delivery'] = forms.data['first_delivery']
    except:
        result_data['first_delivery'] = '0'
    queryset = PrivateItemPriceModel.objects.filter(fee_type=0)
    customs_clearance = extra_codes = tax_minimum = handling_fee = congestion_fee = 0
    # 查询是否需要收取拥堵费
    is_charge_congestion = False
    result_data['postcode'] = format_postcode(forms.data['postcode'])
    postcode = result_data['postcode'][:-3].strip()
    queryset_london = LondonPostcodeModel.objects.filter(begin_code__lte=postcode, end_code__gte=postcode)
    if queryset_london:
        is_charge_congestion = True

    result_data['is_charge_congestion'] = is_charge_congestion

    for record in queryset:
        if record.fee_code == 'CUSTO':  # 清关费用
            customs_clearance = record.rate
        if record.fee_code == 'EXTRA':  # HS CODE 品名费单价
            extra_codes = record.rate
        if record.fee_code == 'USEOF':  # 关税的最低费用
            tax_minimum = record.minimum_charge
        if record.fee_code == 'HANDL':  # 操作费用
            handling_fee = record.rate
        if record.fee_code == 'LON' and is_charge_congestion:  # 伦敦拥堵费
            congestion_fee = record.rate

    result_data['total_amount'] = 0
    # 获取清关费用
    result_data['customs_clearance'] = customs_clearance
    result_data['total_amount'] += result_data['customs_clearance']

    # 计算品名费用
    result_data['hs_code_number'] = forms.data['hs_code_number']
    hs_code_number = int(result_data['hs_code_number'])
    if hs_code_number > 3:
        result_data['extra_codes'] = (hs_code_number - 3) * extra_codes
    else:
        result_data['extra_codes'] = 0
    result_data['total_amount'] += result_data['extra_codes']

    # 最低税金
    result_data['tax'] = tax_minimum
    result_data['total_amount'] += result_data['tax']

    # 操作费
    if result_data['first_delivery'] == '1':
        result_data['handling_fee'] = handling_fee
    else:
        result_data['handling_fee'] = 0
    result_data['total_amount'] += result_data['handling_fee']

    # 伦敦拥堵费
    result_data['congestion_fee'] = congestion_fee
    result_data['total_amount'] += result_data['congestion_fee']

    # 计算每个体积重， 体积重的比例是1:500， 取相对应重的那个数据
    # 获取体积重
    result_data['weight'] = float(forms.data['weight'])
    volume_weight = int(math.ceil(result_data['weight'] / 500))  # 向上取整
    result_data['volume'] = float(forms.data['volume'])
    if result_data['volume'] > volume_weight:
        volume_weight = int(result_data['volume'])

    queryset = PostcodePriceModel.objects.filter(postcodemodel__begin_code__lte=postcode,
                                                 postcodemodel__end_code__gte=postcode,
                                                 )
    result_data['delivery_amt'] = 0
    if queryset:
        result_data['delivery_amt'] = volume_weight * queryset[0].price
    result_data['total_amount'] += result_data['delivery_amt']

    # 获取汇率
    qs_exchange_rate = ExchangeModel.objects.first()
    result_data['exchange_rate'] = qs_exchange_rate.exchange_rate
    result_data['total_rmb'] = result_data['total_amount'] * result_data['exchange_rate']

    result_data['quote_ref_no'] = get_quote_ref_no(request, 'P')
    result_data['quote_time'] = datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d %H:%M:%S")

    return result_data


# 判断输入的海运整柜是否有错误
def judge_cabinet_input(request, cabinet_forms):
    error_msg = ''
    containers_data = []
    containers_code_list = []
    for i in range(4):
        container_warehouses = []
        code = 'container' + str(i) + '_code'
        qty = 'container' + str(i) + '_qty'
        volume = 'container' + str(i) + '_volume'
        weight = 'container' + str(i) + '_weight'
        boxes = 'container' + str(i) + '_boxes'
        container_code = request.POST.get(code, 'NO-DATA')
        container_qty = request.POST.get(qty, '')
        container_volume = request.POST.get(volume, '')
        container_weight = request.POST.get(weight, '')
        container_boxes = request.POST.get(boxes, '')
        if container_code != 'NO-DATA':
            containers_code_list.append(container_code)
            # 收集该集装箱下面的所有仓库
            for k in range(5):
                wh_code = 'container' + str(i) + '_fba_code' + str(k) + '_amsify'
                wh_volume = 'container' + str(i) + '_volume' + str(k)
                wh_weight = 'container' + str(i) + '_weight' + str(k)
                warehouse_code = request.POST.get(wh_code, '')
                warehouse_volume = request.POST.get(wh_volume, '')
                warehouse_weight = request.POST.get(wh_weight, '')
                if warehouse_code != '' or k == 0:
                    if warehouse_volume == '':
                        warehouse_volume = 0
                    else:
                        warehouse_volume = decimal.Decimal(warehouse_volume)
                    if warehouse_weight == '':
                        warehouse_weight = 0
                    else:
                        warehouse_weight = decimal.Decimal(warehouse_weight)
                    container_warehouses.append([warehouse_code, warehouse_volume, warehouse_weight, ])
                else:
                    if warehouse_volume != '' and warehouse_weight != '':
                        container_warehouses.append([warehouse_code, warehouse_volume, warehouse_weight, ])

            if container_qty == '':
                container_qty = 0
            else:
                container_qty = int(container_qty)
            if container_volume == '':
                container_volume = 0
            else:
                container_volume = decimal.Decimal(container_volume)
            if container_weight == '':
                container_weight = 0
            else:
                container_weight = decimal.Decimal(container_weight)
            if container_boxes == '':
                container_boxes = 0
            else:
                container_boxes = int(container_boxes)
            containers_data.append([container_code,
                                    container_qty,
                                    container_volume,
                                    container_weight,
                                    container_boxes,
                                    container_warehouses])

    # 判断集装箱类型是否重复
    if len(containers_code_list) != len(set(containers_code_list)):
        error_msg = '错误提示：同一集装箱柜型只能输入一次， 请检查数据'

    # 判断集装箱内的数据是全部填写正确
    for container in containers_data:
        if container[1] == 0 or container[2] == 0 or container[3] == 0 or container[4] == 0:
            error_msg = '输入集装箱的数据必须大于零'
            break
        # 检查该集装箱下面的仓库是否输入正确
        warehouse_code_list = []

        # 获取该集装箱的最大体积数
        queryset_contain_type = ContainModel.objects.filter(code__exact=container[0])
        max_volume = queryset_contain_type[0].max_volume
        container_name = queryset_contain_type[0].name

        # 判断集装箱输入的体积数，是否大于该类型集装箱的最大容积
        if container[2] > max_volume * container[1]:
            error_msg = '必须输入集装箱的体积数 ' + str(container[2]) + ' 超过了，  集装箱最大容量为 ' \
                        + str(max_volume) + ' 立方米（' + container_name + '）， 请查证。'
            break

        this_warehouse = container[5]
        this_warehouse_total_volume = 0
        this_warehouse_total_weight = 0
        for warehouse in this_warehouse:
            if warehouse[0] == "" or warehouse[1] <= 0:
                error_msg = '集装箱' + container_name + '内, 请选择需要派送的仓库代码'
                break
            warehouse_code_list.append(warehouse[0])
            this_warehouse_total_volume += decimal.Decimal(warehouse[1])
            this_warehouse_total_weight += decimal.Decimal(warehouse[2])

        if error_msg:
            break
        else:
            # 判断某个集装箱内的仓库是否重复
            if len(warehouse_code_list) != len(set(warehouse_code_list)):
                error_msg = '错误提示：同一集装箱 ' + container_name + ' 类型内部的派送仓库代码不能重复，请查证'
                break
            else:
                # 判断某个集装箱内的体积总数是否超过该集装箱的最大体积数
                if this_warehouse_total_volume != container[2]*container[1]:
                    error_msg = '错误提示：派送仓库输入的体积数之和必须等于集装箱输入的体积数 ' \
                                + str(container[2]*container[1]) + ' 立方米(' + container_name + ')  请查证'
                    break
                else:
                    if this_warehouse_total_weight != container[3]:
                        error_msg = '错误提示：派送仓库输入的重量之和必须等于集装箱 输入的重量 ' \
                                    + str(container[3]) + ' 公斤(' + container_name + ')， 请查证'
                        break

    return containers_data, error_msg


# 计算海运整柜
def calc_cabinet(request, data):
    tax_minimum_unit = extra_codes_unit = customs_clearance_unit = ''
    tax_minimum_price = extra_codes_price = customs_clearance_price = 0
    doc_fee_unit = lift_fee_unit = equipment_fee_unit = port_fee_unit = thc_fee_unit = ''
    port_congestion_fee_unit = shunt_fee_unit = pack_fee_unit = ''
    thc_fee_price = doc_fee_price = lift_fee_price = 0
    equipment_fee_price = port_fee_price = port_congestion_fee_price = shunt_fee_price = pack_fee_price = 0
    unloading_unit = unloading700_price = unloading1000_price = unloading1000_plus_price = 0
    result_data = {}
    queryset = CabinetItemPriceModel.objects.filter(fee_type=0)

    for record in queryset:
        if record.fee_code == 'CUSTO':  # 清关费用
            customs_clearance_unit = record.unit
            customs_clearance_price = record.rate
        if record.fee_code == 'EXTRA':  # HS CODE 品名费单价
            extra_codes_unit = record.unit
            extra_codes_price = record.rate
        if record.fee_code == 'USEOF':  # 关税的最低费用
            tax_minimum_unit = record.unit
            tax_minimum_price = record.minimum_charge
        if record.fee_code == 'THC':  # 码头费
            thc_fee_unit = record.unit
            thc_fee_price = record.rate
        if record.fee_code == 'DOC':  # 文件费
            doc_fee_unit = record.unit
            doc_fee_price = record.rate
        if record.fee_code == 'LIFT':  # 吊柜费
            lift_fee_unit = record.unit
            lift_fee_price = record.rate
        if record.fee_code == 'EQUIP':  # 设备费
            equipment_fee_unit = record.unit
            equipment_fee_price = record.rate
        if record.fee_code == 'PORTC':  # 码头杂费
            port_fee_unit = record.unit
            port_fee_price = record.rate
        if record.fee_code == 'PCONG':  # 码头拥堵费
            port_congestion_fee_unit = record.unit
            port_congestion_fee_price = record.rate
        if record.fee_code == 'SHUNT':  # 提货费
            shunt_fee_unit = record.unit
            shunt_fee_price = record.rate
        if record.fee_code == 'PACK':  # 打包缠膜费
            pack_fee_unit = record.unit
            pack_fee_price = record.rate
        if record.fee_code == 'U700':  # 卸货费 箱数小于等于700
            unloading_unit = record.unit
            unloading700_price = record.rate
        if record.fee_code == 'U1000':  # 卸货费 箱数大于700小于等于1000
            unloading1000_price = record.rate
        if record.fee_code == 'U1001':  # 卸货费 箱数大于1000
            unloading1000_plus_price = record.rate

    # 获取柜量的总计
    containers = []
    warehouses = []
    total_qty = total_volume = total_weight = total_boxes = 0
    for item in data['cabinet_data']:
        total_qty += item[1]
        total_volume += item[2]
        total_weight += item[3]
        total_boxes += item[4]
        containers.append([item[0], item[1], item[2], item[3], item[4], ])
        for warehouse in item[5]:
            warehouses.append(warehouse)

    # 获取 container qty 的总计
    result_data['total_qty'] = total_qty

    # 获取 pallets 的总计
    result_data['total_pallets'] = get_pallets_qty(float(total_volume), float(total_weight))

    # 获取箱数的总计
    result_data['total_boxes'] = total_boxes

    result_data['total_amount'] = 0

    # 获取清关费用
    result_data['customs_clearance_unit'] = customs_clearance_unit
    result_data['customs_clearance_price'] = customs_clearance_price
    result_data['customs_clearance'] = customs_clearance_price
    result_data['total_amount'] += result_data['customs_clearance']

    # 计算品名费用
    if data['hs_code_number'] > 3:
        result_data['extra_codes'] = (data['hs_code_number'] - 3) * extra_codes_price
    else:
        result_data['extra_codes'] = 0
    result_data['extra_codes_unit'] = extra_codes_unit
    result_data['extra_codes_price'] = extra_codes_price
    result_data['total_amount'] += result_data['extra_codes']

    # 最低税金
    result_data['tax_unit'] = tax_minimum_unit
    result_data['tax_price'] = tax_minimum_price
    result_data['tax'] = tax_minimum_price
    result_data['total_amount'] += result_data['tax']

    # 码头费
    result_data['thc_fee_unit'] = thc_fee_unit
    result_data['thc_fee_price'] = thc_fee_price
    result_data['thc_fee'] = thc_fee_price * total_qty
    result_data['total_amount'] += result_data['thc_fee']

    # 文件费
    result_data['doc_fee_unit'] = doc_fee_unit
    result_data['doc_fee_price'] = doc_fee_price
    result_data['doc_fee'] = doc_fee_price * total_qty
    result_data['total_amount'] += result_data['doc_fee']
    # 吊柜费
    result_data['lift_fee_unit'] = lift_fee_unit
    result_data['lift_fee_price'] = lift_fee_price
    result_data['lift_fee'] = lift_fee_price * total_qty
    result_data['total_amount'] += result_data['lift_fee']
    # 设备费
    result_data['equipment_fee_unit'] = equipment_fee_unit
    result_data['equipment_fee_price'] = equipment_fee_price
    result_data['equipment_fee'] = equipment_fee_price * total_qty
    result_data['total_amount'] += result_data['equipment_fee']
    # 码头杂费
    result_data['port_fee_unit'] = port_fee_unit
    result_data['port_fee_price'] = port_fee_price
    result_data['port_fee'] = port_fee_price * total_qty
    result_data['total_amount'] += result_data['port_fee']
    # 码头拥堵费
    result_data['port_congestion_fee_unit'] = port_congestion_fee_unit
    result_data['port_congestion_fee_price'] = port_congestion_fee_price
    result_data['port_congestion_fee'] = port_congestion_fee_price * total_qty
    result_data['total_amount'] += result_data['port_congestion_fee']
    # 提货费
    result_data['shunt_fee_unit'] = shunt_fee_unit
    result_data['shunt_fee_price'] = shunt_fee_price
    result_data['shunt_fee'] = shunt_fee_price * total_qty
    result_data['total_amount'] += result_data['shunt_fee']

    # 计算卸货费
    total_loading_fee = 0
    for container in containers:
        sub_qty = container[1]
        sub_boxes = container[4]
        unloading_plus_fee = 0
        if sub_boxes <= 700:
            unloading_price = unloading700_price
        elif sub_boxes <= 1000:
            unloading_price = unloading1000_price
        else:
            unloading_price = unloading1000_price
            unloading_plus_fee = (sub_boxes - 1000) * unloading1000_plus_price
        total_loading_fee += unloading_price * sub_qty + unloading_plus_fee

    result_data['unloading_fee_unit'] = unloading_unit
    result_data['unloading_fee_price'] = ''
    result_data['unloading_fee'] = total_loading_fee
    result_data['total_amount'] += result_data['unloading_fee']

    # 合并所有重复仓库的体积及重量
    new_warehouses = []
    for key, volume, weight in warehouses:
        is_new = True
        i = 0
        for new_key, new_volume, new_weight in new_warehouses:
            if key == new_key:
                is_new = False
                new_warehouses[i][1] += volume
                new_warehouses[i][2] += weight
                break
            i += 1
        if is_new:
            new_warehouses.append([key, volume, weight])

    # 打包缠膜费(应该根据派送不同仓点，计算不同的托数来计算打包费用)
    result_data['pack_unit'] = pack_fee_unit
    result_data['pack_price'] = pack_fee_price
    result_data['pack_fee'] = 0

    # 计算每个仓库的派送费
    warehouse_data = []
    for warehouse, volume, weight in new_warehouses:
        pallet_fee = pallets_fee(warehouse, float(volume), float(weight))
        warehouse_data.append([warehouse, volume, weight, pallet_fee, ])

        # 打包缠膜费(应该根据派送不同仓点，计算不同的托数来计算打包费用)
        result_data['pack_fee'] += pack_fee_price * get_pallets_qty(float(volume), float(weight))
        # 汇总总金额
        result_data['total_amount'] += pallet_fee

    # 将打包缠膜费加入到汇总金额中
    result_data['total_amount'] += result_data['pack_fee']

    result_data['warehouse_data'] = warehouse_data

    # 获取汇率
    qs_exchange_rate = ExchangeModel.objects.first()
    result_data['exchange_rate'] = qs_exchange_rate.exchange_rate
    result_data['total_rmb'] = result_data['total_amount'] * result_data['exchange_rate']

    result_data['quote_ref_no'] = get_quote_ref_no(request, 'P')
    result_data['quote_time'] = datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d %H:%M:%S")

    return result_data
