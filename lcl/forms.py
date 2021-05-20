#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   forms.py    
@Contact :   thomaslzb@hotmail.com
@License :   (C)Copyright 2020-2022, Zibin Li

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
31/03/2021 14:40   lzb       1.0         None
"""

from django import forms

from .models import LclCompanyModel, LclFuelChargeModel


class LclCompanyForm(forms.ModelForm):
    class Meta:
        model = LclCompanyModel
        fields = ['code', 'name', 'telephone', 'email', 'contact', 'remark', 'op_user', 'is_used', ]

    def clean_code(self):
        code = self.cleaned_data.get('code')
        return code.upper()

    def clean_is_used(self):
        is_used = self.data.get('is_used')
        return is_used


class LclFuelSurchargeForm(forms.ModelForm):
    class Meta:
        model = LclFuelChargeModel
        fields = ['company_code', 'begin_date', 'expire_date', 'fuel_charge', ]

    def clean_begin_date(self):
        company_code = self.data.get('company_code')
        begin_date = self.cleaned_data.get('begin_date')
        queryset = LclFuelChargeModel.objects.filter(company_code=company_code,
                                                     begin_date__lt=begin_date,
                                                     expire_date__gt=begin_date,
                                                     )
        if queryset:
            raise forms.ValidationError('Begin Date has some error.')
        return begin_date

    def clean_expire_date(self):
        company_code = self.data.get('company_code')
        begin_date = self.data.get('begin_date')
        expire_date = self.data.get('expire_date')

        if expire_date < begin_date:
            raise forms.ValidationError('Expire Date must be more than Begin Date.')

        queryset = LclFuelChargeModel.objects.filter(company_code=company_code,
                                                     begin_date__gt=expire_date,
                                                     expire_date__lt=expire_date,
                                                     )
        if queryset:
            raise forms.ValidationError('Expire Date has some error.')

        return expire_date

    def clean_fuel_charge(self):
        fuel_charge = self.data.get('fuel_charge')
        if not fuel_charge:
            raise forms.ValidationError('Please input Fuel Surcharge Rate.')
        return fuel_charge
