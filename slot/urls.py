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
from .views import SlotListView, SlotDetailView, SlotUpdateView, SlotTimeDeleteView, SlotSearchListView
from django.contrib.auth.decorators import login_required


app_name = 'slot'

urlpatterns = [
    path('', login_required(SlotListView.as_view()), name='slot_list'),
    path('<pk>', login_required(SlotDetailView.as_view()), name='slot_detail'),
    path('Update/', login_required(SlotUpdateView.as_view()), name='slot_update'),
    path('delete/<pk>', login_required(SlotTimeDeleteView.as_view()), name='slot_delete'),
    path('list/', login_required(SlotSearchListView.as_view()), name='slot_list_search'),

]
