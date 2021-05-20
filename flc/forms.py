#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   forms.py    
@Contact :   thomaslzb@hotmail.com
@License :   (C)Copyright 2020-2022, Zibin Li

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
16/04/2021 10:01   lzb       1.0         None
"""
import datetime

from django import forms
from django.db.models import Q

from utils.tools import format_postcode
from .models import FlcCompanyModel, FlcFuelChargeModel, FLCPortModel, FLCPriceModel, FLCPostcodeModel


class FlcCompanyForm(forms.ModelForm):
    class Meta:
        model = FlcCompanyModel
        fields = ['code', 'name', 'telephone', 'email', 'contact', 'remark', 'op_user', 'is_used', ]

    def clean_code(self):
        code = self.cleaned_data.get('code')
        return code.upper()

    def clean_is_used(self):
        is_used = self.data.get('is_used')
        return is_used


class FlcFuelSurchargeForm(forms.ModelForm):
    class Meta:
        model = FlcFuelChargeModel
        fields = ['company_code', 'begin_date', 'expire_date', 'fuel_charge', ]

    def clean_begin_date(self):
        company_code = self.data.get('company_code')
        begin_date = self.cleaned_data.get('begin_date')
        queryset = FlcFuelChargeModel.objects.filter(company_code=company_code,
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

        queryset = FlcFuelChargeModel.objects.filter(company_code=company_code,
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


class FlcPortForm(forms.ModelForm):
    class Meta:
        model = FLCPortModel
        fields = ['port_code', 'port_name', 'country', ]

    def clean_port_code(self):
        port_code = self.cleaned_data.get('port_code')
        return port_code.upper()


class FlcPriceForm(forms.ModelForm):
    class Meta:
        model = FLCPriceModel
        fields = ['destination', 'destination_type', 'begin_date', 'expire_date', 'date_type',
                  'price', 'company_code', 'container', 'port_code']

    def clean_destination(self):
        destination = self.data.get('destination')
        destination_type = self.data.get('destination_type')
        if destination == "":
            raise forms.ValidationError('Destination fields cannot be empty')
        if destination_type == "POSTCODE":
            if len(destination) <= 4:
                raise forms.ValidationError('Destinations - Postcode does not exist.')
            destination = format_postcode(destination)
            queryset_postcode = FLCPostcodeModel.objects.filter(postcode__exact=destination)
            if not queryset_postcode:
                raise forms.ValidationError('Destinations - Postcode does not exist.')

        return destination

    def clean_price(self):
        price = self.data.get('price')
        if price == '':
            raise forms.ValidationError('Please input price')
        return price

    def clean_begin_date(self):
        begin_date = self.data.get('begin_date')
        company_code = self.data.get('company_code')
        destination = self.data.get('destination')
        destination_type = self.data.get('destination_type')
        port_code = self.data.get('port_code')
        container = self.data.get('container')
        insert_id = self.data.get('insert_id')
        if insert_id == 'None':   # append
            queryset_begin_date = FLCPriceModel.objects.filter(begin_date__lte=begin_date,
                                                               expire_date__gte=begin_date,
                                                               company_code=company_code,
                                                               port_code__exact=port_code,
                                                               destination_type=destination_type,
                                                               destination=destination,
                                                               container=container,
                                                               )
        else:
            insert_id = int(insert_id)
            queryset_begin_date = FLCPriceModel.objects.filter(~Q(id=insert_id),
                                                               begin_date__lte=begin_date,
                                                               expire_date__gte=begin_date,
                                                               company_code=company_code,
                                                               port_code__exact=port_code,
                                                               destination_type=destination_type,
                                                               destination=destination,
                                                               container=container,
                                                               )
        if queryset_begin_date:
            raise forms.ValidationError('This begin date already exists in the database. ')
        return begin_date

    def clean_expire_date(self):
        begin_date = self.data.get('begin_date')
        expire_date = self.data.get('expire_date')

        if expire_date < begin_date:
            raise forms.ValidationError('Expire Date must be more than Begin Date.')

        begin_date = self.data.get('begin_date')
        company_code = self.data.get('company_code')
        destination = self.data.get('destination')
        destination_type = self.data.get('destination_type')
        container = self.data.get('container')
        port_code = self.data.get('port_code')
        insert_id = self.data.get('insert_id')
        if insert_id == 'None':   # append
            queryset_expire_date = FLCPriceModel.objects.filter(begin_date__lte=begin_date,
                                                                expire_date__gte=begin_date,
                                                                company_code=company_code,
                                                                destination_type=destination_type,
                                                                port_code__exact=port_code,
                                                                destination=destination,
                                                                container=container,
                                                                )
        else:
            insert_id = int(insert_id)
            queryset_expire_date = FLCPriceModel.objects.filter(~Q(id=insert_id),
                                                                begin_date__lte=begin_date,
                                                                expire_date__gte=begin_date,
                                                                company_code=company_code,
                                                                port_code__exact=port_code,
                                                                destination_type=destination_type,
                                                                destination=destination,
                                                                container=container,
                                                                )
        if queryset_expire_date:
            raise forms.ValidationError('This expire date already exists in the database. ')

        return expire_date


class FLCQuoteForm(forms.Form):
    postcode = forms.CharField(max_length=10, required=True)

    def clean_postcode(self):
        postcode = self.cleaned_data['postcode']
        postcode = format_postcode(postcode)
        queryset = FLCPostcodeModel.objects.filter(postcode=postcode)
        if not queryset:
            raise forms.ValidationError('Postcode is not correct.')
        return postcode

