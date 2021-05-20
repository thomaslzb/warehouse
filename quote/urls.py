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
from .views import ProfitDetailUpdateView, ProfitDetailListView, GeneralQuoteInquireUK, GeneralQuoteInquireEURO

app_name = 'quote'

urlpatterns = [
    path('setup_profit/users/<pk>/', login_required(UserSetupProfitView.as_view()), name='profit-rate'),
    path('setup_profit/users-profit-detail/<pk>/',
         login_required(ProfitDetailListView.as_view()), name='profit-detail'),
    path('uk/', login_required(QuoteInquireUK.as_view()), name='inquire-uk'),
    path('euro/', login_required(QuoteInquireEuro.as_view()), name='inquire-euro'),
    path('users/', login_required(UserListView.as_view()), name='user-list'),

    path('setup_profit/users-profit-update-detail/<user_id>/<euro_id>/<uk_id>/<is_uk>',
         login_required(ProfitDetailUpdateView.as_view()), name='profit-update-detail'),

    path('general/quote-uk/',
         login_required(GeneralQuoteInquireUK.as_view()), name='general-quote-uk'),

    path('general/quote-euro/',
         login_required(GeneralQuoteInquireEURO.as_view()), name='general-quote-euro'),

]
