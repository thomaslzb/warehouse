import datetime
import math
import xlrd

from django.core.files.storage import FileSystemStorage
from django.http import HttpResponseRedirect
from django.shortcuts import render, reverse
from django.views import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.db import transaction

from menu.views import get_user_grant_list
from quote.models import EuroCountry
from quote.public_func import parcel
from .forms import SkuUKForm, SkuEuroForm, SkuForm
from .models import Sku, SkuFileUpload

MY_MENU_LOCAL = 'MY_SKU'


def valid_file(req):
    error = ''
    if not len(req.FILES):  # 判断是否有选择文件
        error = 'Must selected a file to upload.'

    try:
        uploaded_file = req.FILES['document']
        # 通过文件的后缀名，判断选择的文件是否是excel文件
        if not uploaded_file.name.split('.')[-1].upper() in ['XLS', 'XLSX']:
            error = 'Only excel file can be uploaded.'

        # 判断选择的文件是否大于5M  1M = bytes/1000000
        if uploaded_file.size / 1000000 > 5:
            error = 'File size = ' + format(uploaded_file.size / 1000000, "4.2") + 'M. File size can not more than 5M.'
    except:
        error = 'Must selected a file to upload.'
    return error


def valid_excel_data(excel_table):
    error = False
    n_rows = excel_table.nrows  # 行数
    for i in range(1, n_rows):
        rowValues = excel_table.row_values(i)
        try:
            if float(rowValues[2]) <= 0:
                error = True
            if float(rowValues[3]) <= 0:
                error = True
            if float(rowValues[4]) <= 0:
                error = True
            if float(rowValues[5]) <= 0:
                error = True
        except:
            error = True
        if error:
            break

    return error


class SkuCreateView(CreateView):
    model = Sku
    form_class = SkuForm
    template_name = 'sku_create.html'
    success_url = '/sku/sku-list'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_active'] = MY_MENU_LOCAL
        context['menu_grant'] = get_user_grant_list(self.request.user.id)
        return context

    def form_invalid(self, form):  # 定义表对象没有添加失败后跳转到的页面。
        response = super().form_invalid(form)
        return response


class SkuSaveAndAnotherView(SkuCreateView):
    success_url = '/sku/add'


class SkuUpdateView(UpdateView):
    model = Sku
    form_class = SkuForm
    template_name = 'sku_edit.html'
    success_url = '/sku/sku-list'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_active'] = MY_MENU_LOCAL
        context['menu_grant'] = get_user_grant_list(self.request.user.id)
        return context

    def form_invalid(self, form):  # 定义表对象没有添加失败后跳转到的页面。
        response = super().form_invalid(form)
        return response


class SkuListView(ListView):
    model = Sku
    template_name = 'sku_list.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_active'] = MY_MENU_LOCAL
        context['menu_grant'] = get_user_grant_list(self.request.user.id)
        return context

    def get_queryset(self):
        query_status = self.request.GET.get('status')
        query_sku = self.request.GET.get('s_sku')
        query_product = self.request.GET.get('s_product')
        if query_status or query_sku or query_product:
            if query_status == '':
                return Sku.objects.filter(sku_no__icontains=query_sku,
                                          sku_name__icontains=query_product,
                                          custom_id=self.request.user.id,
                                          )
            else:
                return Sku.objects.filter(is_ok__exact=query_status, sku_no__icontains=query_sku,
                                          sku_name__icontains=query_product,
                                          custom_id=self.request.user.id,
                                          )

        else:
            return Sku.objects.filter(custom_id=self.request.user.id)


class SkuUKDetail(DetailView):
    model = Sku
    template_name = 'sku_detail_uk.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_active'] = MY_MENU_LOCAL
        context['menu_grant'] = get_user_grant_list(self.request.user.id)
        return context


class SkuEuroDetail(DetailView):
    model = Sku
    template_name = 'sku_detail_euro.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_euro_queryset = EuroCountry.objects.all().order_by('country')
        context['all_euro'] = all_euro_queryset
        context['menu_active'] = MY_MENU_LOCAL
        context['menu_grant'] = get_user_grant_list(self.request.user.id)
        return context


