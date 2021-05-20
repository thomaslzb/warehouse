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

import datetime
from random import Random
from django.core.mail import send_mail

from users.models import EmailVerifyRecord
from warehouse.settings import EMAIL_FROM
from utils.record_log import get_logger
from users.models import SlotEmailGroup, UserProfile


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


# send_type
# 操作员：Inbound :  Delivery Manifest
#                   OP Form
#        Outbound: Delivery Note
# 仓库： 状态变更：   Arrived
#                   Finished
#       上传文件：Inbound: Breakdown
#                         Parcel List
#                         Delivery POD
#
#                Outbound: Paperwork

def system_sendmail(ref, op_name, file_list, email_to, send_type, position, ):
    user_mail_group = SlotEmailGroup.objects.filter(to_email_group__user__username=op_name,
                                                    position__exact=position,
                                                    )
    if user_mail_group:
        group_mail = user_mail_group[0].email.strip()
        if len(group_mail) != 0:
            email_to.append(group_mail)
        else:
            email_to.append('ecom.dpt@dcg-uk.co.uk')
            email_to.append('cmwarehouse.dpt@dcg-uk.co.uk')
            email_to.append('transport@dcg-uk.co.uk')
    today_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%I")
    if send_type == "Delivery Manifest":
        subject = 'DOCS Uploaded: CM-Inbound Delivery Manifest' + ' Ref:(   ' + ref + '    ) Op:' + op_name
        email_body = 'Dear Warehouse Team: \n\r'
        email_body += 'Operator(   ' + op_name + '   ) has uploaded documents for Ref(   ' + ref + \
                      '   ) in the System: \n\n'
    elif send_type == "OP Form":
        subject = 'DOCS Uploaded: CM-Inbound OP Form' + ' Ref:(   ' + ref + '   ) Op:' + op_name
        email_body = 'Dear Warehouse Team: \n\r'
        email_body += 'Operator(   ' + op_name + '   ) has uploaded documents for Ref(   ' + ref + \
                      '   ) in the System: \n\n'
    elif send_type == "Delivery Note":
        subject = 'DOCS Uploaded: CM-Outbound Delivery Note' + ' Ref:(   ' + ref + '   ) Op:' + op_name
        email_body = 'Dear Warehouse Team: \n\r'
        email_body += 'Operator(   ' + op_name + '   ) has uploaded documents for Ref(   ' + ref + \
                      '   ) in the System: \n\n'
    elif send_type == "Arrived":
        subject = 'Ref: (   ' + ref + '   ) has just arrive, '
        email_body = 'Dear ' + op_name + ': \n\r'
        email_body += '(    ' + ref + '    ) has arrived at CM Warehouse in -----  ' + today_now + '   -----'
        email_body += ', you will receive another email once the vehicle been tipped. \n\n'
    elif send_type == "Finished":
        subject = 'Ref: (   ' + ref + '    ) has finished'
        email_body = 'Dear ' + op_name + ': \n\r'
        email_body += '(   ' + ref + '   ) has finished at CM Warehouse on ----   ' + today_now + '   ----'
        email_body += ', thank you.\n\n'
    elif send_type == "Breakdown":
        subject = 'Inbound Breakdown for (    ' + ref + '   ) has uploaded'
        email_body = 'Dear E-commerce Team: \n\r'
        email_body += 'Inbound Breakdown for (   ' + ref + '    ) has uploaded in the system on ----    '\
                      + today_now + '---- '
        email_body += ', you can now check the docs by click on the ref.\n\n'
    elif send_type == "Parcel List":
        subject = 'Inbound Parcel List for (    ' + ref + '   ) has uploaded'
        email_body = 'Dear E-commerce Team: \n\r'
        email_body += 'Inbound Parcel List for (   ' + ref + '    ) has uploaded in the system on ----    ' \
                      + today_now + '---- '
        email_body += ', you can now check the docs by click on the ref.\n\n'
    elif send_type == "Delivery POD":
        subject = 'Inbound Delivery POD for (    ' + ref + '   ) has uploaded'
        email_body = 'Dear E-commerce Team: \n\r'
        email_body += 'Inbound Delivery POD for (   ' + ref + '    ) has uploaded in the system on ----    ' \
                      + today_now + '---- '
        email_body += ', you can now check the docs by click on the ref.\n\n'
    else:
        send_type == "Paperwork"
        subject = 'Documents for Outbound (   ' + ref + '   ) has uploaded'
        email_body = 'Dear ' + op_name + ': \n\r'
        email_body += 'Outbound paperwork for (    ' + ref + '    ) has uploaded in the system on ----   '\
                      + today_now + '    -----'
        email_body += ', you can now check the docs by click on the ref.\n\n'

    for file_list_name in file_list:
        email_body += '           ' + file_list_name + '\n'

    email_footer = '\n'
    email_footer += 'Please check detail in the System. Thank you. \n\n'
    email_footer += 'Slot Booking System Notification.\n'
    email_footer += 'Please do not reply, this email will not be monitored. \n'
    email_footer += 'Please contact relevant operators regarding any queries.\n'

    email_title = subject
    email_body = email_body + email_footer

    try:
        send_status = send_mail(email_title, email_body, EMAIL_FROM, email_to)
        if send_status:
            pass
    except:
        # logger = get_logger()
        #  logger.debug('send_mail is wrong EMAIL_FROM ' + EMAIL_FROM)
        print('send_mail is wrong EMAIL_FROM')
