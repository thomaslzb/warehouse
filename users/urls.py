#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   urls.py    
@Contact :   thomaslzb@hotmail.com
@License :   (C)Copyright 2020-2022, Zibin Li

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
14/08/2020 16:41   lzb       1.0         None
"""

from django.urls import re_path, path
from .views import LoginView, LogoutView, MyProfile, pwd_change, MyProfileUpdateView

app_name = 'users'
urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('myprofile/<pk>/', MyProfile.as_view(), name='my_profile'),
    path('myprofile/update/<pk>/', MyProfileUpdateView.as_view(), name='my_profile_update'),

    # path('user/<pk>/pwdchange/', pwd_change, name='pwd_change'),
    # re_path(r'^register/$', views.register, name='register'),
    # re_path(r'^user/(?P<pk>\d+)/profile/update/$', views.profile_update, name='profile_update'),
]

