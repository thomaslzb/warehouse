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
from .views import SkuCreateView, SkuUpdateView, SkuDeleteView, SkuSaveAndAnotherView, SkuFileView

app_name = 'sku'
urlpatterns = [
    path('sku-list/', SkuListView.as_view(), name='sku-list'),
    path('sku/<pk>/uk/', SkuUKDetail.as_view(), name='sku-detail-uk'),
    path('sku/<pk>/euro/', SkuEuroDetail.as_view(), name='sku-detail-euro'),
    path('touk/<slug:slug>/', SkuQuoteUK.as_view(), name='sku-uk'),
    path('toeuro/<slug:slug>/', SkuQuoteEURO.as_view(), name='sku-euro'),
    path('sku/add/', SkuCreateView.as_view(), name='sku-create'),
    path('sku/add/another/', SkuSaveAndAnotherView.as_view(), name='sku-create-add'),
    path('sku/<pk>/', SkuUpdateView.as_view(), name='sku-update'),
    path('sku/<pk>/delete/', SkuDeleteView.as_view(), name='sku-delete'),
    path('file/upload/', SkuFileView.as_view(), name='sku-file-upload'),
]
