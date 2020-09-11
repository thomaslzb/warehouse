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
from django import forms


class SkuUKForm(forms.Form):
    qty = forms.IntegerField(required=True, error_messages={'required': 'Quantity must be required.'})
    postcode = forms.CharField(required=True, error_messages={'required': 'Postcode must be required.'})

    def clean_qty(self):
        qty = int(self.cleaned_data.get('qty'))
        if qty <= 0:
            raise forms.ValidationError("Length must be more than 0")
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
            raise forms.ValidationError("Length must be more than 0")
        return qty

