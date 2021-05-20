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
from django.urls import path
from .views import LoginView, LogoutView, MyProfile, MyProfileUpdateView, ChangeSlotUserPwdView
from .views import AddUserView, EditUserView, ResetPwdView, ChangeQuoteUserPwdView, SetUserPermissionView
from .views import SlotUserProfile, SlotUserProfileUpdateView, SlotAddUserView

app_name = 'users'
urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('myprofile/<pk>/', login_required(MyProfile.as_view()), name='my_profile'),
    path('myprofile/update/<pk>/', login_required(MyProfileUpdateView.as_view()), name='my_profile_update'),
    path('quote/add/', login_required(AddUserView.as_view()), name='add_quote_user'),
    path('quote/edit/<pk>', login_required(EditUserView.as_view()), name='edit_quote_user'),
    path('quote/reset-pwd/<pk>/', login_required(ResetPwdView.as_view()), name='reset_password'),
    path('quote/change-pwd/<pk>', login_required(ChangeQuoteUserPwdView.as_view()), name='change_password'),
    path('quote/set_permission/<pk>/', login_required(SetUserPermissionView.as_view()), name='set_user_permission'),

    path('detail/<pk>/', login_required(SlotUserProfile.as_view()), name='slot_user_profile'),
    path('change-pwd/<pk>/', login_required(ChangeSlotUserPwdView.as_view()),
         name='slot_user_change_password'),
    path('slot/add/', login_required(SlotAddUserView.as_view()), name='slot_add_user'),
    path('update/<pk>/', login_required(SlotUserProfileUpdateView.as_view()), name='slot_user_update'),

]

