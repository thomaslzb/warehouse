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
from .models import Warehouse


class SoltTimeForm(forms.ModelForm):
    class Meta:
        model = Warehouse
        exclude = ["progress", "op_user", "position", "status", "op_datetime", "hailerid", "havetime", ]

"""
    def clean_deliveryref(self):
        deliveryref = self.cleaned_data.get('hailer')+self.cleaned_data.get('deliveryref')

        filter_result = Warehouse.objects.filter(deliveryref__exact=deliveryref)
        if filter_result:
            raise forms.ValidationError("This Delivery Ref. is exist")
        return deliveryref
"""


class SoltTimeUpdateForm(forms.ModelForm):
    class Meta:
        model = Warehouse
        exclude = ["position", "status", "op_datetime", "hailerid", "workdate", "slottime",
                   "deliveryref", "vehiclereg", "havetime", "op_user", "progress"]
