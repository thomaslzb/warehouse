# -*- coding: utf-8 -*-

import datetime
import decimal
import os

import numpy as np
import pandas as pd
import xlrd
import xlwt
from xlwt import Formula, XFStyle
from xlwt.Utils import rowcol_to_cell
import math

from decimal import Decimal
from django.db import transaction
from django.db.models import Q, Max, Min, Sum
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.views import View
from django.views.generic import ListView, CreateView

from menu.views import get_user_grant_list
from xiaomi.calc_bill_function import calc_dcg_bill
from xiaomi.forms import CalcDcgUpsBillForm, FuelSurchargeForm
from xiaomi.models import MiAccountBillDetailModel, MiAccountBillMainModel, DPDMainBillModel, DPDBillDetailModel, \
    RentalPriceModel, FLCTempModel, FLCTempCounterModel
from xiaomi.models import RentalBillModel, RentalBillDetailModel
from xiaomi.models import DcgBillDetailTotalModel, DcgBillDetailHandleModel, DcgBillDetailUPSModel
from xiaomi.models import DcgBillDetailDPDModel, FuelSurchargeModel, DPDCongestionPostcodeModel
from xiaomi.models import UpsMainBillModel, UpsBillDetailModel, DcgBillModel
from xiaomi.models import PostcodeModel, CalculateItemModel, SpecialItemModel

MI_UPLOAD_PROGRESS_NUMBER = 0

MENU_ACTIVE = "XIAOMI"
EACH_PAGE = 13


def valid_file(file_name, file_type, display_error=""):
    error = ''
    try:
        # 通过文件的后缀名，判断选择的文件是否是excel文件
        if not file_name.name.split('.')[-1].upper() in file_type:
            error = display_error
    except:
        error = 'Must selected a file to upload.'
    return error


# 小米账单主表列表
class MiBillMainListView(ListView):
    ordering = ["bill_year", "bill_month", ]
    model = MiAccountBillMainModel
    template_name = 'mi_bill_main_list.html'
    paginate_by = EACH_PAGE

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_active'] = MENU_ACTIVE
        context['page_tab'] = 1
        context['menu_grant'] = get_user_grant_list(self.request.user.id)
        context['bill_year'] = int(self.request.GET.get('bill_year', datetime.datetime.now().strftime('%Y')))
        return context

    def get_queryset(self):
        query_bill_year = int(self.request.GET.get('bill_year', datetime.datetime.now().strftime('%Y')))
        result = MiAccountBillMainModel.objects.filter(bill_year=query_bill_year, ).order_by('bill_year', '-bill_month')

        return result


# 小米账单明细列表
class MiBillDetailListView(ListView):
    ordering = ["bill_year", "bill_month", "mi_code", "finished_datetime"]
    model = MiAccountBillDetailModel
    template_name = 'mi_bill_detail_list.html'
    paginate_by = EACH_PAGE

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_active'] = MENU_ACTIVE
        context['page_tab'] = 1
        context['menu_grant'] = get_user_grant_list(self.request.user.id)
        context['mi_code'] = self.request.GET.get('mi_code', '')
        context['ups_code'] = self.request.GET.get('ups_code', '')
        context['postcode'] = self.request.GET.get('postcode', '')
        context['express_company'] = self.request.GET.get('express_company', 'ALL')
        context['is_delivery_checked'] = int(self.request.GET.get('is_delivery_checked', '-1'))
        context['bill_year'] = int(self.kwargs['pk'])
        context['bill_month'] = int(self.kwargs['slug'])
        return context

    def get_queryset(self):
        query_mi_code = self.request.GET.get('mi_code', '')
        query_ups_code = self.request.GET.get('ups_code', '')
        query_postcode = self.request.GET.get('postcode', '')
        query_express_company = self.request.GET.get('express_company', 'ALL')
        query_is_checked = int(self.request.GET.get('is_delivery_checked', '-1'))
        if query_express_company == 'ALL':
            query_express_company = ""
        if query_is_checked != -1:
            result = MiAccountBillDetailModel.objects.filter(mi_code__icontains=query_mi_code,
                                                             parcel_id__icontains=query_ups_code,
                                                             postcode__icontains=query_postcode,
                                                             express_company__icontains=query_express_company,
                                                             delivery_fee_checked=query_is_checked,
                                                             )
        else:
            result = MiAccountBillDetailModel.objects.filter(mi_code__icontains=query_mi_code,
                                                             parcel_id__icontains=query_ups_code,
                                                             postcode__icontains=query_postcode,
                                                             express_company__icontains=query_express_company,
                                                             )

        return result


# 仓租费账单主表列表
class RentalBillMainListView(ListView):
    ordering = ["bill_year", "bill_month", ]
    model = RentalBillModel
    template_name = 'rental_main_list.html'
    paginate_by = EACH_PAGE

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_active'] = MENU_ACTIVE
        context['page_tab'] = 7
        context['menu_grant'] = get_user_grant_list(self.request.user.id)
        context['bill_year'] = int(self.request.GET.get('bill_year', datetime.datetime.now().strftime('%Y')))
        return context

    def get_queryset(self):
        query_bill_year = int(self.request.GET.get('bill_year', datetime.datetime.now().strftime('%Y')))
        result = RentalBillModel.objects.filter(bill_year=query_bill_year, ).order_by('bill_year', '-bill_month')

        return result


# 仓租费账单明细列表
class RentalDetailListView(ListView):
    ordering = ["bill_date", "sku", ]
    model = RentalBillDetailModel
    template_name = 'rental_detail_list.html'
    paginate_by = EACH_PAGE

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_active'] = MENU_ACTIVE
        context['page_tab'] = 7
        context['menu_grant'] = get_user_grant_list(self.request.user.id)
        context['sku'] = self.request.GET.get('sku', '')
        context['goods_id'] = self.request.GET.get('goods_id', '')

        return context

    def get_queryset(self):
        query_sku = self.request.GET.get('sku', '')
        query_goods_id = self.request.GET.get('goods_id', '')
        date_filter = self.request.GET.get('range_date_filter', '')

        if date_filter:
            begin_date = datetime.datetime.strptime(date_filter[0:10], '%Y-%m-%d')
            end_date = datetime.datetime.strptime(date_filter[13:23], '%Y-%m-%d')
            result = RentalBillDetailModel.objects.filter(sku__icontains=query_sku,
                                                          goods_id__icontains=query_goods_id,
                                                          bill_date__range=(begin_date, end_date),
                                                          )
        else:
            result = RentalBillDetailModel.objects.filter(sku__icontains=query_sku,
                                                          goods_id__icontains=query_goods_id,
                                                          )

        return result


# UPS账单主表列表
class UPSBillMainListView(ListView):
    ordering = ["bill_year", "bill_month", ]
    model = UpsMainBillModel
    template_name = 'ups_bill_main_list.html'
    paginate_by = EACH_PAGE

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_active'] = MENU_ACTIVE
        context['page_tab'] = 2
        context['menu_grant'] = get_user_grant_list(self.request.user.id)
        context['bill_year'] = int(self.request.GET.get('bill_year', datetime.datetime.now().strftime('%Y')))
        context['bill_month'] = int(self.request.GET.get('bill_month', '0'))
        context['ups_bill_no'] = self.request.GET.get('ups_bill_no', '')
        return context

    def get_queryset(self):
        query_ups_bill_no = self.request.GET.get('ups_bill_no', '')
        query_bill_year = int(self.request.GET.get('bill_year', datetime.datetime.now().strftime('%Y')))
        query_bill_month = int(self.request.GET.get('bill_month', '0'))
        if query_bill_month == 0:
            result = UpsMainBillModel.objects.filter(bill_date__year=query_bill_year,
                                                     ups_bill_no__icontains=query_ups_bill_no,
                                                     ).order_by('-bill_date')
        else:
            result = UpsMainBillModel.objects.filter(bill_date__year=query_bill_year,
                                                     bill_date__month=query_bill_month,
                                                     ups_bill_no__icontains=query_ups_bill_no,
                                                     ).order_by('-bill_date')
        return result


