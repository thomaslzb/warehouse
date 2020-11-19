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
from django.contrib.auth.decorators import login_required
from django.urls import re_path, path
from .views import LoginView, LogoutView, MyProfile, MyProfileUpdateView, \
    AddUserView, EditUserView, ResetPwdView, ChangePwdView

app_name = 'users'
urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('myprofile/<pk>/', login_required(MyProfile.as_view()), name='my_profile'),
    path('myprofile/update/<pk>/', login_required(MyProfileUpdateView.as_view()), name='my_profile_update'),
    path('new_user/', login_required(AddUserView.as_view()), name='add_new_user'),
    path('edit_user/<pk>', login_required(EditUserView.as_view()), name='edit_quote_user'),
    path('user/<pk>/reset-pwd/', login_required(ResetPwdView.as_view()), name='reset_password'),
    path('user/<pk>/change-pwd/', login_required(ChangePwdView.as_view()), name='change_password'),

    # path('user/<pk>/pwdchange/', pwd_change, name='pwd_change'),
    # re_path(r'^register/$', views.register, name='register'),
    # re_path(r'^user/(?P<pk>\d+)/profile/update/$', views.profile_update, name='profile_update'),
]

