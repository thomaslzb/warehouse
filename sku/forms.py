#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   forms.py    
@Contact :   thomaslzb@hotmail.com
@License :   (C)Copyright 2020-2022, Zibin Li

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
11/09/2020 11:58   lzb       1.0         None
"""
import decimal

from django import forms
from .models import Sku


class SkuUKForm(forms.Form):
    qty = forms.IntegerField(required=True, error_messages={'required': 'Quantity must be required.'})
    postcode = forms.CharField(required=True, error_messages={'required': 'Postcode must be required.'})

    def clean_qty(self):
        qty = int(self.cleaned_data.get('qty'))
        if qty <= 0:
            raise forms.ValidationError("Qty must be more than 0")
        return qty

    def clean_postcode(self):
        postcode = self.cleaned_data.get('postcode')
        if len(postcode) < 6:
            raise forms.ValidationError("Postcode isn't correct.")

        if postcode.isdecimal() or postcode[0].isdecimal():
            raise forms.ValidationError("Postcode isn't correct.")
        return postcode


class SkuEuroForm(forms.Form):
    qty = forms.IntegerField(required=True, error_messages={'required': 'Quantity must be required.'})

    def clean_qty(self):
        qty = int(self.cleaned_data.get('qty'))
        if qty <= 0:
            raise forms.ValidationError("Qty must be more than 0")
        return qty


class SkuForm(forms.ModelForm):
    class Meta:
        model = Sku
        fields = ['sku_no', 'sku_name', 'sku_length', 'sku_width', 'sku_high', 'sku_weight',
                  'sku_width', 'is_ok', 'custom']
        # exclude = ['last_update', ]

    # def clean_sku_no(self):
    #     sku_no = self.cleaned_data.get('sku_no')
    #     queryset = Sku.objects.filter(sku_no__exact=sku_no, custom_id=request.user.id)
    #     if queryset:
    #         raise forms.ValidationError("This Sku No. is exist.")
    #     return sku_no

    def clean_sku_length(self):
        length = int(self.cleaned_data.get('sku_length'))
        if length <= 0:
            raise forms.ValidationError("Length must be more than 0")
        return length

    def clean_sku_width(self):
        width = int(self.cleaned_data.get('sku_width'))
        if width <= 0:
            raise forms.ValidationError("Width must be more than 0")
        return width

    def clean_sku_high(self):
        high = int(self.cleaned_data.get('sku_high'))
        if high <= 0:
            raise forms.ValidationError("High must be more than 0")
        return high

    def clean_sku_weight(self):
        weight = decimal.Decimal(self.cleaned_data.get('sku_weight'))
        if weight <= 0:
            raise forms.ValidationError("Weight must be more than 0")
        return weight