# UPS账单明细表列表
class UPSBillDetailListView(ListView):
    ordering = ["bill_date", "parcel_id", "delivery_date", 'fee_code', ]
    model = UpsBillDetailModel
    template_name = 'ups_bill_detail_list.html'
    paginate_by = EACH_PAGE

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_active'] = MENU_ACTIVE
        context['page_tab'] = 2
        context['menu_grant'] = get_user_grant_list(self.request.user.id)
        context['mi_code'] = self.request.GET.get('mi_code', '')
        context['ups_code'] = self.request.GET.get('ups_code', '')
        context['ups_bill_no'] = self.kwargs['pk']
        context['fee_desc'] = self.request.GET.get('fee_desc', '')
        return context

    def get_queryset(self):
        query_mi_code = self.request.GET.get('mi_code', '')
        query_ups_code = self.request.GET.get('ups_code', '')
        query_fee_desc = self.request.GET.get('fee_desc', '')
        result = UpsBillDetailModel.objects.filter(mi_code__icontains=query_mi_code,
                                                   parcel_id__icontains=query_ups_code,
                                                   fee_desc__icontains=query_fee_desc,
                                                   )

        return result


# DPD 账单主表列表
class DPDBillMainListView(ListView):
    ordering = ["bill_date", "dpd_account_no", "dpd_invoice_no", ]
    model = UpsMainBillModel
    template_name = 'dpd_bill_main_list.html'
    paginate_by = EACH_PAGE

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_active'] = MENU_ACTIVE
        context['page_tab'] = 3
        context['menu_grant'] = get_user_grant_list(self.request.user.id)
        context['bill_year'] = int(self.request.GET.get('bill_year', datetime.datetime.now().strftime('%Y')))
        context['bill_month'] = int(self.request.GET.get('bill_month', '0'))
        context['dpd_invoice_no'] = self.request.GET.get('dpd_invoice_no', '')
        return context

    def get_queryset(self):
        query_dpd_invoice_no = self.request.GET.get('dpd_invoice_no', '')
        query_bill_year = int(self.request.GET.get('bill_year', datetime.datetime.now().strftime('%Y')))
        query_bill_month = int(self.request.GET.get('bill_month', '0'))
        if query_bill_month == 0:
            result = DPDMainBillModel.objects.filter(bill_date__year=query_bill_year,
                                                     dpd_invoice_no__icontains=query_dpd_invoice_no,
                                                     ).order_by('-bill_date')
        else:
            result = DPDMainBillModel.objects.filter(bill_date__year=query_bill_year,
                                                     bill_date__month=query_bill_month,
                                                     dpd_invoice_no__icontains=query_dpd_invoice_no,
                                                     ).order_by('-bill_date')
        return result


# DPD 账单明细表列表
class DPDBillDetailListView(ListView):
    ordering = ["bill_date", "dpd_account_no", "dpd_invoice_no", 'parcel_id', ]
    model = DPDBillDetailModel
    template_name = 'dpd_bill_detail_list.html'
    paginate_by = EACH_PAGE

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_active'] = MENU_ACTIVE
        context['page_tab'] = 3
        context['menu_grant'] = get_user_grant_list(self.request.user.id)
        context['mi_code'] = self.request.GET.get('mi_code', '')
        context['parcel_id'] = self.request.GET.get('parcel_id', '')
        context['qty'] = self.request.GET.get('qty', '')
        context['revenue'] = self.request.GET.get('revenue', '')
        context['qty_compare'] = self.request.GET.get('qty_compare', 'less than')
        context['revenue_compare'] = self.request.GET.get('revenue_compare', 'less than')
        return context

    def get_queryset(self):
        query_mi_code = self.request.GET.get('mi_code', '')
        query_parcel_id = self.request.GET.get('parcel_id', '')
        try:
            query_qty = Decimal(self.request.GET.get('qty', 0))
        except:
            query_qty = 0
        try:
            query_revenue = Decimal(self.request.GET.get('revenue', 0))
        except:
            query_revenue = 0
        query_qty_compare = self.request.GET.get('qty_compare', '')
        query_revenue_compare = self.request.GET.get('revenue_compare', '')
        if query_qty == 0 and query_revenue == 0:
            result = DPDBillDetailModel.objects.filter(mi_code__icontains=query_mi_code,
                                                       parcel_id__icontains=query_parcel_id,
                                                       )
        else:
            if query_revenue != 0:
                if query_revenue_compare == 'more than':
                    result = DPDBillDetailModel.objects.filter(mi_code__icontains=query_mi_code,
                                                               parcel_id__icontains=query_parcel_id,
                                                               revenue__gt=query_revenue,
                                                               )
                elif query_revenue_compare == 'less than':
                    result = DPDBillDetailModel.objects.filter(mi_code__icontains=query_mi_code,
                                                               parcel_id__icontains=query_parcel_id,
                                                               revenue__lt=query_revenue,
                                                               )
                else:
                    result = DPDBillDetailModel.objects.filter(mi_code__icontains=query_mi_code,
                                                               parcel_id__icontains=query_parcel_id,
                                                               revenue=query_revenue,
                                                               )
            else:
                if query_qty_compare == 'more than':
                    result = DPDBillDetailModel.objects.filter(mi_code__icontains=query_mi_code,
                                                               parcel_id__icontains=query_parcel_id,
                                                               qty__gt=query_qty,
                                                               )
                elif query_qty_compare == 'less than':
                    result = DPDBillDetailModel.objects.filter(mi_code__icontains=query_mi_code,
                                                               parcel_id__icontains=query_parcel_id,
                                                               qty__lt=query_qty,
                                                               )
                else:
                    result = DPDBillDetailModel.objects.filter(mi_code__icontains=query_mi_code,
                                                               parcel_id__icontains=query_parcel_id,
                                                               qty=query_qty,
                                                               )

        return result


# DPD 文件上传
class DPDFileUploadView(View):
    def get(self, request):
        return render(request, 'dpd_files_upload.html', {
            'menu_active': MENU_ACTIVE,
            'menu_grant': get_user_grant_list(request.user.id),
            'page_tab': 3,
        })

    def post(self, request):
        global MI_UPLOAD_PROGRESS_NUMBER
        dpd_error = ""
        file_name = ""
        dpd_account_no = request.POST['dpd_account_no'].strip()
        dpd_invoice_no = request.POST['dpd_invoice_no'].strip()
        input_string = dpd_account_no + "." + dpd_invoice_no
        try:
            file_name = request.FILES['file_name']

            dpd_queryset = DPDMainBillModel.objects.filter(dpd_account_no=dpd_account_no, dpd_invoice_no=dpd_invoice_no)
            if dpd_queryset:  # 判断同一文件不能反复上传
                dpd_error = "This DPD bill " + input_string + "has been uploaded."

            error = valid_file(file_name, ['CSV'], "This is not a csv file. Please select a CSV file.")
        except:
            error = "Please select a CSV file."
        if not error:
            # 文件名，必须和输入的一致
            if input_string != os.path.splitext(file_name.name)[0]:
                error = file_name.name + ' - File name is not match with the DPD Bill Account No. or Invoice No.- ' \
                        + input_string
        if error or dpd_error:
            return render(request, 'dpd_files_upload.html', {
                'menu_active': MENU_ACTIVE,
                'menu_grant': get_user_grant_list(request.user.id),
                'error': error,
                'ups_error': dpd_error,
                'dpd_account_no': dpd_account_no,
                'dpd_invoice_no': dpd_invoice_no,
                'page_tab': 2,
            })
        if error or dpd_error:
            return render(request, 'dpd_files_upload.html', {
                'menu_active': MENU_ACTIVE,
                'menu_grant': get_user_grant_list(request.user.id),
                'error': error,
                'ups_error': dpd_error,
                'dpd_account_no': dpd_account_no,
                'dpd_invoice_no': dpd_invoice_no,
                'page_tab': 2,
            })

        # 从第 6 行开始读入数据
        invoice_value = 0
        data = pd.read_csv(file_name, dtype=str, header=4)
        data = data.replace(np.nan, '', regex=True)  # 过滤到nan
        data_index = data.index
        dpd_insert_sql = []
        MI_UPLOAD_PROGRESS_NUMBER = 0
        for i in data_index:
            rowValues = data.values[i]
            MI_UPLOAD_PROGRESS_NUMBER = int((i / data_index.size) * 100)
            change_empty = lambda the_number: the_number if the_number != "" else 0
            bill_date = datetime.datetime.strptime(rowValues[0], '%d/%m/%Y')
            if float(change_empty(rowValues[13])) != 0:
                dpd_insert_sql.append(DPDBillDetailModel(bill_date=bill_date,
                                                         dpd_account_no=dpd_account_no,
                                                         dpd_invoice_no=dpd_invoice_no,
                                                         parcel_id=rowValues[1].strip(),
                                                         product_code=int(rowValues[2].strip()),
                                                         product_description=rowValues[3].strip(),
                                                         service_code=int(rowValues[4].strip()),
                                                         service_description=rowValues[5].strip(),
                                                         mi_code=rowValues[11].strip(),
                                                         weight=float(change_empty(rowValues[13])),
                                                         qty=float(change_empty(rowValues[13])),
                                                         revenue=float(change_empty(rowValues[15])),
                                                         fuel_surcharge=float(change_empty(rowValues[17])),
                                                         third_party_collection=float(change_empty(rowValues[18])),
                                                         fourth_party_collection=float(change_empty(rowValues[19])),
                                                         congestion=float(change_empty(rowValues[20])),
                                                         eu_clearance=float(change_empty(rowValues[21])),
                                                         return_charge=float(change_empty(rowValues[22])),
                                                         failed_collection=float(change_empty(rowValues[23])),
                                                         scottish_zone=float(change_empty(rowValues[24])),
                                                         tax_prepaid=float(change_empty(rowValues[25])),
                                                         handling=float(change_empty(rowValues[26])),
                                                         contractual_liability=float(change_empty(rowValues[27])),
                                                         oversize_exports=float(change_empty(rowValues[28])),
                                                         unsuccessful_eu_export=float(change_empty(rowValues[29])),
                                                         eu_export_return=float(change_empty(rowValues[30])),
                                                         op_user_id=self.request.user.id,
                                                         op_datetime=datetime.datetime.now(),
                                                         ))
                invoice_value += float(change_empty(rowValues[15])) + float(change_empty(rowValues[17])) + float(
                    change_empty(rowValues[18])) + float(change_empty(rowValues[19])) + float(
                    change_empty(rowValues[20])) + float(
                    change_empty(rowValues[21])) + float(change_empty(rowValues[22])) + float(
                    change_empty(rowValues[23])) + float(
                    change_empty(rowValues[24])) + float(change_empty(rowValues[25])) + float(
                    change_empty(rowValues[26])) + float(
                    change_empty(rowValues[27])) + float(change_empty(rowValues[28])) + float(
                    change_empty(rowValues[29])) + float(
                    change_empty(rowValues[30]))

        if dpd_insert_sql:
            with transaction.atomic():
                vat_value = invoice_value * 0.2  # 20% 的增值税
                gross_value = invoice_value + vat_value
                DPDMainBillModel.objects.create(bill_date=bill_date,
                                                dpd_account_no=dpd_account_no,
                                                dpd_invoice_no=dpd_invoice_no,
                                                record_num=data_index.size,
                                                invoice_value=invoice_value,
                                                vat=vat_value,
                                                gross_invoice_value=gross_value,
                                                op_user_id=self.request.user.id,
                                                op_datetime=datetime.datetime.now(),
                                                )
                DPDBillDetailModel.objects.bulk_create(dpd_insert_sql)
        return HttpResponseRedirect(reverse('xiaomi:dpd_bill_list_main'))


