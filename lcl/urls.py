#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   urls.py.py    
@Contact :   thomaslzb@hotmail.com
@License :   (C)Copyright 2020-2022, Zibin Li

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
01/09/2020 10:29   lzb       1.0         None
"""
from django.urls import path
from django.contrib.auth.decorators import login_required
from .views import LclCompanyListView, company_create, company_update
from .views import LclCalculationView
from .views import LclFuelSurchargeListView, fuel_surcharge_create, fuel_surcharge_update
app_name = 'lcl'

urlpatterns = [
    path('company/', login_required(LclCompanyListView.as_view()), name='lcl_company_list'),
    path('company/create/', company_create, name='company_create'),
    path('company/<pk>/update', company_update, name='company_update'),

    path('fuel-surcharge/', login_required(LclFuelSurchargeListView.as_view()), name='lcl_fuel_surcharge_list'),
    path('fuel-surcharge/create/', fuel_surcharge_create, name='fuel_surcharge_create'),
    path('fuel-surcharge/<pk>/<slug>/update', fuel_surcharge_update, name='fuel_surcharge_update'),

    path('calc/', login_required(LclCalculationView.as_view()), name='lcl_calculation'),

]
