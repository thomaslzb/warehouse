#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   forms.py    
@Contact :   thomaslzb@hotmail.com
@License :   (C)Copyright 2020-2022, Zibin Li

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
15/08/2020 14:22   lzb       1.0         None
"""
from django import forms
from .models import Warehouse, SlotFiles


class SlotTimeForm(forms.ModelForm):
    class Meta:
        model = Warehouse
        exclude = ["progress", "op_user", "position", "status", "op_datetime", "hailerid", "havetime", "last_update"]


class SlotTimeUpdateForm(forms.ModelForm):
    class Meta:
        model = Warehouse
        exclude = ["position", "status", "op_datetime", "hailerid", "workdate", "slottime",
                   "deliveryref", "vehiclereg", "havetime", "op_user", "progress"]


class SlotFilesForm(forms.ModelForm):
    class Meta:
        model = SlotFiles
        fields = ('file', )

