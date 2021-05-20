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
from .views import SlotHaulierListView, SlotHaulierUpdateView
from .views import SlotUserListView, SlotHaulierCreateView
from .views import uploads, file_download
from django.contrib.auth.decorators import login_required


app_name = 'slot'

urlpatterns = [
    path('list/', login_required(SlotListView.as_view()), name='slot_list'),
    path('detail/<pk>/<slug>/', login_required(SlotDetailView.as_view()), name='slot_detail'),
    path('update/', login_required(SlotUpdateView.as_view()), name='slot_update'),
    path('delete/<pk>/', login_required(SlotTimeDeleteView.as_view()), name='slot_delete'),

    path('search-list/', login_required(SlotSearchListView.as_view()), name='slot_list_search'),
    path('user-list/', login_required(SlotUserListView.as_view()), name='slot_user_list'),

    path('haulier-list/', login_required(SlotHaulierListView.as_view()), name='slot_haulier_list'),
    path('haulier-add/', login_required(SlotHaulierCreateView.as_view()), name='slot_haulier_add'),
    path('haulier-update/<pk>/', login_required(SlotHaulierUpdateView.as_view()), name='slot_haulier_update'),

    path('uploads/', login_required(uploads), name='uploads_files'),
    path('files/download/', login_required(file_download), name='download_file'),

]

