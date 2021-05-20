#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   sql_const.py    
@Contact :   thomaslzb@hotmail.com
@License :   (C)Copyright 2020-2022, Zibin Li

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
09/03/2021 09:07   lzb       1.0         None
"""


UPS_FILTER_ITEM_LIST = ['Fuel Surcharge', '20.000 % Tax', ]

MI_BILL_UPS_SQL = "SELECT x_mi_bill_detail.id, " \
                   "x_mi_bill_detail.bill_year, " \
                   "x_mi_bill_detail.bill_month, " \
                   "x_mi_bill_detail.mi_code, " \
                   "x_mi_bill_detail.weight, " \
                   "x_mi_bill_detail.total_qty, " \
                   "x_mi_bill_detail.goods_id, " \
                   "x_mi_bill_detail.postcode, " \
                   "x_ups_bill_detail.parcel_id as parcel_id, " \
                   "x_ups_bill_detail.fee_code as ups_fee_code, " \
                   "x_ups_bill_detail.fee_desc as ups_fee_desc, " \
                   "x_ups_bill_detail.ups_bill_no as bill_no, " \
                   "x_mi_bill_detail.express_company, " \
                   "x_ups_bill_detail.fee_amount as ups_fee_amount " \
                   "FROM x_mi_bill_detail " \
                   "JOIN x_ups_bill_detail ON x_ups_bill_detail.mi_code = x_mi_bill_detail.mi_code " \
                   "WHERE x_mi_bill_detail.delivery_fee_checked = 0 " \
                   "and x_mi_bill_detail.bill_year <= %s " \
                   "and x_mi_bill_detail.bill_month <= %s " \
                   "and x_mi_bill_detail.express_company = 'UPS' " \
                   "ORDER BY x_ups_bill_detail.mi_code, " \
                   "x_mi_bill_detail.bill_year, " \
                   "x_mi_bill_detail.bill_month "

UPS_RESIDENTIAL_FEE = 2.40

DPD_DELIVERY_MAX_PRICE = 12.36
DPD_VAT_RATE = 0.20   # DPD 的增值费率 20%
DPD_STANDARD_ITEM = 'Standard Delivery Fee'
DPD_ADDITIONAL_ITEM = 'Additional Fee'

MI_BILL_DPD_SQL = "SELECT x_mi_bill_detail.id, " \
                   "x_mi_bill_detail.bill_year, " \
                   "x_mi_bill_detail.bill_month, " \
                   "x_mi_bill_detail.mi_code, " \
                   "x_mi_bill_detail.weight, " \
                   "x_mi_bill_detail.total_qty, " \
                   "x_mi_bill_detail.goods_id, " \
                   "x_mi_bill_detail.postcode, " \
                   "x_dpd_bill_detail.parcel_id as parcel_id," \
                   "x_dpd_bill_detail.dpd_invoice_no as bill_no," \
                   "x_dpd_bill_detail.qty, " \
                   "x_dpd_bill_detail.revenue, " \
                  "x_dpd_bill_detail.fuel_surcharge, " \
                   "x_dpd_bill_detail.third_party_collection, " \
                   "x_dpd_bill_detail.fourth_party_collection, " \
                   "x_dpd_bill_detail.congestion, " \
                   "x_dpd_bill_detail.eu_clearance, " \
                   "x_dpd_bill_detail.return_charge, " \
                   "x_dpd_bill_detail.failed_collection, " \
                   "x_dpd_bill_detail.scottish_zone, " \
                   "x_dpd_bill_detail.tax_prepaid, " \
                   "x_dpd_bill_detail.handling, " \
                   "x_dpd_bill_detail.contractual_liability, " \
                   "x_dpd_bill_detail.oversize_exports, " \
                   "x_dpd_bill_detail.unsuccessful_eu_export, " \
                   "x_dpd_bill_detail.eu_export_return " \
                   "FROM x_mi_bill_detail " \
                   "JOIN x_dpd_bill_detail ON x_dpd_bill_detail.mi_code = x_mi_bill_detail.mi_code " \
                   "WHERE x_mi_bill_detail.delivery_fee_checked = 0 " \
                   "and x_mi_bill_detail.bill_year <= %s " \
                   "and x_mi_bill_detail.bill_month <= %s " \
                   "and x_mi_bill_detail.express_company = 'DPD' " \
                   "ORDER BY x_dpd_bill_detail.mi_code, " \
                   "x_mi_bill_detail.bill_year, x_mi_bill_detail.bill_month "


UPS_BILL_MI_SQL = "SELECT x_ups_bill_detail.id, " \
                  "x_ups_bill_detail.mi_code, " \
                  "x_mi_bill_detail.bill_year,  " \
                  "x_mi_bill_detail.bill_month, " \
                  "x_mi_bill_detail.express_company, " \
                  "x_ups_bill_detail.ups_bill_no as bill_no, " \
                  "x_mi_bill_detail.parcel_id, " \
                  "x_mi_bill_detail.mi_code, " \
                  "x_mi_bill_detail.total_qty, " \
                  "x_mi_bill_detail.goods_id, " \
                  "x_mi_bill_detail.postcode, " \
                  "x_mi_bill_detail.package_code, " \
                  "x_mi_bill_detail.ready_datetime, " \
                  "x_mi_bill_detail.weight, " \
                  "x_ups_bill_detail.fee_desc as ups_fee_desc, " \
                  "x_ups_bill_detail.fee_amount as ups_fee_amount " \
                  "FROM x_ups_bill_detail " \
                  "JOIN x_mi_bill_detail ON x_ups_bill_detail.mi_code = x_mi_bill_detail.mi_code " \
                  "WHERE x_mi_bill_detail.express_company = 'UPS' " \
                  "AND x_ups_bill_detail.is_use = 0 " \
                  "AND NOT (x_ups_bill_detail.fee_desc IN %s ) " \
                  "AND NOT (x_ups_bill_detail.mi_code IN %s ) " \
                  "AND x_mi_bill_detail.bill_year <= %s " \
                  "AND x_mi_bill_detail.bill_month <= %s " \
                  "ORDER BY x_ups_bill_detail.mi_code, x_ups_bill_detail.fee_desc"
