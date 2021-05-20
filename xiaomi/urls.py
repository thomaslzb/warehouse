#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   urls.py.py    
@Contact :   thomaslzb@hotmail.com
@License :   (C)Copyright 2020-2022, Zibin Li

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
02/03/2021 16:57   lzb       1.0         None
"""
from django import views
from django.contrib.auth.decorators import login_required
from django.urls import path

from xiaomi.calc_bill_function import calc_progress
from xiaomi.views import MiBillMainListView, MiBillDetailListView, MiFileUploadView, loadfile, loadfile_with_cost, \
    MiLookup
from xiaomi.views import RentalBillMainListView, RentalDetailListView, RentalDailyChart, RentalFileUploadView
from xiaomi.views import FuelSurchargeListView, FuelSurchargeCreateView

from xiaomi.views import UPSBillMainListView, UPSBillDetailListView, UPSFileUploadView
from xiaomi.views import DPDBillMainListView, DPDBillDetailListView, DPDFileUploadView
from xiaomi.views import DCGBillListView, DCGBillDetailListView
from xiaomi.views import CalcDcgUpsBillCreateView, CongestionZoneListView, show_progress
from xiaomi.views import ItemDeliveryListView, ItemHandleListView, ItemSpecialListView, ItemZoneListView

app_name = 'xiaomi'

urlpatterns = [
    #  小米账单
    path('mi-list/', login_required(MiBillMainListView.as_view()), name='mi_bill_list_main'),
    path('mi-list/detail/<pk>/<slug>/', login_required(MiBillDetailListView.as_view()), name='mi_bill_list_detail'),

    path('show-progress/', show_progress, name='mi_show_progress'),
    path('calc-progress/', calc_progress, name='calc_progress'),
    path('mi-file/upload/', login_required(MiFileUploadView.as_view()), name='mi-file-upload'),

    #  UPS 账单
    path('ups-list/', login_required(UPSBillMainListView.as_view()), name='ups_bill_list_main'),
    path('ups-list/<pk>/', login_required(UPSBillDetailListView.as_view()), name='ups_bill_list_detail'),
    path('ups-file/upload/', login_required(UPSFileUploadView.as_view()), name='ups-file-upload'),

    #  DPD 账单
    path('dpd-list/', login_required(DPDBillMainListView.as_view()), name='dpd_bill_list_main'),
    path('dpd-list/detail/', login_required(DPDBillDetailListView.as_view()),
         name='dpd_bill_list_detail'),
    path('dpd-file/upload/', login_required(DPDFileUploadView.as_view()), name='dpd-file-upload'),

    #  仓储费账单
    path('rental-list/', login_required(RentalBillMainListView.as_view()), name='rental_list_main'),
    path('rental-list/detail/', login_required(RentalDetailListView.as_view()), name='rental_list_detail'),
    path('rental-file/upload/', login_required(RentalFileUploadView.as_view()), name='rental-file-upload'),
    path('rental/chart/', login_required(RentalDailyChart.as_view()), name='rental-chart'),

    #  DCG-UK 账单
    path('dcg-list/', login_required(DCGBillListView.as_view()), name='dcg_bill_list'),
    path('dcg-list/detail/<pk>/<slug>/', login_required(DCGBillDetailListView.as_view()), name='dcg_bill_detail'),

    # DCG-UK 账单计算
    path('dcg-list/calc-ups-bill/', login_required(CalcDcgUpsBillCreateView.as_view()), name='calc_ups_bill'),

    # 相关参数列表
    path('item-list/delivery/<pk>/', login_required(ItemDeliveryListView.as_view()), name='item_delivery'),
    path('item-list/postcode/<pk>/', login_required(ItemZoneListView.as_view()), name='item_postcode'),
    path('congestion/postcode/<pk>/', login_required(CongestionZoneListView.as_view()), name='congestion_zone'),
    path('item-list/handle/', login_required(ItemHandleListView.as_view()), name='item_handle'),
    path('item-list/special-item/', login_required(ItemSpecialListView.as_view()), name='item_special'),

    # 下载文件，保存成为excel文件
    path('dcg-bill/loadfile/<bill_year>/<bill_month>', login_required(loadfile), name='file_load'),
    path('dcg-bill/loadfile-with-cost/<bill_year>/<bill_month>', login_required(loadfile_with_cost),
         name='file_load_cost'),

    # 燃油费维护
    path('fuel-surcharge-list/', login_required(FuelSurchargeListView.as_view()), name='fuel-surcharge-list'),
    path('fuel-surcharge-list/add/', login_required(FuelSurchargeCreateView.as_view()), name='fuel-surcharge-add'),

    path('lookup/', MiLookup.as_view(), name='lookup-view'),

]

