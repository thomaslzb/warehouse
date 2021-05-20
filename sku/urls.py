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
from django.contrib.auth.decorators import login_required
from django.urls import path
from .views import SkuListView, SkuUKDetail, SkuEuroDetail,  SkuQuoteUK, SkuQuoteEURO
from .views import SkuCreateView, SkuUpdateView, SkuDeleteView, SkuSaveAndAnotherView, SkuFileUploadView

app_name = 'sku'
urlpatterns = [
    path('sku-list/', login_required(SkuListView.as_view()), name='sku-list'),
    path('<pk>/uk/', login_required(SkuUKDetail.as_view()), name='sku-detail-uk'),
    path('<pk>/euro/', login_required(SkuEuroDetail.as_view()), name='sku-detail-euro'),
    path('touk/<slug:slug>/', login_required(SkuQuoteUK.as_view()), name='sku-uk'),
    path('toeuro/<slug:slug>/', login_required(SkuQuoteEURO.as_view()), name='sku-euro'),
    path('sku/add/', login_required(SkuCreateView.as_view()), name='sku-create'),
    path('sku/add/another/', login_required(SkuSaveAndAnotherView.as_view()), name='sku-create-add'),
    path('sku/<pk>/', login_required(SkuUpdateView.as_view()), name='sku-update'),
    path('sku/<pk>/delete/', login_required(SkuDeleteView.as_view()), name='sku-delete'),
    path('file/upload/', login_required(SkuFileUploadView.as_view()), name='sku-file-upload'),
]
