#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   urls.py    
@Contact :   thomaslzb@hotmail.com
@License :   (C)Copyright 2020-2022, Zibin Li

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
19/03/2021 15:35   lzb       1.0         None
"""

from django.urls import path
from django.contrib.auth.decorators import login_required

from flc.views import FlcCompanyListView, flc_company_create, flc_company_update
from flc.views import FlcPriceListView, flc_price_create, flc_price_update
from flc.views import FlcPortListView, flc_port_create, flc_port_update
from flc.views import FlcFuelSurchargeListView, flc_fuel_surcharge_create, flc_fuel_surcharge_update
from flc.views import FlcContainerListView, FlcPostcodeListView, FLCQuoteView

app_name = 'flc'

urlpatterns = [
    path('company/', login_required(FlcCompanyListView.as_view()), name='flc_company_list'),
    path('company/create/', flc_company_create, name='flc_company_create'),
    path('company/<pk>/update', flc_company_update, name='flc_company_update'),

    path('fuel-surcharge/', login_required(FlcFuelSurchargeListView.as_view()), name='flc_fuel_surcharge_list'),
    path('fuel-surcharge/create/', flc_fuel_surcharge_create, name='flc_fuel_surcharge_create'),
    path('fuel-surcharge/<pk>/<slug>/update', flc_fuel_surcharge_update, name='flc_fuel_surcharge_update'),

    path('port/', login_required(FlcPortListView.as_view()), name='flc_port_list'),
    path('port/create/', flc_port_create, name='flc_port_create'),
    path('port/<pk>/update', flc_port_update, name='flc_port_update'),

    path('container/', login_required(FlcContainerListView.as_view()), name='flc_container_list'),

    path('postcode/', login_required(FlcPostcodeListView.as_view()), name='flc_postcode_list'),

    path('price/', login_required(FlcPriceListView.as_view()), name='flc_price_list'),
    path('price/create/', flc_price_create, name='flc_price_create'),
    path('price/<company_code>/<port_code>/<destination_type>/<destination>/<container>/<begin_date>/update', flc_price_update,
         name='flc_price_update'),

    path('quote/', login_required(FLCQuoteView.as_view()), name='flc_quote'),

]
