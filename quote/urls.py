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
from .views import QuoteInquireUK, QuoteInquireEuro, UserListView, UserSetupProfitView

urlpatterns = [
    path('uk/', login_required(QuoteInquireUK.as_view()), name='inquire-uk'),
    path('euro/', login_required(QuoteInquireEuro.as_view()), name='inquire-euro'),
    path('users/', login_required(UserListView.as_view()), name='user-list'),
    path('setup/mode/<pk>/', login_required(UserSetupProfitView.as_view()), name='profit-mode')


]
