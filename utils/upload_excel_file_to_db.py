#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   upload_file_temp.py    
@Contact :   thomaslzb@hotmail.com
@License :   (C)Copyright 2020-2022, Zibin Li

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
17/04/2021 10:25   lzb       1.0         None
"""
import datetime

import pandas as pd
import numpy as np
import pymysql
import xlrd

INSERT_SQL = "INSERT INTO flc_price_list " \
                 "(destination, destination_type, " \
                 "begin_date, expire_date, " \
                 "date_type, price, " \
                 "company_code_id, port_code_id, container_id, " \
                 "op_datetime, op_user_id) " \
                 "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"


# 连接的 MYSQL 数据库
def connect_remote_db():
    # 远程数据库的配置
    IP_ADDRESS = '127.0.0.1'
    DATABASE_NAME = "ukdcg"
    DATABASE_USERNAME = "ukdcg"
    DATABASE_PWD = "ukthomas"
    connect = pymysql.connect(host=IP_ADDRESS,
                              user=DATABASE_USERNAME,
                              password=DATABASE_PWD,
                              database=DATABASE_NAME,
                              cursorclass=pymysql.cursors.DictCursor)

    return connect


def insert_sql_many(db_connects, sql, data):
    """
    :param db_connects: database
    :param data: value
    :param sql: update sql
    :return: cursor
    """
    cursor = db_connects.cursor()
    # try:
    cursor.fast_executemany = True
    cursor.executemany(sql, data)
    db_connects.commit()
    # print('Save DB Successfully......')
    # except:
    #     db_connects.rollback()
    #     print('Save DB Error......')
    cursor.close()


def upload_excel_file(input_file_name):
    # 处理 Excel 文件
    print('read file....')
    excel_data = xlrd.open_workbook(filename=input_file_name)
    print('get data....')
    table = excel_data.sheet_by_index(0)

    n_rows = table.nrows
    print('get data index....'+str(n_rows))
    get_data_list = []
    begin_date = datetime.datetime.strptime('2020.01.01', '%Y.%m.%d').date()
    expire_date = datetime.datetime.strptime('2020.04.30', '%Y.%m.%d').date()
    company_code = 'CMA-CGM'
    for i in range(4, n_rows):
        rowValues = table.row_values(i)

        city = rowValues[0].strip() + " - " + rowValues[1].strip()
        # GB-SOU
        get_data_list.append((city, 'CITY', begin_date, expire_date, 'Pickup Date', rowValues[2], company_code,
                              'SOU', 2, datetime.datetime.now(), 1))

        get_data_list.append((city, 'CITY', begin_date, expire_date, 'Pickup Date', rowValues[3], company_code,
                              'SOU', 9, datetime.datetime.now(), 1))
        get_data_list.append((city, 'CITY', begin_date, expire_date, 'Pickup Date', rowValues[4], company_code,
                              'SOU', 10, datetime.datetime.now(), 1))

        # GB-FXT
        get_data_list.append((city, 'CITY', begin_date, expire_date, 'Pickup Date', rowValues[5], company_code,
                              'FXT', 2, datetime.datetime.now(), 1))
        get_data_list.append((city, 'CITY', begin_date, expire_date, 'Pickup Date', rowValues[6], company_code,
                              'FXT', 9, datetime.datetime.now(), 1))
        get_data_list.append((city, 'CITY', begin_date, expire_date, 'Pickup Date', rowValues[7], company_code,
                              'FXT', 10, datetime.datetime.now(), 1))

        # GB-TIL
        get_data_list.append((city, 'CITY', begin_date, expire_date, 'Pickup Date', rowValues[8], company_code,
                              'TIL', 2, datetime.datetime.now(), 1))
        get_data_list.append((city, 'CITY', begin_date, expire_date, 'Pickup Date', rowValues[9], company_code,
                              'TIL', 9, datetime.datetime.now(), 1))
        get_data_list.append((city, 'CITY', begin_date, expire_date, 'Pickup Date', rowValues[10], company_code,
                              'TIL', 10, datetime.datetime.now(), 1))

        # GB-LGP
        get_data_list.append((city, 'CITY', begin_date, expire_date, 'Pickup Date', rowValues[11], company_code,
                              'LGP', 2, datetime.datetime.now(), 1))
        get_data_list.append((city, 'CITY', begin_date, expire_date, 'Pickup Date', rowValues[12], company_code,
                              'LGP', 9, datetime.datetime.now(), 1))
        get_data_list.append((city, 'CITY', begin_date, expire_date, 'Pickup Date', rowValues[13], company_code,
                              'LGP', 10, datetime.datetime.now(), 1))
    return get_data_list


if __name__ == "__main__":
    print('begin loading file.....')
    connect_db = connect_remote_db()
    print('begin insert DB......')
    file_name = 'C:\DCG\EXCEL Develop\Import Haulage Tariff  Base ports Valid Q1 April 2021 09042021up-converted.xlsx'
    data_list = upload_excel_file(file_name)
    if data_list:
        connect_db = connect_remote_db()
        print('begin insert DB......')
        insert_sql_many(connect_db, INSERT_SQL, data_list)
    print('finished.....')
