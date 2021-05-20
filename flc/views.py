import datetime
import decimal

from django.db.models import Q, Prefetch
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.views import View
from django.views.generic import ListView

from flc.forms import FlcCompanyForm, FlcFuelSurchargeForm, FlcPortForm, FlcPriceForm, FLCQuoteForm
from flc.models import FlcCompanyModel, FlcFuelChargeModel, FLCPortModel, FLCContainModel, FLCPostcodeModel
from flc.models import FLCPriceModel
from menu.views import get_user_grant_list
from utils.tools import format_postcode

MENU_ACTIVE = 'FLC_DATA'
EACH_PAGE = 15


# FLC 公司列表
class FlcCompanyListView(ListView):
    ordering = ["code", ]
    model = FlcCompanyModel
    template_name = 'flc_company_list.html'
    paginate_by = EACH_PAGE

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_active'] = MENU_ACTIVE
        context['page_tab'] = 1
        context['menu_grant'] = get_user_grant_list(self.request.user.id)
        context['company_code'] = self.request.GET.get('company_code', '')
        context['company_name'] = self.request.GET.get('company_name', '')
        context['status'] = int(self.request.GET.get('status', -1))
        return context

    def get_queryset(self):
        query_code = self.request.GET.get('company_code', '')
        query_name = self.request.GET.get('company_name', '')
        query_status = int(self.request.GET.get('status', -1))
        if query_status == -1:
            result = FlcCompanyModel.objects.filter(~Q(code__exact='Public'),
                                                    code__icontains=query_code,
                                                    name__icontains=query_name,
                                                    )
        else:
            result = FlcCompanyModel.objects.filter(~Q(code__exact='Public'),
                                                    code__icontains=query_code,
                                                    name__icontains=query_name,
                                                    is_used=query_status
                                                    )

        return result


def save_flc_company_form(request, form, template_name):
    data = dict()
    if request.method == "POST":
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
            companies = FlcCompanyModel.objects.all()
            data['html_company_list'] = render_to_string('flc_company/partial_flc_company_list.html',
                                                         {'object_list': companies},
                                                         )
        else:
            data['form_is_valid'] = False

    context = {'form': form}
    data['html_form'] = render_to_string(template_name, context, request=request, )
    return JsonResponse(data)


def flc_company_create(request):
    if request.method == "POST":
        form = FlcCompanyForm(request.POST)
    else:
        form = FlcCompanyForm()

    return save_flc_company_form(request, form, 'flc_company/flc_company_create.html')


def flc_company_update(request, pk):
    company = get_object_or_404(FlcCompanyModel, pk=pk)
    if request.method == "POST":
        form = FlcCompanyForm(request.POST, instance=company)
    else:
        form = FlcCompanyForm(instance=company)

    return save_flc_company_form(request, form, 'flc_company/flc_company_update.html')


# Flc 燃油费列表
class FlcFuelSurchargeListView(ListView):
    ordering = ["-begin_date", ]
    model = FlcFuelChargeModel
    template_name = 'flc_fuel_surcharge_list.html'
    paginate_by = EACH_PAGE

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_active'] = MENU_ACTIVE
        context['page_tab'] = 3
        context['menu_grant'] = get_user_grant_list(self.request.user.id)
        context['company_code'] = self.request.GET.get('company_code', '')
        context['company_name'] = self.request.GET.get('company_name', '')
        return context

    def get_queryset(self):
        query_code = self.request.GET.get('company_code', '')
        query_name = self.request.GET.get('company_name', '')
        result = FlcFuelChargeModel.objects.filter(company_code__name__icontains=query_name,
                                                   company_code__code__icontains=query_code,
                                                   )

        return result


def save_flc_fuel_form(request, form, template_name):
    data = dict()
    if request.method == "POST":
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
            fuel_surcharges = FlcFuelChargeModel.objects.all()
            data['html_fuel_list'] = render_to_string('flc_fuel_surcharge/partial_flc_fuel_surcharge_list.html',
                                                      {'object_list': fuel_surcharges},
                                                      )
        else:
            data['form_is_valid'] = False

    queryset_company = FlcCompanyModel.objects.all()
    context = {'form': form, 'all_company': queryset_company}
    data['html_form'] = render_to_string(template_name, context, request=request, )

    return JsonResponse(data)


