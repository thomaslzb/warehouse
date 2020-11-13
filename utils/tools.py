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
