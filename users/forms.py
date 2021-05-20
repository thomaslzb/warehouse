#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   forms.py    
@Contact :   thomaslzb@hotmail.com
@License :   (C)Copyright 2020-2022, Zibin Li

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
13/08/2020 14:14   lzb       1.0         None
"""
import re
from django import forms
from django.contrib.auth.models import User
from captcha.fields import CaptchaField
from django.db.models import Q
from quote.models import Company

PROFIT_MODE = [(0, 'By Percent'), (1, 'By Fix Amount')]


def email_check(email):
    if re.match(r'[^@]+@[^@]+\.[^@]', email):
        return True
    return False


class LoginForm(forms.Form):
    username = forms.CharField(required=True)
    password = forms.CharField(required=True)
    captcha = CaptchaField(label="Captcha")

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if email_check(username):
            filter_result = User.objects.filter(email__exact=username)
            if not filter_result:
                raise forms.ValidationError("This email does not exist.")
        else:
            filter_result = User.objects.filter(username__exact=username)
            if not filter_result:
                raise forms.ValidationError("This username does not exist. ")

        return username


class RegisterForm(forms.Form):
    username = forms.CharField(max_length=20, required=True)
    email = forms.CharField(widget=forms.PasswordInput, required=True)
    password1 = forms.CharField(widget=forms.PasswordInput, required=True)
    password2 = forms.CharField(widget=forms.PasswordInput, required=True)

    def clean_username(self):
        username = self.cleaned_data.get('username')

        if len(username) < 4:
            raise forms.ValidationError("Your username must be at least 4 characters long.")
        elif len(username) > 20:
            raise forms.ValidationError("Your username is too long.")
        else:
            filter_result = User.objects.filter(username__exact=username)
            if len(filter_result) > 0:
                raise forms.ValidationError("Your username already exists.")

        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')

        if email_check(email):
            filter_result = User.objects.filter(email__exact=email)
            if len(filter_result) > 0:
                raise forms.ValidationError("Your email already exists.")
        else:
            raise forms.ValidationError("Please enter a valid email.")

        return email

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if len(password1) < 8:
            raise forms.ValidationError('Your password is too short at least 8 characters.')
        elif len(password1) > 20:
            raise forms.ValidationError("Your password is too long, Max length is 20 characters.")

        return password1

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Password mismatch. Please enter again.")

        return password2


class ForgetPwdForm(forms.Form):
    email = forms.CharField(required=True, error_messages={"required": "Please input the correct email address"})


class ModifyPwdForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    re_password = forms.CharField(required=True, widget=forms.PasswordInput,)

    def clean_password(self):
        password = self.cleaned_data.get('password')

        if len(password) < 8:
            raise forms.ValidationError('Your password is too short at least 8 characters')
        elif len(password) > 20:
            raise forms.ValidationError('Your password is too long, Max length is 20 characters')

        return password

    def clean_re_password(self):
        password = self.cleaned_data.get('password')
        re_password = self.cleaned_data.get('re_password')

        if password and re_password and password != re_password:
            raise forms.ValidationError("Password mismatch. Please enter again.")

        return re_password


class ResetPwdForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    re_password = forms.CharField(required=True, widget=forms.PasswordInput,)

    def clean_password(self):
        password = self.cleaned_data.get('password')

        if len(password) < 8:
            raise forms.ValidationError('Your password is too short at least 8 characters')
        elif len(password) > 20:
            raise forms.ValidationError('Your password is too long, Max length is 20 characters')

        return password

    def clean_re_password(self):
        password = self.cleaned_data.get('password')
        re_password = self.cleaned_data.get('re_password')

        if password and re_password and password != re_password:
            raise forms.ValidationError("Password mismatch. Please enter again.")

        return re_password


class MyProfileForm(forms.ModelForm):
    username = forms.CharField(max_length=20, required=True)
    first_name = forms.CharField(max_length=20, required=False)
    last_name = forms.CharField(max_length=20, required=False)
    telephone = forms.CharField(max_length=20, required=False)
    favorite_company = forms.IntegerField(required=True)

    def clean_username(self):
        username = self.cleaned_data.get('username')
        email = self.data['email']
        queryset = User.objects.filter(~Q(email=email), username=username)
        if queryset:
            raise forms.ValidationError(username + " - This username already exist.")
        elif len(username) < 4:
            raise forms.ValidationError("Your username must be at least 4 characters long.")
        elif len(username) > 20:
            raise forms.ValidationError("Your username is too long.")
        elif email_check(username):
            raise forms.ValidationError("Username can not use email address.")

        return username

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'telephone', 'favorite_company']


class QuoteUserForm(forms.Form):
    username = forms.CharField(max_length=20, required=True)
    email = forms.EmailField(max_length=80, required=True)
    password = forms.CharField(label='Password', widget=forms.PasswordInput, required=True)
    re_password = forms.CharField(required=True, widget=forms.PasswordInput, )
    first_name = forms.CharField(max_length=20, required=False)
    last_name = forms.CharField(max_length=20, required=False)
    telephone = forms.CharField(max_length=20, required=False)
    booking_system = forms.BooleanField(required=False)
    quote_system = forms.BooleanField(required=False)

    def clean_booking_system(self):
        get_booking_system = self.cleaned_data.get("booking_system")
        get_quote_system = self.data.get("quote_system")
        if not get_booking_system and not get_quote_system:
            raise forms.ValidationError('one SYSTEM must be selected.')
        return get_booking_system

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) < 8:
            raise forms.ValidationError('Your password is too short at least 8 characters')
        elif len(password) > 20:
            raise forms.ValidationError('Your password is too long, Max length is 20 characters')

    def clean_re_password(self):
        password1 = self.data.get('password')
        password2 = self.cleaned_data.get('re_password')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Password mismatch. Please enter again.")

        return password2

    def clean_username(self):
        username = self.cleaned_data.get('username')

        if email_check(username):
            raise forms.ValidationError("Username can not use email address.")
        elif len(username) < 4:
            raise forms.ValidationError("Username must be at least 4 characters long.")
        elif len(username) > 20:
            raise forms.ValidationError("Username is too long.")
        else:
            filter_result = User.objects.filter(username__exact=username)
            if len(filter_result) > 0:
                raise forms.ValidationError("Username already exists.")

        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')

        if email_check(email):
            filter_result = User.objects.filter(email__exact=email)
            if len(filter_result) > 0:
                raise forms.ValidationError("Your email already exists.")
        else:
            raise forms.ValidationError("Please enter a valid email.")

        return email


class SlotUserUpdateForm(forms.ModelForm):
    username = forms.CharField(max_length=20, required=True)
    first_name = forms.CharField(max_length=20, required=False)
    last_name = forms.CharField(max_length=20, required=False)
    telephone = forms.CharField(max_length=20, required=False)
    favorite_company = forms.IntegerField(required=True)

    def clean_username(self):
        username = self.cleaned_data.get('username')
        email = self.data['email']
        queryset = User.objects.filter(~Q(email=email), username=username)
        if queryset:
            raise forms.ValidationError(username + " - This username already exist.")
        elif len(username) < 4:
            raise forms.ValidationError("Your username must be at least 4 characters long.")
        elif len(username) > 20:
            raise forms.ValidationError("Your username is too long.")
        elif email_check(username):
            raise forms.ValidationError("Username can not use email address.")
        return username

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'telephone', ]


class SlotUserForm(forms.Form):
    username = forms.CharField(max_length=20, required=True)
    email = forms.EmailField(max_length=80, required=True)
    password = forms.CharField(label='Password', widget=forms.PasswordInput, required=True)
    re_password = forms.CharField(widget=forms.PasswordInput, required=True)
    first_name = forms.CharField(max_length=20, required=False)
    last_name = forms.CharField(max_length=20, required=False)
    telephone = forms.CharField(max_length=20, required=False)
    email_group = forms.CharField(max_length=200, required=True)
    role = forms.IntegerField(required=True)
    status = forms.IntegerField(required=True)

    def clean_password(self):
        password = self.cleaned_data.get('password')

        if len(password) < 8:
            raise forms.ValidationError('Your password is too short at least 8 characters')
        elif len(password) > 20:
            raise forms.ValidationError('Your password is too long, Max length is 20 characters.')

    def clean_re_password(self):
        password1 = self.data.get('password')
        password2 = self.cleaned_data.get('re_password')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Password mismatch. Please enter again.")

        return password2

    def clean_username(self):
        username = self.cleaned_data.get('username')

        if len(username) < 4:
            raise forms.ValidationError("Your username must be at least 4 characters long.")
        elif len(username) > 20:
            raise forms.ValidationError("Your username is too long.")
        elif email_check(username):
            raise forms.ValidationError("Username can not use email address.")
        else:
            filter_result = User.objects.filter(username__exact=username)
            if len(filter_result) > 0:
                raise forms.ValidationError("Your username already exists.")

        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')

        if email_check(email):
            filter_result = User.objects.filter(email__exact=email)
            if len(filter_result) > 0:
                raise forms.ValidationError("Your email already exists.")
        else:
            raise forms.ValidationError("Please enter a valid email.")

        return email