def flc_fuel_surcharge_create(request):
    if request.method == "POST":
        form = FlcFuelSurchargeForm(request.POST)
    else:
        # 初始化日期
        year = datetime.date.today().strftime("%Y")
        month = datetime.date.today().strftime("%m")
        this_month_first_day = datetime.datetime.strptime(year + "-" + month + "-01", "%Y-%m-%d")
        this_month_first_day = this_month_first_day.strftime("%Y-%m-%d")
        next_month_first_day = datetime.datetime.strptime(year + "-" + str(int(month) + 1) + "-01", "%Y-%m-%d")
        this_month_last_day = (next_month_first_day + datetime.timedelta(-1)).strftime("%Y-%m-%d")

        form = FlcFuelSurchargeForm(initial={'begin_date': this_month_first_day,
                                             'expire_date': this_month_last_day,
                                             })

    return save_flc_fuel_form(request, form, 'flc_fuel_surcharge/flc_fuel_surcharge_create.html')


def flc_fuel_surcharge_update(request, pk, slug):
    fuel_surcharge = get_object_or_404(FlcFuelChargeModel, company_code_id=pk, begin_date=slug)
    if request.method == "POST":
        form = FlcFuelSurchargeForm(request.POST, instance=fuel_surcharge)
    else:
        form = FlcFuelSurchargeForm(instance=fuel_surcharge)

    return save_flc_fuel_form(request, form, 'flc_fuel_surcharge/flc_fuel_surcharge_update.html')


# FLC 英国港口列表
class FlcPortListView(ListView):
    ordering = ["code", ]
    model = FLCPortModel
    template_name = 'flc_port_list.html'
    paginate_by = EACH_PAGE

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_active'] = MENU_ACTIVE
        context['page_tab'] = 4
        context['menu_grant'] = get_user_grant_list(self.request.user.id)
        context['company_code'] = self.request.GET.get('port_code', '')
        context['company_name'] = self.request.GET.get('port_name', '')
        return context

    def get_queryset(self):
        query_code = self.request.GET.get('port_code', '')
        query_name = self.request.GET.get('port_name', '')
        result = FLCPortModel.objects.filter(port_code__icontains=query_code,
                                             port_name__icontains=query_name,
                                             )

        return result


def save_flc_port_form(request, form, template_name):
    data = dict()
    if request.method == "POST":
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
            ports = FLCPortModel.objects.all()
            data['html_port_list'] = render_to_string('flc_port/partial_flc_port_list.html',
                                                      {'object_list': ports},
                                                      )
        else:
            data['form_is_valid'] = False

    context = {'form': form}
    data['html_form'] = render_to_string(template_name, context, request=request, )
    return JsonResponse(data)


def flc_port_create(request):
    if request.method == "POST":
        form = FlcPortForm(request.POST)
    else:
        form = FlcPortForm()

    return save_flc_port_form(request, form, 'flc_port/flc_port_create.html')


def flc_port_update(request, pk):
    port = get_object_or_404(FLCPortModel, pk=pk)
    if request.method == "POST":
        form = FlcPortForm(request.POST, instance=port)
    else:
        form = FlcPortForm(instance=port)

    return save_flc_port_form(request, form, 'flc_port/flc_port_update.html')


# FLC Container 列表
class FlcContainerListView(ListView):
    ordering = ["code", ]
    model = FLCContainModel
    template_name = 'flc_container_list.html'
    paginate_by = EACH_PAGE

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_active'] = MENU_ACTIVE
        context['page_tab'] = 5
        context['menu_grant'] = get_user_grant_list(self.request.user.id)
        return context

    def get_queryset(self):
        result = FLCContainModel.objects.all()

        return result