def change_to_datetime(value):
    if value == '':
        value = 0
    if isinstance(value, float) or isinstance(value, int):
        value = timezone.make_aware(xlrd.xldate.xldate_as_datetime(value, 0),
                                    timezone.get_current_timezone())
    if isinstance(value, str):
        value = datetime.datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
    return value


# 上传小米 excel 账单的函数
def mi_upload_excel_file_task(self, table, bill_year, bill_month):
    global MI_UPLOAD_PROGRESS_NUMBER

    n_rows = table.nrows
    # 小米明细账单
    MI_UPLOAD_PROGRESS_NUMBER = 0
    insert_sql_list = []
    express_company = 'UPS'
    for i in range(1, n_rows):
        # 这里的参数是给前台progress bar调用的
        MI_UPLOAD_PROGRESS_NUMBER = int((i / n_rows) * 100)

        rowValues = table.row_values(i)
        ready_datetime = change_to_datetime(rowValues[10])

        if rowValues[8]:
            if isinstance(rowValues[8], str):
                ready_datetime = datetime.datetime.strptime(rowValues[8], "%Y-%m-%d %H:%M:%S")
            if isinstance(rowValues[8], float):
                ready_datetime = timezone.make_aware(xlrd.xldate.xldate_as_datetime(rowValues[8], 0),
                                                     timezone.get_current_timezone())

        if rowValues[12]:
            total_qty = int(rowValues[12])
        else:
            total_qty = 0
        if rowValues[13]:
            weight = rowValues[13]
        else:
            weight = 0
        if rowValues[3].upper().find('UPS') != -1:
            express_company = "UPS"
        if rowValues[3].upper().find('DPD') != -1:
            express_company = "DPD"

        string_mi_code = rowValues[0]
        mi_code = ""
        for char in string_mi_code:
            if char != '=' and char != '"':
                mi_code += ''.join(char)

        insert_sql_list.append(MiAccountBillDetailModel(bill_year=bill_year,
                                                        bill_month=bill_month,
                                                        mi_code=mi_code,
                                                        package_code=rowValues[1],
                                                        parcel_id=rowValues[2],
                                                        express_company=express_company,
                                                        country='GB',
                                                        county=rowValues[4],
                                                        town=rowValues[5],
                                                        postcode=rowValues[6],
                                                        ready_datetime=ready_datetime,
                                                        goods_id=rowValues[11],
                                                        total_qty=total_qty,
                                                        weight=weight,
                                                        delivery_fee_checked=0,
                                                        update_bill_year=0,
                                                        update_bill_month=0,
                                                        op_user_id=self.request.user.id,
                                                        op_datetime=datetime.datetime.now(),
                                                        ))

    # 批量写入数据库
    with transaction.atomic():
        # 小米主账单
        MiAccountBillMainModel.objects.create(bill_year=bill_year,
                                              bill_month=bill_month,
                                              record_num=n_rows - 1,
                                              is_used=0,
                                              op_user_id=self.request.user.id,
                                              op_datetime=datetime.datetime.now(),
                                              )
        MiAccountBillDetailModel.objects.bulk_create(insert_sql_list)

    MI_UPLOAD_PROGRESS_NUMBER = 99
    return JsonResponse(MI_UPLOAD_PROGRESS_NUMBER, safe=False)


# 上传小米账单
class MiFileUploadView(View):
    def get(self, request):
        bill_year = int(datetime.datetime.now().strftime('%Y'))
        bill_month = int(datetime.datetime.now().strftime('%m'))
        return render(request, 'mi_bill_upload.html', {
            'menu_active': MENU_ACTIVE,
            'menu_grant': get_user_grant_list(request.user.id),
            'bill_year': bill_year,
            'bill_month': bill_month,
            'page_tab': 1,
        })

    def post(self, request):
        error = ""
        file_name = ""
        bill_year = request.POST['bill_year']
        bill_month = request.POST['bill_month']
        try:
            file_name = request.FILES['file_name']
            query_bill = MiAccountBillMainModel.objects.filter(bill_year=bill_year, bill_month=bill_month)
            if query_bill:
                if int(bill_month) > 9:
                    error = str(bill_year) + "-" + str(bill_month) + " bill has been uploaded."
                else:
                    error = str(bill_year) + "-0" + str(bill_month) + " bill has been uploaded."
        except:
            error = "Please select a excel file."

        if not error:
            error = valid_file(file_name, ['XLS', 'XLSX', ], "Please select a excel file.")
        if error:
            return render(request, 'mi_bill_upload.html', {
                'menu_active': MENU_ACTIVE,
                'menu_grant': get_user_grant_list(request.user.id),
                'error': error,
                'page_tab': 1,
                'bill_year': int(bill_year),
                'bill_month': int(bill_month),
            })

        if file_name.name.split('.')[-1].upper() in ['XLS', 'XLSX']:
            # 处理 Excel 文件
            excel_data = xlrd.open_workbook(filename=None, file_contents=file_name.read())
            table = excel_data.sheet_by_index(0)
            # mi_upload_excel_file_task(self, table, bill_year, bill_month)
            try:
                mi_upload_excel_file_task(self, table, bill_year, bill_month)
            except:
                error = 'Uploading file failure. There are some error in the uploading Files '
                return render(request, 'mi_bill_upload.html', {
                    'menu_active': MENU_ACTIVE,
                    'menu_grant': get_user_grant_list(request.user.id),
                    'bill_year': int(bill_year),
                    'bill_month': int(bill_month),
                    'error': error,
                    'page_tab': 1,
                })

        return HttpResponseRedirect(reverse('xiaomi:mi_bill_list_main'))


