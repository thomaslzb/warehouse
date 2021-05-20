#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   forms.py    
@Contact :   thomaslzb@hotmail.com
@License :   (C)Copyright 2020-2022, Zibin Li

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
28/04/2021 13:02   lzb       1.0         None
"""
from django import forms

from flc.models import FLCPostcodeModel
from utils.tools import format_postcode


class FbaQuoteForm(forms.Form):
    port = forms.CharField(required=True)
    hs_code_number = forms.IntegerField(required=True, )
    fba_number = forms.IntegerField(required=True)
    first_delivery = forms.BooleanField(required=False, initial=0)

    def clean_hs_code_number(self):
        hs_code_number = int(self.cleaned_data.get('hs_code_number'))
        if hs_code_number <= 0:
            raise forms.ValidationError('HS Code 的数量必须大于0.')

    def clean_fba_number(self):
        fba_number = int(self.cleaned_data.get('fba_number'))
        if fba_number <= 0:
            raise forms.ValidationError('FBA的数量必须大于0.')


class PrivateQuoteForm(forms.Form):
    port = forms.CharField(required=True)
    hs_code_number = forms.IntegerField(required=True, )
    postcode = forms.CharField(required=True, error_messages={'required': '请填写正确的英国邮编'})
    volume = forms.DecimalField(required=True, )
    weight = forms.DecimalField(required=True, )

    def clean_hs_code_number(self):
        hs_code_number = int(self.cleaned_data.get('hs_code_number'))
        if hs_code_number <= 0:
            raise forms.ValidationError('HS Code 的数量必须大于0.')
        return hs_code_number

    def clean_volume(self):
        volume = int(self.cleaned_data.get('volume'))
        if volume <= 0:
            raise forms.ValidationError('体积必须大于0.')
        return volume

    def clean_weight(self):
        weight = int(self.cleaned_data.get('weight'))
        if weight <= 0:
            raise forms.ValidationError('重量必须大于0.')
        return weight

    def clean_postcode(self):
        postcode = self.cleaned_data['postcode'].upper().strip()
        postcode = format_postcode(postcode)

        queryset = FLCPostcodeModel.objects.filter(postcode=postcode)

        if not queryset:
            raise forms.ValidationError('输入的邮编不正确，请查证。')
        return postcode


class CabinetQuoteForm(forms.Form):
    port = forms.CharField(required=True)
    hs_code_number = forms.IntegerField(required=True, )

    def clean_hs_code_number(self):
        hs_code_number = int(self.cleaned_data.get('hs_code_number'))
        if hs_code_number <= 0:
            raise forms.ValidationError('HS Code 的数量必须大于0.')


