#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   tools.py    
@Contact :   thomaslzb@hotmail.com
@License :   (C)Copyright 2020-2022, Zibin Li

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
12/10/2020 13:48   lzb       1.0         None
"""
import re
import time


def exchange_string(s):
    """
    将字符串中的空格，转换成为下划线
    """
    # Remove all non-word characters (everything except numbers and letters)
    s = re.sub(r"[^\w\s]", '', s)

    # Replace all runs of whitespace with a single dash
    s = re.sub(r"\s+", '-', s)

    return s


def is_float(numstr):
    """
     字符串是否是浮点数(整数算小数)
    """
    flag = False
    numStr = str(numstr).strip().lstrip('-').lstrip('+')  # 去除正数(+)、负数(-)符号
    try:
        numFloat = float(numstr)
        flag = True
    except:
        flag = False
    return flag


def format_postcode(postcode):
    postcode = postcode.strip().upper()
    if len(postcode) > 3:
        postcode = postcode[0:len(postcode) - 3].strip() + \
                   " " + postcode[len(postcode) - 3:len(postcode)]
    return postcode


def run_timer(func):
    """
    统计某函数运行多长时间的装饰器
    :param func: 函数体
    :return:
    """
    def wrapper(*args, **kwargs):
        start = time.time()
        ret_value = func(*args, **kwargs)
        end = time.time()
        used = end - start
        print(f'{func.__name__} used {used}')
        return ret_value
    return wrapper

