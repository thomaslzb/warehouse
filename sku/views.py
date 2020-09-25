import math
import datetime

from django.core.files.storage import FileSystemStorage
from django.http import request
from django.shortcuts import render, reverse
from django.views import View
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from quote.models import EuroCountry
from .models import Sku, SkuFileUpload
from .forms import SkuUKForm, SkuEuroForm, SkuForm
from quote.public_func import parcel

MY_MENU_LOCAL = 'MY_SKU'


class SkuCreateView(CreateView):
    model = Sku
    form_class = SkuForm
    template_name = 'sku_create.html'
    success_url = '/sku/sku-list'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_active'] = MY_MENU_LOCAL

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
        return context


class SkuEuroDetail(DetailView):
    model = Sku
    template_name = 'sku_detail_euro.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_euro_queryset = EuroCountry.objects.all().order_by('country')
        context['all_euro'] = all_euro_queryset
        context['menu_active'] = MY_MENU_LOCAL
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

            if (not l_hermes[5]) and (not l_pacelforce[5]) and (not l_dhl[5]) and (not l_dpd[5]) and (not l_ups[5]):
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
                'sku_no': sku_queryset[0].sku_no,
                'sku_name': sku_queryset[0].sku_name,
            })
        return render(request, "sku_detail_uk.html", {
            'sku_uk_form': sku_uk_form,
            'object': sku_queryset[0],
            'menu_active': MY_MENU_LOCAL,
        })


class SkuQuoteEURO(View):
    def post(self, request, slug):
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

            if (not l_hermes[5]) and (not l_pacelforce[5]) and (not l_dhl[5]) and (not l_dpd[5]) and (not l_ups[5]):
                return render(request, 'quote_error.html', {'go': 'UK',
                                                            'length': length,
                                                            'width': width,
                                                            'high': high,
                                                            'weight': weight,
                                                            'qty': qty,
                                                            'postcode': postcode,
                                                            'address_type': address_type,
                                                            "quote_uk_form": sku_euro_form,
                                                            'menu_active': MY_MENU_LOCAL,
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
                'sku_no': sku_queryset[0].sku_no,
                'sku_name': sku_queryset[0].sku_name,
            })
        return render(request, "sku_detail_euro.html", {
            'sku_uk_form': sku_euro_form,
            'object': sku_queryset[0],
            'menu_active': MY_MENU_LOCAL,
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

    def get_success_url(self):
        return reverse('sku:sku-list')


class SkuFileView(View):
    def get(self, request):
        return render(request, 'sku_upload.html', {
                'menu_active': MY_MENU_LOCAL,
                })

    def post(self, request):
        uploaded_file = request.FILES['document']
        fs = FileSystemStorage()
        new_file_name = str(request.user.id) + '-' + uploaded_file.name
        fs.save(new_file_name, uploaded_file)
        sku_upload = SkuFileUpload()
        sku_upload.file_name = new_file_name
        sku_upload.custom_id = request.user.id
        sku_upload.save()

        return render(request, 'sku_upload.html', {
                'menu_active': MY_MENU_LOCAL,
                })


class UserListView(ListView):
    model = Sku
    template_name = 'sku_list.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_active'] = MY_MENU_LOCAL
        return context