# 上传 rental excel 账单的函数
def rental_upload_excel_file_task(self, table, bill_year, bill_month, fee_unit_price):
    global MI_UPLOAD_PROGRESS_NUMBER

    n_rows = table.nrows
    MI_UPLOAD_PROGRESS_NUMBER = 0
    insert_sql_list = []
    fee_total = 0
    for i in range(1, n_rows):
        # 这里的参数是给前台progress bar调用的
        MI_UPLOAD_PROGRESS_NUMBER = int((i / n_rows) * 100)

        rowValues = table.row_values(i)
        bill_date = str(int(rowValues[6]))
        bill_date = datetime.datetime.strptime(bill_date, "%Y%m%d")

        unit_volume = Decimal(rowValues[7])
        qty = Decimal(rowValues[8])
        total_volume = unit_volume * qty
        fee_subtotal = total_volume * fee_unit_price
        fee_total += fee_subtotal
        insert_sql_list.append(RentalBillDetailModel(bill_date=bill_date,
                                                     sku=rowValues[2],
                                                     goods_id=str(int(rowValues[3])),
                                                     unit_volume=unit_volume,
                                                     qty=qty,
                                                     pallet_qty=rowValues[9],
                                                     total_volume=total_volume,
                                                     fee_unit=fee_unit_price,
                                                     fee_total=fee_subtotal,
                                                     op_user_id=self.request.user.id,
                                                     op_datetime=datetime.datetime.now(),
                                                     ))

    # 批量写入数据库
    with transaction.atomic():
        # 仓租费主账单
        RentalBillModel.objects.create(bill_year=bill_year,
                                       bill_month=bill_month,
                                       record_num=n_rows - 1,
                                       fee_unit=fee_unit_price,
                                       fee_total=fee_total,
                                       op_user_id=self.request.user.id,
                                       op_datetime=datetime.datetime.now(),
                                       )
        # 仓租费明细账单
        RentalBillDetailModel.objects.bulk_create(insert_sql_list)

    MI_UPLOAD_PROGRESS_NUMBER = 99
    return JsonResponse(MI_UPLOAD_PROGRESS_NUMBER, safe=False)


# 上传仓租费账单
class RentalFileUploadView(View):
    def get(self, request):
        bill_year = int(datetime.datetime.now().strftime('%Y'))
        bill_month = int(datetime.datetime.now().strftime('%m'))
        return render(request, 'rental_bill_upload.html', {
            'menu_active': MENU_ACTIVE,
            'menu_grant': get_user_grant_list(request.user.id),
            'bill_year': bill_year,
            'bill_month': bill_month,
            'page_tab': 7,
        })

    def post(self, request):
        error = ""
        file_name = ""
        bill_year = int(request.POST['bill_year'])
        bill_month = int(request.POST['bill_month'])
        try:
            file_name = request.FILES['file_name']
            query_bill = RentalBillModel.objects.filter(bill_year=bill_year, bill_month=bill_month)
            if query_bill:
                if bill_month > 9:
                    error = str(bill_year) + "-" + str(bill_month) + " bill has been uploaded."
                else:
                    error = str(bill_year) + "-0" + str(bill_month) + " bill has been uploaded."
        except:
            error = "Please select a excel file."

        if not error:
            error = valid_file(file_name, ['XLS', 'XLSX', ], "Please select a excel file.")
        if error:
            return render(request, 'rental_bill_upload.html', {
                'menu_active': MENU_ACTIVE,
                'menu_grant': get_user_grant_list(request.user.id),
                'error': error,
                'page_tab': 7,
                'bill_year': bill_year,
                'bill_month': bill_month,
            })

        if file_name.name.split('.')[-1].upper() in ['XLS', 'XLSX']:
            # 处理 Excel 文件
            excel_data = xlrd.open_workbook(filename=None, file_contents=file_name.read())
            table = excel_data.sheet_by_index(0)
            fee_unit_price = RentalPriceModel.objects.all()[0].fee_unit
            # rental_upload_excel_file_task(self, table, bill_year, bill_month, fee_unit_price)
            try:
                rental_upload_excel_file_task(self, table, bill_year, bill_month, fee_unit_price)
            except:
                error = 'Uploading file failure. There are some error in the uploading Files '
                return render(request, 'rental_bill_upload.html', {
                    'menu_active': MENU_ACTIVE,
                    'menu_grant': get_user_grant_list(request.user.id),
                    'error': error,
                    'page_tab': 7,
                    'bill_year': bill_year,
                    'bill_month': bill_month,
                })

        return HttpResponseRedirect(reverse('xiaomi:rental_list_main'))


def get_max_int(number):
    str_number = str(number)
    if str_number[-1] == '0':
        return number
    new_number = int(number / 10) + 1
    number = new_number * 10
    return number


# 显示仓租费的直方图
class RentalDailyChart(View):
    def get(self, request):
        bill_year = int(request.GET.get('year', 0))
        bill_month = int(request.GET.get('month', 0))
        queryset = RentalBillDetailModel.objects.values('bill_date').annotate(sub_total=Sum('fee_total')) \
            .order_by('bill_date')
        max_min = queryset.aggregate(Max('sub_total'))
        max_value = get_max_int(math.ceil(int(max_min['sub_total__max'])))
        y_axis = [max_value, int(max_value * 4 / 5), int(max_value * 3 / 5), int(max_value * 2 / 5),
                  int(max_value * 1 / 5), 0]
        data_list = [(datetime.datetime.strftime(item['bill_date'], '%d'),
                      str("{:.2f}".format(round(item['sub_total'], 2))),
                      str("{:.0%}".format(item['sub_total'] / max_value)))
                     for item in queryset]

        return render(request, 'rental_month_charts.html', {'y_axis': y_axis,
                                                            'data_list': data_list,
                                                            'menu_active': MENU_ACTIVE,
                                                            'menu_grant': get_user_grant_list(request.user.id),
                                                            'page_tab': 7,
                                                            'bill_year': bill_year,
                                                            'bill_month': bill_month,
                                                            })


# 返回进度条 的 进度
def show_progress(request):
    return JsonResponse(MI_UPLOAD_PROGRESS_NUMBER, safe=False)


# 上传 UPS 账单
class UPSFileUploadView(View):
    def get(self, request):
        return render(request, 'ups_files_upload.html', {
            'menu_active': MENU_ACTIVE,
            'menu_grant': get_user_grant_list(request.user.id),
            'page_tab': 2,
        })

    def post(self, request):
        global MI_UPLOAD_PROGRESS_NUMBER
        ups_error = ""
        file_name = ""
        ups_bill_no = request.POST['ups_bill_no']
        try:
            file_name = request.FILES['file_name']

            ups_bill_no_queryset = UpsMainBillModel.objects.filter(ups_bill_no__exact=ups_bill_no)
            if ups_bill_no_queryset:  # 判断同一文件不能反复上传
                ups_error = "This ups bill " + ups_bill_no + " has been uploaded."

            error = valid_file(file_name, ['CSV'], "This is not a csv file. Please select a CSV file.")
        except:
            error = "Please select a CSV file."
        if not error:
            # 文件名，必须和输入的一致
            if ups_bill_no != os.path.splitext(file_name.name)[0]:
                error = file_name.name + ' - File name is not match with the UPS Bill No. - ' + ups_bill_no
        if error or ups_error:
            return render(request, 'ups_files_upload.html', {
                'menu_active': MENU_ACTIVE,
                'menu_grant': get_user_grant_list(request.user.id),
                'error': error,
                'ups_error': ups_error,
                'ups_bill_no': ups_bill_no,
                'page_tab': 2,
            })

        data = pd.read_csv(file_name, dtype=str)
        data = data.replace(np.nan, '', regex=True)  # 过滤到nan
        data_index = data.index

        total_bill_amount = 0
        ups_insert_detail_sql = []
        MI_UPLOAD_PROGRESS_NUMBER = 0
        for i in data_index:
            MI_UPLOAD_PROGRESS_NUMBER = int((i / data_index.size) * 100)
            rowValues = data.values[i]
            bill_date = datetime.datetime.strptime(rowValues[4], '%Y-%m-%d')
            delivery_date = datetime.datetime.strptime(rowValues[11], '%Y-%m-%d')
            if rowValues[13]:  # parcel_id 不为空，则导入
                total_bill_amount += decimal.Decimal(rowValues[52])
                ups_insert_detail_sql.append(UpsBillDetailModel(ups_bill_no=ups_bill_no,
                                                                mi_code=rowValues[15],
                                                                parcel_id=rowValues[13],
                                                                bill_date=bill_date,
                                                                delivery_date=delivery_date,
                                                                fee_code=rowValues[43],
                                                                fee_desc=rowValues[45],
                                                                fee_currency=rowValues[50],
                                                                fee_amount=float(rowValues[52]),
                                                                is_use=0,
                                                                op_user_id=self.request.user.id,
                                                                op_datetime=datetime.datetime.now(),
                                                                ))

        if ups_insert_detail_sql:
            bill_date = datetime.datetime.strptime(data.values[1][4], '%Y-%m-%d')
            with transaction.atomic():
                # 导入UPS 账单的账单
                UpsMainBillModel.objects.create(bill_date=bill_date,
                                                ups_bill_no=ups_bill_no,
                                                record_num=data_index.size,
                                                total_amount=total_bill_amount,
                                                op_user_id=self.request.user.id,
                                                op_datetime=datetime.datetime.now(),
                                                )
                UpsBillDetailModel.objects.bulk_create(ups_insert_detail_sql)
        return HttpResponseRedirect(reverse('xiaomi:ups_bill_list_main'))


