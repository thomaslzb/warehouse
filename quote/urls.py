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
from .views import QuoteIndex

urlpatterns = [
    path('', login_required(QuoteIndex.as_view()), name='index'),
]
