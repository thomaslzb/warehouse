#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   email_send.py    
@Contact :   thomaslzb@hotmail.com
@License :   (C)Copyright 2020-2022, Zibin Li

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
13/08/2020 15:00   lzb       1.0         None
"""

# !/usr/bin/python3.6
# -*-coding:utf-8-*-
from random import Random
from django.core.mail import send_mail

from users import EmailVerifyRecord
from warehouse.settings import EMAIL_FROM


def random_string(randomlength=8):
    str = ""
    chars = "AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789"
    length = len(chars) - 1
    random = Random()
    for i in range(randomlength):
        str += chars[random.randint(0, length)]
    return str


def send_register_email(e_mail, send_type="register"):
    rendom_code = random_string(16)

    emailrecord = EmailVerifyRecord()
    emailrecord.email = e_mail
    emailrecord.code = rendom_code
    emailrecord.send_type = send_type
    emailrecord.save()

    if send_type == "register":
        email_title = "Lzb Online Course Register Testing Mail"
        email_body = "Click here http://127.0.0.1:8000/active/{0}".format(rendom_code)
        send_status = send_mail(email_title, email_body, EMAIL_FROM, [e_mail])
        if send_status:
            pass
    elif send_type == "forget":
            email_title = "Lzb Online Course Reset Password Testing Mail"
            email_body = "Click here http://127.0.0.1:8000/password_reset/{0}".format(rendom_code)
            send_status = send_mail(email_title, email_body, EMAIL_FROM, [e_mail])
            if send_status:
                pass

