#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   urls.py    
@Contact :   thomaslzb@hotmail.com
@License :   (C)Copyright 2020-2022, Zibin Li

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
15/08/2020 08:22   lzb       1.0         None
"""

from django.urls import path
from .views import SoltListView,SoltDetailView
from django.contrib.auth.decorators import login_required


app_name = 'slot'

urlpatterns = [
    path('', login_required(SoltListView.as_view()), name='slot_list'),
    path('deliveryRef=<pk>', login_required(SoltDetailView.as_view()), name='slot_Detail'),
    # re_path(r'^slot/(?P<pk>\d+)/slot_profile/$', views.profile, name='slot_profile'),
    # re_path(r'^slot/(?P<pk>\d+)/slot_profile/update/$', views.profile_update, name='slot_update'),
    # re_path(r'^slot/(?P<pk>\d+)/slot_change/$', views.pwd_change, name='slot_change'),
]
