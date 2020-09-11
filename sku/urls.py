#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   urls.py.py    
@Contact :   thomaslzb@hotmail.com
@License :   (C)Copyright 2020-2022, Zibin Li

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
11/09/2020 08:32   lzb       1.0         None
"""

from django.urls import path
from .views import SkuListView, SkuUKDetail, SkuEuroDetail,  SkuQuoteUK, SkuQuoteEURO

app_name = 'sku'
urlpatterns = [
    path('SkuList/', SkuListView.as_view(), name='sku-list'),
    path('Sku/UK/<pk>/', SkuUKDetail.as_view(), name='sku-detail-uk'),
    path('Sku/Euro/<pk>/', SkuEuroDetail.as_view(), name='sku-detail-euro'),
    path('ToUK/<slug:slug>', SkuQuoteUK.as_view(), name='sku-uk'),
    path('ToEuro/<slug:slug>', SkuQuoteEURO.as_view(), name='sku-euro'),
]
