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
from .models import UserProfile
from captcha.fields import CaptchaField

PROFIT_MODE = [(0, 'By Percent'), (1, 'By Fix Amount')]


def email_check(email):
    pattern = re.compile(r"\"?([-a-zA-Z0-9.`?{}]+@\w+\.\w+)\"?")
    return re.match(pattern, email)


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
            filter_result = User.objects.filter(email__exact=username)
            if not filter_result:
                raise forms.ValidationError("This username does not exist. Please register first.")

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
        if len(password1) < 6:
            raise forms.ValidationError("Your password is too short.")
        elif len(password1) > 20:
            raise forms.ValidationError("Your password is too long.")

        return password1

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Password mismatch. Please enter again.")

        return password2


class ForgetPwdForm(forms.Form):
    email = forms.CharField(required=True, error_messages={"required": "Please input the correct email address"})
    # captcha = CaptchaField(error_messages={'invalid': '验证码错误'})


class ModifyPwdForm(forms.Form):
    old_password = forms.CharField(label='Old Password', widget=forms.PasswordInput)
    password1 = forms.CharField(label='New Password', widget=forms.PasswordInput, required=True)
    password2 = forms.CharField(required=True, widget=forms.PasswordInput, min_length=8)

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')

        if len(password1) < 8:
            raise forms.ValidationError('Your password is too short')
        elif len(password1) > 20:
            raise forms.ValidationError('Your password is too long')

        return password1

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Password mismatch. Please enter again.")

        return password2


class MyProfileForm(forms.ModelForm):
    # GROUP_CHOICES = [(-1, '[Choose]')]
    # GROUP_CHOICES += [(group.id, group.name.capitalize()) for group in auth.models.Group.objects.all()]
    #
    # group = forms.ChoiceField(
    #     label='Group',
    #     choices=GROUP_CHOICES
    # )
    #
    # def clean_group(self):
    #     if self.cleaned_data['group'] != -1:
    #         return self.cleaned_data['group']
    #     else:
    #         raise forms.ValidationError('Please, choose a group')
    username = forms.CharField(max_length=20, required=True)
    first_name = forms.CharField(max_length=20, required=False)
    last_name = forms.CharField(max_length=20, required=False)
    telephone = forms.CharField(max_length=20, required=False)
    profit_mode = forms.ChoiceField(label='profit_mode', choices=PROFIT_MODE, required=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'telephone', 'profit_mode']