# FLC Postcode 列表
class FlcPostcodeListView(ListView):
    ordering = ['postcode', ]
    model = FLCPostcodeModel
    template_name = 'flc_postcode_list.html'
    paginate_by = EACH_PAGE

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_active'] = MENU_ACTIVE
        context['page_tab'] = 6
        context['menu_grant'] = get_user_grant_list(self.request.user.id)
        context['postcode'] = self.request.GET.get('postcode', '').strip().upper()
        context['county'] = self.request.GET.get('county', '').strip().upper()
        context['district'] = self.request.GET.get('district', '').strip().upper()
        return context

    def get_queryset(self):
        query_postcode = self.request.GET.get('postcode', '').strip().upper()
        query_county = self.request.GET.get('county', '').strip().upper()
        query_district = self.request.GET.get('district', '').strip().upper()
        result = FLCPostcodeModel.objects.filter(postcode__icontains=query_postcode,
                                                 county__icontains=query_county,
                                                 district__icontains=query_district,
                                                 )

        return result


# Flc Price 列表
class FlcPriceListView(ListView):
    ordering = ['company_code', 'port_code', 'destination', 'container', '-begin_date', ]
    model = FLCPriceModel
    template_name = 'flc_price_list.html'
    paginate_by = EACH_PAGE

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_active'] = MENU_ACTIVE
        context['page_tab'] = 2
        context['menu_grant'] = get_user_grant_list(self.request.user.id)
        context['company_code'] = self.request.GET.get('company_code', '')
        context['port'] = self.request.GET.get('port', '')
        context['destination'] = self.request.GET.get('destination', '')
        context['destination_type'] = self.request.GET.get('destination_type', '')
        return context

    def get_queryset(self):
        query_company_code = self.request.GET.get('company_code', '')
        query_port = self.request.GET.get('port', '')
        query_container = self.request.GET.get('container', '')
        query_destination = self.request.GET.get('destination', '')
        query_destination_type = self.request.GET.get('destination_type', 'ALL')

        if query_destination_type == "POSTCODE":
            result1 = FLCPriceModel.objects.filter(company_code__code__icontains=query_company_code,
                                                   port_code__port_code__icontains=query_port,
                                                   destination__icontains=query_destination,
                                                   destination_type__icontains='POSTCODE',
                                                   )
            result2 = FLCPriceModel.objects.filter(company_code__code__icontains=query_company_code,
                                                   port_code__port_name__icontains=query_port,
                                                   destination__icontains=query_destination,
                                                   destination_type__icontains='POSTCODE',
                                                   )

        elif query_destination_type == "CITY":
            result1 = FLCPriceModel.objects.filter(company_code__code__icontains=query_company_code,
                                                   port_code__port_code__icontains=query_port,
                                                   destination__icontains=query_destination,
                                                   destination_type__icontains='CITY',
                                                   )
            result2 = FLCPriceModel.objects.filter(company_code__code__icontains=query_company_code,
                                                   port_code__port_name__icontains=query_port,
                                                   destination__icontains=query_destination,
                                                   destination_type__icontains='POSTCODE',
                                                   )
        else:
            result1 = FLCPriceModel.objects.filter(company_code__code__icontains=query_company_code,
                                                   port_code__port_code__icontains=query_port,
                                                   container__name__icontains=query_container,
                                                   destination__icontains=query_destination,
                                                   )
            result2 = FLCPriceModel.objects.filter(company_code__code__icontains=query_company_code,
                                                   port_code__port_name__icontains=query_port,
                                                   destination__icontains=query_destination,
                                                   destination_type__icontains='POSTCODE',
                                                   )

        result = result1.union(result2).order_by('company_code_id',
                                                 'port_code_id',
                                                 'destination',
                                                 'destination_type',
                                                 'container_id',
                                                 '-begin_date'
                                                 )
        return result


def save_flc_price_form(request, form, template_name):
    data = dict()
    if request.method == "POST":
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
            flc_price = FLCPriceModel.objects.all()
            data['html_flc_price_list'] = render_to_string('flc_price/partial_price_list.html',
                                                           {'object_list': flc_price},
                                                           )
        else:
            data['form_is_valid'] = False

    queryset_company = FlcCompanyModel.objects.all()
    queryset_container = FLCContainModel.objects.all()
    queryset_port = FLCPortModel.objects.all()
    context = {'form': form,
               'all_company': queryset_company,
               'all_container': queryset_container,
               'all_port': queryset_port,
               }
    data['html_form'] = render_to_string(template_name, context, request=request, )

    return JsonResponse(data)