class SkuQuoteUK(View):
    def post(self, request, slug):
        sku_uk_form = SkuUKForm(request.POST)
        sku_queryset = Sku.objects.filter(id__exact=slug)
        if sku_uk_form.is_valid():
            length = int(math.ceil(sku_queryset[0].sku_length))
            width = int(math.ceil(sku_queryset[0].sku_width))
            high = int(math.ceil(sku_queryset[0].sku_high))

            # 确定长，宽，高的正确顺序 length > width > high
            list_sort = [length, width, high]
            list_sort.sort()
            high = list_sort[0]
            width = list_sort[1]
            length = list_sort[2]

            is_uk = True
            weight = math.ceil(math.ceil(sku_queryset[0].sku_weight))
            qty = int(request.POST.get("qty", 0))
            postcode = request.POST.get("postcode", "").upper()
            address_type = request.POST.get("addresstype", "").upper()
            user_id = request.user.id

            company_code = 'HERM'
            l_hermes = parcel(company_code, length, width, high, weight, postcode, qty, user_id, is_uk)
            company_code = 'PASC'
            l_pacelforce = parcel(company_code, length, width, high, weight, postcode, qty, user_id, is_uk)
            company_code = 'DHL'
            l_dhl = parcel(company_code, length, width, high, weight, postcode, qty, user_id, is_uk)
            company_code = 'DPD'
            l_dpd = parcel(company_code, length, width, high, weight, postcode, qty, user_id, is_uk)
            company_code = 'UPS'
            l_ups = parcel(company_code, length, width, high, weight, postcode, qty, user_id, is_uk)

            if (not l_hermes[10]) and (not l_pacelforce[10]) and (not l_dhl[10]) and (not l_dpd[10]) and (
                    not l_ups[10]):
                return render(request, 'quote_error.html', {'go': 'UK',
                                                            'length': length,
                                                            'width': width,
                                                            'high': high,
                                                            'weight': weight,
                                                            'qty': qty,
                                                            'postcode': postcode,
                                                            'address_type': address_type,
                                                            "quote_uk_form": sku_uk_form,
                                                            'menu_active': MY_MENU_LOCAL,
                                                            'menu_grant': get_user_grant_list(request.user.id),
                                                            'sku_no': sku_queryset[0].sku_no,
                                                            'sku_name': sku_queryset[0].sku_name,
                                                            })

            l_hermes = l_hermes[:-1]
            l_pacelforce = l_pacelforce[:-1]
            l_dhl = l_dhl[:-1]
            l_dpd = l_dpd[:-1]
            l_ups = l_ups[:-1]
            return render(request, 'list_price.html', {
                'hermes': l_hermes,
                'parcelforce': l_pacelforce,
                'dhl': l_dhl,
                'dpd': l_dpd,
                'ups': l_ups,
                'length': length,
                'width': width,
                'high': high,
                'weight': weight,
                'qty': qty,
                'postcode': postcode,
                'address_type': address_type,
                'is_uk': is_uk,
                'now': datetime.datetime.now(),
                'menu_active': MY_MENU_LOCAL,
                'menu_grant': get_user_grant_list(request.user.id),
                'sku_no': sku_queryset[0].sku_no,
                'sku_name': sku_queryset[0].sku_name,
            })
        return render(request, "sku_detail_uk.html", {
            'sku_uk_form': sku_uk_form,
            'object': sku_queryset[0],
            'menu_active': MY_MENU_LOCAL,
            'menu_grant': get_user_grant_list(request.user.id),
        })