class DCGBillListView(ListView):
    ordering = ["bill_year", "bill_month", ]
    model = DcgBillModel
    template_name = 'dcg_bill_list.html'
    paginate_by = EACH_PAGE

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_active'] = MENU_ACTIVE
        context['page_tab'] = 4
        context['menu_grant'] = get_user_grant_list(self.request.user.id)
        context['bill_year'] = int(self.request.GET.get('bill_year', datetime.datetime.now().strftime('%Y')))
        context['bill_month'] = int(self.request.GET.get('bill_month', 0))
        return context

    def get_queryset(self):
        query_bill_year = int(self.request.GET.get('bill_year', datetime.datetime.now().strftime('%Y')))
        query_bill_month = int(self.request.GET.get('bill_month', 0))
        if query_bill_month != 0:
            result = DcgBillModel.objects.filter(bill_year=query_bill_year,
                                                 bill_month=query_bill_month,
                                                 ).order_by('bill_year', '-bill_month', )
        else:
            result = DcgBillModel.objects.filter(bill_year=query_bill_year,
                                                 ).order_by('bill_year', '-bill_month', )

        return result


# 计算 DCG 的账单
class CalcDcgUpsBillCreateView(CreateView):
    model = DcgBillModel
    form_class = CalcDcgUpsBillForm
    template_name = 'dcg_bill_calculation.html'
    success_url = '/xiaomi/dcg-list/'

    def form_valid(self, form):
        bill_year = int(self.request.POST['bill_year'])
        bill_month = int(self.request.POST['bill_month'])

        # 计算 DCG 的账单，并更新数据库
        calc_dcg_bill(self, bill_year, bill_month)
        self.object = form.save(commit=False)
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        response = super().form_invalid(form)
        if self.request.accepts('text/html'):
            return response

    def get_initial(self, *args, **kwargs):
        initial = super(CalcDcgUpsBillCreateView, self).get_initial()
        initial["bill_year"] = int(self.request.GET.get('bill_year', datetime.datetime.now().strftime('%Y')))
        initial['bill_month'] = int(self.request.GET.get('bill_month', datetime.datetime.now().strftime('%m')))

        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_tab'] = 4
        context['menu_grant'] = get_user_grant_list(self.request.user.id)
        context['bill_year'] = int(self.request.GET.get('bill_year', datetime.datetime.now().strftime('%Y')))
        context['bill_month'] = int(self.request.GET.get('bill_month', datetime.datetime.now().strftime('%m')))

        return context


# 显示 DCG-UK 账单明细
class DCGBillDetailListView(ListView):
    ordering = ["bill_year", "bill_month", "item_type", "item"]
    model = DcgBillDetailTotalModel
    template_name = 'dcg_bill_detail_display.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_active'] = MENU_ACTIVE
        context['page_tab'] = 4
        context['menu_grant'] = get_user_grant_list(self.request.user.id)
        context['bill_year'] = int(self.kwargs['pk'])
        context['bill_month'] = int(self.kwargs['slug'])

        delivery_ups_count = DcgBillDetailTotalModel.objects.filter(express_company='UPS',
                                                                    bill_year=int(self.kwargs['pk']),
                                                                    bill_month=int(self.kwargs['slug']),
                                                                    ).count()
        delivery_dpd_count = DcgBillDetailTotalModel.objects.filter(express_company='DPD',
                                                                    bill_year=int(self.kwargs['pk']),
                                                                    bill_month=int(self.kwargs['slug']),
                                                                    ).count()
        queryset = DcgBillModel.objects.filter(bill_year=int(self.kwargs['pk']),
                                               bill_month=int(self.kwargs['slug']),
                                               )
        total_package_ups = 0
        total_package_dpd = 0
        total_package_handle = 0
        for record in queryset:
            if record.express_company == 'UPS':
                total_package_ups = record.total_record
            if record.express_company == 'DPD':
                total_package_dpd = record.total_record
            if record.express_company == 'DCG':
                total_package_handle = record.total_record
        context['delivery_ups_count'] = delivery_ups_count + delivery_dpd_count
        context['delivery_dpd_count'] = delivery_dpd_count
        context['total_package_ups'] = total_package_ups
        context['total_package_dpd'] = total_package_dpd
        context['total_package_handle'] = total_package_handle

        return context

    def get_queryset(self):
        query_bill_year = int(self.kwargs['pk'])
        query_bill_month = int(self.kwargs['slug'])
        result = DcgBillDetailTotalModel.objects.filter(bill_year=query_bill_year,
                                                        bill_month=query_bill_month,
                                                        ).order_by('item_type', 'express_company', 'display_order', )
        return result


# 显示 Delivery Item 价格设置明细
class ItemDeliveryListView(ListView):
    ordering = ["item_type", "order_by", ]
    model = CalculateItemModel
    template_name = 'item_delivery_display.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_active'] = MENU_ACTIVE
        context['page_tab'] = 5
        context['menu_grant'] = get_user_grant_list(self.request.user.id)
        context['express_company'] = self.kwargs['pk']
        if self.kwargs['pk'] == "UPS":
            zone1 = 'ZONE1'
            zone2 = 'ZONE2'
        else:
            zone1 = 'ZONE_UK'
            zone2 = 'OFFSHORE'

        zone1_count = CalculateItemModel.objects.filter(item_type='Delivery', zone=zone1,
                                                        item__icontains="Standard Delivery Fee",
                                                        express_company=self.kwargs['pk'],
                                                        ).count()
        zone2_count = CalculateItemModel.objects.filter(item_type='Delivery', zone=zone2,
                                                        item__icontains="Standard Delivery Fee",
                                                        express_company=self.kwargs['pk'],
                                                        ).count()
        context['zone1_count'] = zone1_count
        context['zone2_count'] = zone2_count
        return context

    def get_queryset(self):
        if self.kwargs['pk'] == 'UPS':
            result = CalculateItemModel.objects.filter(item_type='Delivery',
                                                       item__icontains="Standard Delivery Fee",
                                                       express_company=self.kwargs['pk'],
                                                       ).order_by('item_type', 'zone', 'order_by')
        else:
            result = CalculateItemModel.objects.filter(item_type='Delivery',
                                                       express_company=self.kwargs['pk'],
                                                       ).order_by('item_type', 'zone', 'item', 'order_by')

        return result


# 显示 Handle Item 价格设置明细
class ItemHandleListView(ListView):
    ordering = ["item_type", "order_by", ]
    model = CalculateItemModel
    template_name = 'item_handle_display.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_active'] = MENU_ACTIVE
        context['page_tab'] = 5
        context['menu_grant'] = get_user_grant_list(self.request.user.id)

        return context

    def get_queryset(self):
        result = CalculateItemModel.objects.filter(item_type='Handle',
                                                   ).order_by('item_type', 'order_by')
        return result


# 显示 Special Item 明细
class ItemSpecialListView(ListView):
    ordering = ["item_code", ]
    model = SpecialItemModel
    template_name = 'item_special_item_display.html'
    paginate_by = EACH_PAGE

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_active'] = MENU_ACTIVE
        context['page_tab'] = 5
        context['menu_grant'] = get_user_grant_list(self.request.user.id)

        return context

    def get_queryset(self):
        result = SpecialItemModel.objects.all().order_by('item_code', )
        return result


# 显示 Zone Item 明细
class ItemZoneListView(ListView):
    model = PostcodeModel
    template_name = 'item_zone_display.html'
    paginate_by = EACH_PAGE

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_active'] = MENU_ACTIVE
        context['page_tab'] = 5
        context['menu_grant'] = get_user_grant_list(self.request.user.id)
        context['express_company'] = self.kwargs['pk']

        return context

    def get_queryset(self):
        result = PostcodeModel.objects.filter(express_company=self.kwargs['pk']) \
            .order_by('express_company', 'postcode_begin', )
        return result


