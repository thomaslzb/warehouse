#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   forms.py    
@Contact :   thomaslzb@hotmail.com
@License :   (C)Copyright 2020-2022, Zibin Li

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
07/09/2020 12:20   lzb       1.0         None
"""
from django import forms

from quote.models import UserSetupProfit


class QuoteUKForm(forms.Form):
    length = forms.IntegerField(required=True, error_messages={'required': 'Length must be required.'})
    width = forms.IntegerField(required=True, error_messages={'required': 'Width must be required.'})
    high = forms.IntegerField(required=True, error_messages={'required': 'High must be required.'})
    weight = forms.DecimalField(required=True, max_digits=10, decimal_places=2,
                                error_messages={'required': 'Weight must be required.'})
    qty = forms.IntegerField(required=True, error_messages={'required': 'Quantity must be required.'})
    postcode = forms.CharField(required=True, error_messages={'required': 'Postcode must be required.'})

    def clean_length(self):
        length = int(self.cleaned_data.get('length'))
        if length <= 0:
            raise forms.ValidationError("Length must be more than 0")
        return length

    def clean_width(self):
        width = int(self.cleaned_data.get('width'))
        if width <= 0:
            raise forms.ValidationError("Length must be more than 0")
        return width

    def clean_high(self):
        high = int(self.cleaned_data.get('high'))
        if high <= 0:
            raise forms.ValidationError("Length must be more than 0")
        return high

    def clean_weight(self):
        weight = float(self.cleaned_data.get('weight'))
        if weight <= 0:
            raise forms.ValidationError("Length must be more than 0")
        return weight

    def clean_qty(self):
        qty = int(self.cleaned_data.get('qty'))
        if qty <= 0:
            raise forms.ValidationError("Qty. must be more than 0")
        return qty

    def clean_postcode(self):
        postcode = self.cleaned_data.get('postcode')
        if len(postcode) < 6:
            raise forms.ValidationError("Postcode isn't correct.")

        if postcode.isdecimal() or postcode[0].isdecimal():
            raise forms.ValidationError("Postcode isn't correct.")
        return postcode


class QuoteEuroForm(forms.Form):
    length = forms.IntegerField(required=True, error_messages={'required': 'Length must be required.'})
    width = forms.IntegerField(required=True, error_messages={'required': 'Width must be required.'})
    high = forms.IntegerField(required=True, error_messages={'required': 'High must be required.'})
    weight = forms.DecimalField(required=True, max_digits=10, decimal_places=2,
                                error_messages={'required': 'Weight must be required.'})
    qty = forms.IntegerField(required=True, error_messages={'required': 'Quantity must be required.'})

    def clean_length(self):
        length = int(self.cleaned_data.get('length'))
        if length <= 0:
            raise forms.ValidationError("Length must be more than 0")
        return length

    def clean_width(self):
        width = int(self.cleaned_data.get('width'))
        if width <= 0:
            raise forms.ValidationError("Length must be more than 0")
        return width

    def clean_high(self):
        high = int(self.cleaned_data.get('high'))
        if high <= 0:
            raise forms.ValidationError("Length must be more than 0")
        return high

    def clean_weight(self):
        weight = float(self.cleaned_data.get('weight'))
        if weight <= 0:
            raise forms.ValidationError("Length must be more than 0")
        return weight

    def clean_qty(self):
        qty = int(self.cleaned_data.get('qty'))
        if qty <= 0:
            raise forms.ValidationError("Qty. must be more than 0")
        return qty


class UserSetupProfitForm(forms.ModelForm):
    class Meta:
        model = UserSetupProfit
        # fields = ['user', 'is_uk', 'uk_area', 'euro_area', 'fix_amount', 'percent', ]
        fields = ['fix_amount', 'percent', ]