def flc_price_create(request):
    if request.method == "POST":
        form = FlcPriceForm(request.POST)
    else:
        # # 初始化日期
        # year = datetime.date.today().strftime("%Y")
        # month = datetime.date.today().strftime("%m")
        # this_month_first_day = datetime.datetime.strptime(year + "-" + month + "-01", "%Y-%m-%d")
        # this_month_first_day = this_month_first_day.strftime("%Y-%m-%d")
        # next_month_first_day = datetime.datetime.strptime(year + "-" + str(int(month) + 1) + "-01", "%Y-%m-%d")
        # this_month_last_day = (next_month_first_day + datetime.timedelta(-1)).strftime("%Y-%m-%d")
        #
        # form = FlcPriceForm(initial={'begin_date': this_month_first_day,
        #                              'expire_date': this_month_last_day,
        #                              })
        form = FlcPriceForm()

    return save_flc_price_form(request, form, 'flc_price/flc_price_create.html')


def flc_price_update(request, company_code, port_code, destination_type, destination, container, begin_date, ):
    flc_price = get_object_or_404(FLCPriceModel,
                                  company_code_id=company_code,
                                  port_code=port_code,
                                  destination=destination,
                                  destination_type=destination_type,
                                  container=container,
                                  begin_date=begin_date,
                                  )
    if request.method == "POST":
        form = FlcPriceForm(request.POST, instance=flc_price)
    else:
        form = FlcPriceForm(instance=flc_price)

    return save_flc_price_form(request, form, 'flc_price/flc_price_update.html')


class FLCQuoteView(View):
    def get(self, request):
        queryset_port = FLCPortModel.objects.all()
        queryset_container = FLCContainModel.objects.all().order_by('name')
        context = {'all_port': queryset_port,
                   'all_container': queryset_container,
                   'today': datetime.datetime.now().date(),
                   'display': False
                   }
        return render(request, 'flc_quote.html', context=context)

    def post(self, request):
        forms = FLCQuoteForm(request.POST)
        queryset_port = FLCPortModel.objects.all()
        queryset_container = FLCContainModel.objects.all().order_by('name')
        context = {'all_port': queryset_port,
                   'all_container': queryset_container,
                   'forms': forms,
                   }
        if forms.is_valid():
            postcode = format_postcode(self.request.POST.get('postcode'))
            port_code = self.request.POST.get('port_code')
            container = self.request.POST.get('container')
            pick_date = self.request.POST.get('pickup_date')
            queryset_price = FLCPriceModel.objects.filter(destination=postcode,
                                                          destination_type='POSTCODE',
                                                          port_code=port_code,
                                                          container__id=container,
                                                          begin_date__lte=pick_date,
                                                          expire_date__gte=pick_date,
                                                          )

            queryset_fuel = FlcFuelChargeModel.objects.filter(begin_date__lte=pick_date,
                                                              expire_date__gte=pick_date,
                                                              )
            fuel_list = []
            for company in queryset_price:
                found_it = False
                for fuel in queryset_fuel:
                    if company.company_code_id == fuel.company_code_id:
                        found_it = True
                        fuel_list.append([fuel.company_code_id, str(fuel.fuel_charge) + '%'])
                        break
                if not found_it:
                    fuel_list.append([company.company_code_id, ''])

            get_postcode = get_object_or_404(FLCPostcodeModel, postcode=postcode)
            context['postcode'] = postcode
            if get_postcode:
                context['city'] = get_postcode.county
                context['district'] = get_postcode.district

            context['price_list'] = queryset_price
            context['fuel_list'] = fuel_list
            context['display'] = True
            context['forms'] = forms
        else:
            context['display'] = False
        return render(request, 'flc_quote.html', context=context)