# 显示 Congestion Zone Item 明细
class CongestionZoneListView(ListView):
    model = DPDCongestionPostcodeModel
    template_name = 'item_zone_display.html'
    paginate_by = EACH_PAGE

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_active'] = MENU_ACTIVE
        context['page_tab'] = 5
        context['menu_grant'] = get_user_grant_list(self.request.user.id)
        context['express_company'] = self.kwargs['pk']

        return context

    def get_queryset(self):
        result = DPDCongestionPostcodeModel.objects.filter(express_company=self.kwargs['pk']) \
            .order_by('express_company', 'postcode_begin', )
        return result


def write_excel(wb, sheet_name, head_list, data_list, style_list=None,
                sum_formula_list=None, total_list=None, sub_cost=None):
    # sum_formula_list: [col, col1, col2, col3...], [col, col1, col2, col3...]
    # 创建表,第一页
    if style_list is None:
        style_list = []
    if sum_formula_list is None:
        sum_formula_list = []
    if total_list is None:
        total_list = []
    if sub_cost is None:
        sub_cost = []

    ws = wb.add_sheet(sheet_name)

    row_num = 0
    font_style = XFStyle()
    # 二进制
    font_style.font.bold = True
    # 表头内容
    columns = head_list
    # 写进表头内容
    for col_num in range(len(head_list)):
        ws.write(row_num, col_num, columns[col_num], font_style)
    # Sheet body, remaining rows
    font_style = XFStyle()

    # 获取数据库数据
    rows = data_list

    # 转换时间
    rows = [[x.strftime("%Y-%m-%d %H:%M") if isinstance(x, datetime.datetime) else x for x in row] for row in
            rows]
    # 遍历提取出来的内容
    for row in rows:
        row_num += 1
        # 逐行写入Excel
        for col_num in range(len(row)):
            if style_list:
                font_style.num_format_str = style_list[col_num]

            write_formula = False
            formula = ""
            i = 0
            for col in sum_formula_list:
                i += 1
                if i == 1 and col_num != col:
                    write_formula = False
                    break
                if i == 1 and col_num == col:
                    write_formula = True

                if write_formula:
                    sum_col = rowcol_to_cell(row_num, col)
                    if i != 1:
                        formula = formula + sum_col + '+'

            if formula:
                formula = formula[:-1]

            if col_num in sub_cost:
                if col_num == sub_cost[0]:
                    write_formula = True
                    formula = rowcol_to_cell(row_num, col_num - 2) + "+" + rowcol_to_cell(row_num, col_num - 1)

                if col_num == sub_cost[1]:
                    write_formula = True
                    formula = rowcol_to_cell(row_num, col_num - 4) + '-' + rowcol_to_cell(row_num, col_num - 2)

            if write_formula:
                ws.write(row_num, col_num, Formula(formula), style=font_style)
            else:
                ws.write(row_num, col_num, row[col_num], style=font_style)
    row = len(rows) + 1
    for col in total_list:
        if style_list:
            font_style.num_format_str = style_list[col]
        formula = 'SUM(' + rowcol_to_cell(1, col) \
                  + ':' + rowcol_to_cell(len(rows), col) + ')'
        ws.write(row, col, Formula(formula), style=font_style)

    return wb


# 将数据库的数据下载成为excel文件, 不带成本
def loadfile(request, bill_year, bill_month):
    # 指定数据类型
    response = HttpResponse(content_type='application/ms-excel')
    if int(bill_month) < 10:
        bill_month = '0' + bill_month
    file_name = 'DCG-Bill-' + bill_year + '-' + bill_month + '.xls'
    # 设置文件名称
    response['Content-Disposition'] = 'attachment; filename="' + file_name + '"'
    # 创建工作簿
    wb = xlwt.Workbook(encoding='utf-8')

    sheet_name = 'Total'
    head_list = ['year', 'month', 'company', 'last month Package Count', 'this month Package Count', 'Total Records',
                 'Total Amount']
    style_list = ['####', '0#', '', '#,##0', '#,##0', '#,##0', '#,##0.00']
    total_list = [6, ]
    # 获取账单的 total 数据库数据
    data_list = DcgBillModel.objects.filter(bill_year=int(bill_year), bill_month=int(bill_month)). \
        values_list('bill_year',
                    'bill_month',
                    'express_company',
                    'last_month_record',
                    'this_month_record',
                    'total_record',
                    'total_amount',
                    )

    wb = write_excel(wb, sheet_name, head_list, data_list, style_list, '', total_list)

    # 获取账单的sub total
    sheet_name = 'Total_Detail'
    head_list = ['Fee-Type', 'Company', 'Item_description', 'Item_Pcs', 'Records', ]
    style_list = ['', '', '', '#,##0', '#,##0', ]
    # 获取数据库数据
    data_list = DcgBillDetailTotalModel.objects.filter(~Q(item__icontains='cost'),
                                                       bill_year=int(bill_year),
                                                       bill_month=int(bill_month),
                                                       ) \
        .values_list('item_type', 'express_company', 'item', 'qty', 'record_num', )

    wb = write_excel(wb, sheet_name, head_list, data_list, style_list)

    # 获取账单的Rental Fee
    sheet_name = 'Rental Fee'
    head_list = ['Bill_Year', 'Bill_Month', 'Record_Number', 'Price', 'Rental_Amount', ]
    style_list = ['####', '0#', '#,##0', '#,##0.00', '#,##0.00']
    # 获取数据库数据
    data_list = RentalBillModel.objects.filter(bill_year=int(bill_year),
                                               bill_month=int(bill_month),
                                               ) \
        .values_list('bill_year', 'bill_month', 'record_num', 'fee_unit', 'fee_total')

    wb = write_excel(wb, sheet_name, head_list, data_list, style_list, )

    # 获取账单的明细 Handle 费用
    sheet_name = 'Handle_Fee_Detail'
    head_list = ['Bill_Year', 'Bill_Month', 'Mi_Code', 'Package_Code', 'Express_Company', 'Parcel_Id', 'Goods_Id',
                 'Postcode', 'Ready_Datetime', 'Total_PCs', 'Weight',
                 'Handle_Fee', 'ExtraHandle_Fee', 'SpecialItem_Fee', 'Package_Fee', 'Total_Amount', ]
    style_list = ['####', '0#', '', '', '', '', '',
                  '', '', '#,##0', '#,##0.0000',
                  '#,##0.00', '#,##0.00', '#,##0.00', '#,##0.00', '#,##0.00', ]
    sum_formula_list = [15, 11, 12, 13, 14, ]
    total_list = [11, 12, 13, 14, 15]

    # 获取数据库数据
    data_list = DcgBillDetailHandleModel.objects.filter(bill_year=int(bill_year), bill_month=int(bill_month)) \
        .values_list('bill_year', 'bill_month', 'mi_code', 'package_code', 'express_company', 'parcel_id', 'goods_id',
                     'postcode', 'ready_datetime', 'total_qty', 'weight',
                     'handle_fee', 'extra_handle_fee', 'special_item_fee', 'package_fee',
                     'total_amount', )

    wb = write_excel(wb, sheet_name, head_list, data_list, style_list, sum_formula_list, total_list)

    # 获取账单的明细 UPS 费用
    sheet_name = 'UPS_Delivery_Fee_Detail'
    head_list = ['Bill_Year', 'Bill_Month', 'Mi_Code', 'Package_Code', 'Express_Company', 'Parcel_Id', 'Goods_Id',
                 'Postcode', 'ready_datetime', 'Total_Qty', 'Weight', 'Standard_Delivery_fee', 'Residential',
                 'Dom_Standard_Undeliverable_Return', 'Uk_Border_Fee', 'Additional_Handling',
                 'Peak_Surcharge_Additional_Handling', 'Address_Correction_Dom_Standard',
                 'extended_area_surcharge_destination', 'Fuel_Surcharge_Rate', 'Fuel_Surcharge', 'Total_Amount',
                 'Update_Year', 'Update_Month', ]
    style_list = ['####', '0#', '', '', '', '', '', '', '', '#,##0', '#,##0.0000',
                  '#,##0.00', '#,##0.00', '#,##0.00', '#,##0.00', '#,##0.00', '#,##0.00',
                  '#,##0.00', '#,##0.00', '#,##0.00', '#,##0.00', '#,##0.00', '####', '0#']
    sum_formula_list = [21, 11, 12, 13, 14, 15, 16, 17, 18, 20]
    total_list = [11, 12, 13, 14, 15, 16, 17, 18, 20, 21, ]

    # 获取数据库数据
    data_list = DcgBillDetailUPSModel.objects.filter(update_year=int(bill_year), update_month=int(bill_month)) \
        .values_list('bill_year', 'bill_month', 'mi_code', 'package_code', 'express_company', 'parcel_id', 'goods_id',
                     'postcode', 'ready_datetime', 'total_qty', 'weight',
                     'standard_delivery_fee', 'residential', 'dom_standard_undeliverable_return',
                     'uk_border_fee', 'additional_handling', 'peak_surcharge_additional_handling',
                     'address_correction_dom_standard', 'extended_area_surcharge_destination',
                     'fuel_surcharge_rate', 'fuel_surcharge', 'total_amount',
                     'update_year', 'update_month', )

    wb = write_excel(wb, sheet_name, head_list, data_list, style_list, sum_formula_list, total_list)

    # 获取账单的明细 DPD 费用
    sheet_name = 'DPD_Delivery_Fee_Detail'
    head_list = ['Bill_Year', 'Bill_Month', 'Mi_Code', 'Package_Code', 'Express_Company', 'Parcel_Id', 'Goods_Id',
                 'Postcode', 'ready_datetime', 'Total_Qty', 'Weight',
                 'Standard_Delivery_fee', 'Additional_Fee', 'Fuel_Surcharge_Rate',
                 'Fuel_Surcharge', 'Total_Amount', 'Update_Year', 'Update_Month', ]
    style_list = ['####', '0#', '', '', '', '', '', '', '', '#,##0', '#,##0.0000',
                  '#,##0.00', '#,##0.00', '#,##0.00', '#,##0.00', '#,##0.00', '####', '0#']
    sum_formula_list = [15, 11, 12, 14]
    total_list = [11, 12, 14, 15]

    data_list = DcgBillDetailDPDModel.objects.filter(update_year=int(bill_year), update_month=int(bill_month)) \
        .values_list('bill_year', 'bill_month', 'mi_code', 'package_code', 'express_company', 'parcel_id', 'goods_id',
                     'postcode', 'ready_datetime', 'total_qty', 'weight', 'standard_delivery_fee',
                     'additional_fee', 'fuel_surcharge_rate',
                     'fuel_surcharge', 'total_amount', 'update_year', 'update_month', )

    wb = write_excel(wb, sheet_name, head_list, data_list, style_list, sum_formula_list, total_list)

    # 获取账单中没有结算快递费用的的明细
    sheet_name = 'unCalc_Delivery_Fee_Detail'
    head_list = ['Bill_Year', 'Bill_Month', 'Mi_Code', 'Package_Code', 'Express_Company', 'Parcel_Id', 'Goods_Id',
                 'Postcode', 'ready_datetime', 'Total_Qty', 'Weight', ]
    style_list = ['####', '0#', '', '', '', '', '',
                  '', '', '#,##0', '#,##0.0000', ]

    data_list = MiAccountBillDetailModel.objects.filter(delivery_fee_checked=0,
                                                        bill_year__lte=int(bill_year),
                                                        bill_month__lte=int(bill_month), ) \
        .values_list('bill_year', 'bill_month', 'mi_code', 'package_code', 'express_company', 'parcel_id', 'goods_id',
                     'postcode', 'ready_datetime', 'total_qty', 'weight', )

    wb = write_excel(wb, sheet_name, head_list, data_list, style_list)

    wb.save(response)
    return response


