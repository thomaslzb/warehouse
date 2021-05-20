#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   forms.py
@Contact :   thomaslzb@hotmail.com
@License :   (C)Copyright 2020-2022, Zibin Li

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
03/03/2021 09:03   lzb       1.0         None
"""
import datetime

from django import forms

from xiaomi.models import DcgBillModel, MiAccountBillMainModel, FuelSurchargeModel


class CalcDcgUpsBillForm(forms.ModelForm):
    class Meta:
        model = DcgBillModel
        fields = ['bill_year', 'bill_month']

    def clean(self):
        bill_year = self.cleaned_data.get("bill_year")
        bill_month = self.cleaned_data.get("bill_month")
        queryset = MiAccountBillMainModel.objects.filter(bill_year=bill_year, bill_month=bill_month)
        year_str = str(bill_year)
        if bill_month < 10:
            month_str = '0' + str(bill_month)
        else:
            month_str = str(bill_month)
        if not queryset:
            raise forms.ValidationError('Error: Xiaomi bill (' + year_str + '-' + month_str + ') can not be found.')
        else:
            queryset = DcgBillModel.objects.filter(bill_year=bill_year, bill_month=bill_month)
            if queryset:
                raise forms.ValidationError('The ' + year_str + '-' + month_str + ' bills has be calculated.')


class FuelSurchargeForm(forms.ModelForm):
    class Meta:
        model = FuelSurchargeModel
        fields = ['express_company', 'begin_date', 'end_date', 'fuel_surcharge', 'range']

    def clean_fuel_surcharge(self):
        fuel_surcharge = self.cleaned_data.get("fuel_surcharge")
        if fuel_surcharge < 0:
            raise forms.ValidationError('Fuel Surcharge must be more than 0.')
        return fuel_surcharge

    def clean_begin_date(self):
        begin_date = self.cleaned_data.get("begin_date")
        express_company = self.cleaned_data.get("express_company")

        if express_company == 'UPS':
            if begin_date.weekday() != 0:
                raise forms.ValidationError('The begin Date must be MONDAY ')

        queryset = FuelSurchargeModel.objects.filter(begin_date__gte=begin_date,
                                                     express_company=express_company).order_by('-begin_date')
        if queryset:
            begin_date = queryset[0].begin_date.strftime('%d/%m/%Y')
            raise forms.ValidationError('The begin Date must be greater than '+begin_date)
        return begin_date


