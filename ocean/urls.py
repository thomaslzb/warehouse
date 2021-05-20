#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   urls.py    
@Contact :   thomaslzb@hotmail.com
@License :   (C)Copyright 2020-2022, Zibin Li

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
28/04/2021 13:01   lzb       1.0         None
"""

from django.urls import path
from django.contrib.auth.decorators import login_required

from ocean.views import OceanCalcFbaView, OceanCalcPrivateView, OceanCalcCabinetView

app_name = 'ocean'

urlpatterns = [
    path('fba/', login_required(OceanCalcFbaView.as_view()), name='ocean_fba'),
    path('private/', login_required(OceanCalcPrivateView.as_view()), name='ocean_private'),
    path('cabinet/', login_required(OceanCalcCabinetView.as_view()), name='ocean_cabinet'),

]