# 将数据库的数据下载成为excel文件, 带成本
def loadfile_with_cost(request, bill_year, bill_month):
    # 指定数据类型
    response = HttpResponse(content_type='application/ms-excel')
    if int(bill_month) < 10:
        bill_month = '0' + bill_month
    file_name = 'DCG-Bill-With-Cost' + bill_year + '-' + bill_month + '.xls'
    # 设置文件名称
    response['Content-Disposition'] = 'attachment; filename="' + file_name + '"'
    # 创建工作簿
    wb = xlwt.Workbook(encoding='utf-8')

    sheet_name = 'Total'
    head_list = ['year', 'month', 'company', 'last month Package Count', 'this month Package Count',
                 'Total Records', 'Total Amount', 'Nett Cost', 'Total VAT', 'Total Cost', 'Total Profit']
    style_list = ['####', '0#', '', '#,##0', '#,##0', '#,##0', '#,##0.00', '#,##0.00', '#,##0.00',
                  '#,##0.00', '#,##0.00']
    total_list = [6, 7, 8, 9, 10]

    # 获取账单的 total 数据库数据
    data_list = DcgBillModel.objects.filter(bill_year=int(bill_year), bill_month=int(bill_month)). \
        values_list('bill_year',
                    'bill_month',
                    'express_company',
                    'last_month_record',
                    'this_month_record',
                    'total_record',
                    'total_amount',
                    'nett_cost',
                    'total_vat',
                    'total_cost',
                    'total_profit',
                    )

    wb = write_excel(wb, sheet_name, head_list, data_list, style_list, '', total_list)

    # 获取账单的sub total
    sheet_name = 'Total_Detail'
    head_list = ['Fee-Type', 'Company', 'Item_description', 'Item_Pcs', 'Records', 'unit_price', 'sub_total']
    style_list = ['', '', '', '#,##0', '#,##0', '#,##0.00', '#,##0.00']
    # 获取数据库数据
    data_list = DcgBillDetailTotalModel.objects.filter(~Q(item__icontains='cost'),
                                                       bill_year=int(bill_year),
                                                       bill_month=int(bill_month),
                                                       ) \
        .values_list('item_type', 'express_company', 'item', 'qty', 'record_num', 'unit_price', 'sub_total_amount')

    wb = write_excel(wb, sheet_name, head_list, data_list, style_list)

    # 获取账单的Rental Fee
    sheet_name = 'Rental Fee'
    head_list = ['Bill_Year', 'Bill_Month', 'Record_Number', 'Price', 'Rental_Amount', ]
    style_list = ['####', '0#', '#,##0', '#,##0.00', '#,##0.00']
    # 获取数据库数据
    data_list = RentalBillModel.objects.filter(bill_year=int(bill_year),
                                               bill_month=int(bill_month),
                                               ) \
        .values_list('bill_year', 'bill_month', 'record_num', 'fee_unit', 'fee_total')

    wb = write_excel(wb, sheet_name, head_list, data_list, style_list, )

    # 获取账单的明细 Handle 费用
    sheet_name = 'Handle_Fee_Detail'
    head_list = ['Bill_Year', 'Bill_Month', 'Mi_Code', 'Package_Code', 'Express_Company', 'Parcel_Id', 'Goods_Id',
                 'Postcode', 'ready_datetime', 'Total_Qty', 'Weight',
                 'Handle_Fee', 'ExtraHandle_Fee', 'SpecialItem_Fee', 'Package_Fee', 'Total_Amount', ]
    style_list = ['####', '0#', '', '', '', '', '', '', '', '#,##0', '#,##0.0000',
                  '#,##0.00', '#,##0.00', '#,##0.00', '#,##0.00', '#,##0.00', ]

    sum_formula_list = [15, 11, 12, 13, 14, ]
    total_list = [11, 12, 13, 14, 15]
    # 获取数据库数据
    data_list = DcgBillDetailHandleModel.objects.filter(bill_year=int(bill_year), bill_month=int(bill_month)) \
        .values_list('bill_year', 'bill_month', 'mi_code', 'package_code', 'express_company', 'parcel_id', 'goods_id',
                     'postcode', 'ready_datetime', 'total_qty', 'weight',
                     'handle_fee', 'extra_handle_fee', 'special_item_fee', 'package_fee',
                     'total_amount', )

    wb = write_excel(wb, sheet_name, head_list, data_list, style_list, sum_formula_list, total_list)

    # 获取账单的明细 UPS 费用
    sheet_name = 'UPS_Delivery_Fee_Detail'
    head_list = ['Bill_Year', 'Bill_Month', 'Mi_Code', 'Package_Code', 'Express_Company', 'Parcel_Id', 'Goods_Id',
                 'Postcode', 'ready_datetime', 'Total_Qty', 'Weight',
                 'Standard_Delivery_fee', 'Residential', 'Dom_Standard_Undeliverable_Return',
                 'Uk_Border_Fee', 'Additional_Handling', 'Peak_Surcharge_Additional_Handling',
                 'Address_Correction_Dom_Standard', 'extended_area_surcharge_destination',
                 'Fuel_Surcharge_Rate', 'Fuel_Surcharge', 'Total_Amount',
                 'VAT', 'Nett Cost', 'Total Cost', 'Nett Profit', 'Update_Year', 'Update_Month', 'Express_Bill_No.', ]

    style_list = ['####', '0#', '', '', '', '', '', '', '', '#,##0', '#,##0.0000',
                  '#,##0.00', '#,##0.00', '#,##0.00', '#,##0.00', '#,##0.00', '#,##0.00',
                  '#,##0.00', '#,##0.00', '#,##0.00', '#,##0.00', '#,##0.00', '#,##0.00', '#,##0.00',
                  '#,##0.00', '#,##0.00', '####', '0#', '']
    sum_formula_list = [21, 11, 12, 13, 14, 15, 16, 17, 18, 20, ]
    total_list = [11, 12, 13, 14, 15, 16, 17, 18, 20, 21, 22, 23, 24, 25]
    sub_cost = [24, 25]

    # 获取数据库数据
    data_list = DcgBillDetailUPSModel.objects.filter(update_year=int(bill_year), update_month=int(bill_month)) \
        .values_list('bill_year', 'bill_month', 'mi_code', 'package_code', 'express_company', 'parcel_id', 'goods_id',
                     'postcode', 'ready_datetime', 'total_qty', 'weight',
                     'standard_delivery_fee', 'residential', 'dom_standard_undeliverable_return',
                     'uk_border_fee', 'additional_handling', 'peak_surcharge_additional_handling',
                     'address_correction_dom_standard', 'extended_area_surcharge_destination',
                     'fuel_surcharge_rate', 'fuel_surcharge', 'total_amount',
                     'total_vat', 'nett_cost', 'total_cost', 'total_profit', 'update_year', 'update_month',
                     'ups_bill_no_list')

    wb = write_excel(wb, sheet_name, head_list, data_list, style_list, sum_formula_list, total_list, sub_cost)

    # 获取账单的明细 DPD 费用
    sheet_name = 'DPD_Delivery_Fee_Detail'
    head_list = ['Bill_Year', 'Bill_Month', 'Mi_Code', 'Package_Code', 'Express_Company', 'Parcel_Id', 'Goods_Id',
                 'Postcode', 'ready_datetime', 'Total_Qty', 'Weight', 'Standard_Delivery_fee',
                 'Additional_Fee', 'Fuel_Surcharge_Rate', 'Fuel_Surcharge', 'Amount',
                 'VAT', 'Nett Cost', 'Total Cost', 'Nett Profit', 'Update_Year', 'Update_Month', 'Express_Bill_No.', ]
    style_list = ['####', '0#', '', '', '', '', '', '', '', '#,##0', '#,##0.0000', '#,##0.00', '#,##0.00', '#,##0.00',
                  '#,##0.00', '#,##0.00', '#,##0.00', '#,##0.00', '#,##0.00', '#,##0.00', '####', '0#', '']
    sum_formula_list = [15, 11, 12, 14]
    total_list = [11, 12, 14, 15, 16, 17, 18, 19]
    sub_cost = [18, 19]

    data_list = DcgBillDetailDPDModel.objects.filter(update_year=int(bill_year), update_month=int(bill_month)) \
        .values_list('bill_year', 'bill_month', 'mi_code', 'package_code', 'express_company', 'parcel_id', 'goods_id',
                     'postcode', 'ready_datetime', 'total_qty', 'weight', 'standard_delivery_fee',
                     'additional_fee', 'fuel_surcharge_rate',
                     'fuel_surcharge', 'total_amount', 'total_vat', 'nett_cost', 'total_cost',
                     'total_profit', 'update_year', 'update_month', 'dpd_bill_no_list')

    wb = write_excel(wb, sheet_name, head_list, data_list, style_list, sum_formula_list, total_list, sub_cost)

    # 获取账单中没有结算快递费用的的明细
    sheet_name = 'unCalc_Delivery_Fee_Detail'
    head_list = ['Bill_Year', 'Bill_Month', 'Mi_Code', 'Package_Code', 'Express_Company', 'Parcel_Id', 'Goods_Id',
                 'Postcode', 'ready_datetime', 'Total_Qty', 'Weight', ]
    style_list = ['####', '0#', '', '', '', '', '', '', '', '#,##0', '#,##0.0000', ]

    data_list = MiAccountBillDetailModel.objects.filter(delivery_fee_checked=0,
                                                        bill_year__lte=int(bill_year),
                                                        bill_month__lte=int(bill_month), ) \
        .values_list('bill_year', 'bill_month', 'mi_code', 'package_code', 'express_company', 'parcel_id', 'goods_id',
                     'postcode', 'ready_datetime', 'total_qty', 'weight', )

    wb = write_excel(wb, sheet_name, head_list, data_list, style_list)

    wb.save(response)
    return response