class SkuQuoteEURO(View):
    def post(self, request, slug):
        all_euro = EuroCountry.objects.all().filter(belong='EURO')
        sku_euro_form = SkuEuroForm(request.POST)
        sku_queryset = Sku.objects.filter(id__exact=slug)
        if sku_euro_form.is_valid():
            length = int(math.ceil(sku_queryset[0].sku_length))
            width = int(math.ceil(sku_queryset[0].sku_width))
            high = int(math.ceil(sku_queryset[0].sku_high))

            # 确定长，宽，高的正确顺序 length > width > high
            list_sort = [length, width, high]
            list_sort.sort()
            high = list_sort[0]
            width = list_sort[1]
            length = list_sort[2]

            is_uk = False
            weight = math.ceil(math.ceil(sku_queryset[0].sku_weight))
            qty = int(request.POST.get("qty", 0))
            postcode = request.POST.get("euro", "")
            address_type = request.POST.get("addresstype", "").upper()
            user_id = request.user.id

            company_code = 'HERM'
            l_hermes = parcel(company_code, length, width, high, weight, postcode, qty, user_id, is_uk, )
            company_code = 'PASC'
            l_pacelforce = parcel(company_code, length, width, high, weight, postcode, qty, user_id, is_uk, )
            company_code = 'DHL'
            l_dhl = parcel(company_code, length, width, high, weight, postcode, qty, user_id, is_uk, )

            company_code = 'DPD'
            l_dpd = parcel(company_code, length, width, high, weight, postcode, qty, user_id, is_uk, )
            company_code = 'UPS'
            l_ups = parcel(company_code, length, width, high, weight, postcode, qty, user_id, is_uk, )

            if (not l_hermes[10]) and (not l_pacelforce[10]) \
                    and (not l_dhl[10]) and (not l_dpd[10]) and (not l_ups[10]):
                return render(request, 'quote_error.html', {'go': 'EURO',
                                                            'length': length,
                                                            'width': width,
                                                            'high': high,
                                                            'weight': weight,
                                                            'qty': qty,
                                                            'postcode': postcode,
                                                            'address_type': address_type,
                                                            "quote_uk_form": sku_euro_form,
                                                            'menu_active': MY_MENU_LOCAL,
                                                            'menu_grant': get_user_grant_list(request.user.id),
                                                            'sku_no': sku_queryset[0].sku_no,
                                                            'sku_name': sku_queryset[0].sku_name,
                                                            })

            l_hermes = l_hermes[:-1]
            l_pacelforce = l_pacelforce[:-1]
            l_dhl = l_dhl[:-1]
            l_dpd = l_dpd[:-1]
            l_ups = l_ups[:-1]
            return render(request, 'list_price.html', {
                'hermes': l_hermes,
                'parcelforce': l_pacelforce,
                'dhl': l_dhl,
                'dpd': l_dpd,
                'ups': l_ups,
                'length': length,
                'width': width,
                'high': high,
                'weight': weight,
                'qty': qty,
                'postcode': postcode,
                'address_type': address_type,
                'is_uk': is_uk,
                'now': datetime.datetime.now(),
                'menu_active': MY_MENU_LOCAL,
                'menu_grant': get_user_grant_list(request.user.id),
                'sku_no': sku_queryset[0].sku_no,
                'sku_name': sku_queryset[0].sku_name,
            })
        return render(request, "sku_detail_euro.html", {
            'sku_uk_form': sku_euro_form,
            'object': sku_queryset[0],
            'all_euro': all_euro,
            'menu_active': MY_MENU_LOCAL,
            'menu_grant': get_user_grant_list(request.user.id),
        })


class SkuDeleteView(DeleteView):
    model = Sku
    template_name = "sku_confirm_delete.html"

    def get_object(self, queryset=None):
        """ Hook to ensure object is owned by request.user. """
        obj = super(SkuDeleteView, self).get_object()
        # if not obj.op_user == self.request.user.id:
        #     raise Http404
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_active'] = MY_MENU_LOCAL
        context['menu_grant'] = get_user_grant_list(self.request.user.id)
        return context

    def get_success_url(self):
        return reverse('sku:sku-list')


class SkuFileUploadView(View):
    def get(self, request):
        return render(request, 'sku_upload.html', {
            'menu_active': MY_MENU_LOCAL,
            'menu_grant': get_user_grant_list(request.user.id),
        })

    def post(self, request):
        error = valid_file(request)
        if error:
            return render(request, 'sku_upload.html', {
                'menu_active': MY_MENU_LOCAL,
                'menu_grant': get_user_grant_list(request.user.id),
                'error': error,
            })

        uploaded_file = request.FILES['document']
        excel_data = xlrd.open_workbook(filename=None, file_contents=uploaded_file.read())
        table = excel_data.sheet_by_index(0)
        n_rows = table.nrows  # 行数

        if valid_excel_data(table):
            error = 'Uploading Failure. length/width/high/weight must be more than zero. ' \
                    'There are some error in the uploading File - ' + \
                    uploaded_file.name + '. '
            return render(request, 'sku_upload.html', {
                'menu_active': MY_MENU_LOCAL,
                'menu_grant': get_user_grant_list(request.user.id),
                'error': error,
            })
        try:
            with transaction.atomic():
                for i in range(1, n_rows):
                    rowValues = table.row_values(i)
                    Sku.objects.create(sku_no=rowValues[0],
                                       sku_name=rowValues[1],
                                       sku_length=rowValues[2],
                                       sku_width=rowValues[3],
                                       sku_high=rowValues[4],
                                       sku_weight=rowValues[5],
                                       is_ok='1',
                                       custom_id=request.user.id
                                       )

        except Exception as e:
            error = 'Sku No can no be duplication. There are some error in the uploading Files - ' + \
                    uploaded_file.name + '. '
            return render(request, 'sku_upload.html', {
                'menu_active': MY_MENU_LOCAL,
                'menu_grant': get_user_grant_list(request.user.id),
                'error': error,
            })

        return HttpResponseRedirect(reverse('sku:sku-list'))


class UserListView(ListView):
    model = Sku
    template_name = 'sku_list.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_active'] = MY_MENU_LOCAL
        context['menu_grant'] = get_user_grant_list(self.request.user.id)
        return context