# Fuel surcharge list
class FuelSurchargeListView(ListView):
    ordering = ["express_company", "-begin_date", ]
    model = FuelSurchargeModel
    template_name = 'mi_fuel_surcharge_list.html'
    paginate_by = EACH_PAGE

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_active'] = MENU_ACTIVE
        context['page_tab'] = 6
        context['menu_grant'] = get_user_grant_list(self.request.user.id)
        context['express_company'] = self.request.GET.get('express_company', 'UPS')
        context['bill_year'] = int(self.request.GET.get('bill_year', datetime.datetime.now().strftime('%Y')))
        context['bill_month'] = int(self.request.GET.get('bill_month', 0))
        return context

    def get_queryset(self):
        query_express = self.request.GET.get('express_company', 'UPS')
        query_year = int(self.request.GET.get('begin_year', datetime.datetime.now().strftime('%Y')))
        query_month = int(self.request.GET.get('begin_month', 0))

        if query_month == 0:
            result = FuelSurchargeModel.objects.filter(express_company=query_express,
                                                       begin_date__year=query_year,
                                                       ) \
                .order_by('express_company', '-begin_date', )
        else:
            result = FuelSurchargeModel.objects.filter(express_company=query_express,
                                                       begin_date__year=query_year,
                                                       begin_date__month=query_month
                                                       ) \
                .order_by('express_company', '-begin_date', )

        return result


# Fuel surcharge add
class FuelSurchargeCreateView(CreateView):
    model = FuelSurchargeModel
    form_class = FuelSurchargeForm
    template_name = 'mi_fuel_surcharge_add.html'
    success_url = '/xiaomi/fuel-surcharge-list/'

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.op_user_id = self.request.user.id
        self.object.op_datetime = datetime.datetime.now()
        self.object.end_date = datetime.datetime.strptime('2030-12-31', '%Y-%m-%d')
        express_company = self.request.POST.get('express_company')
        this_begin_date = datetime.datetime.strptime(self.request.POST.get('begin_date'), '%Y-%m-%d')
        last_end_date = this_begin_date + datetime.timedelta(-1)
        FuelSurchargeModel.objects.filter(end_date__year=2030,
                                          end_date__month=12,
                                          end_date__day=31,
                                          express_company=express_company).update(end_date=last_end_date)

        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    def get_initial(self, *args, **kwargs):
        initial = super(FuelSurchargeCreateView, self).get_initial()
        initial["begin_date"] = datetime.date.today()
        initial["express_company"] = 'UPS'
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["begin_date"] = self.request.POST.get('begin_date', datetime.date.today())
        context['menu_grant'] = get_user_grant_list(self.request.user.id)
        context['menu_active'] = MENU_ACTIVE
        context['page_tab'] = 6
        return context


class MiLookup(View):
    def get(self, request):
        counter = FLCTempCounterModel.objects.get(id=1)
        context = {'page_tab': 8, 'order_no': '', 'qty': counter.qty, 'error': '', }
        return render(request, 'xiaomi_temp.html', context=context)

    def post(self, request):
        counter = FLCTempCounterModel.objects.get(id=1)
        context = {'page_tab': 8, 'order_no': '', 'qty': counter.qty, }
        delivery = self.request.POST.get('delivery')
        if delivery:
            queryset = FLCTempModel.objects.filter(deliver_no__exact=delivery)
            if queryset:
                counter = FLCTempCounterModel.objects.get(id=1)
                order_no = queryset[0].order_no
                if queryset[0].is_scan == 0:
                    new_qty = counter.qty + 1
                    counter.qty = new_qty
                    counter.save()
                    temp_scan = FLCTempModel.objects.get(deliver_no__exact=delivery)
                    temp_scan.is_scan = 1
                    temp_scan.save()
                    context = {'order_no': order_no, 'qty': new_qty, 'error': 'Found .............', }
                else:
                    context = {'order_no': order_no, 'qty': counter.qty, 'error': 'Repeat Scan...', }

        return render(request, 'xiaomi_temp.html', context=context)
