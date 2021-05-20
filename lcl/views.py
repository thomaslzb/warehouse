import datetime
import decimal
import json

from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.views import View
from django.views.generic import ListView, CreateView

from air_freight.views import digit_postcode, string_postcode
from menu.views import get_user_grant_list
from .forms import LclCompanyForm, LclFuelSurchargeForm
from .models import LclZoneDetailModel, ZoneChargeModel, LclCompanyModel, LclAreaDetailModel, LclCollectAreaModel
from .models import LclFuelChargeModel
from .models import AreaDetailModel, LclZoneExtraDetailModel, LclProfitViaAreaDetailModel

MY_MENU_LOCAL = 'LCL'
EACH_PAGE = 15


def get_zone_id(company_code, postcode):
    """
    获取 zonal 的 zone_id
    """
    zone_id = 0
    postcode_digit = digit_postcode(postcode)
    str_postcode = string_postcode(postcode)

    zone_detail_query = LclZoneDetailModel.objects.filter(zone__company__code=company_code,
                                                          begin__icontains=str_postcode,
                                                          end__icontains=str_postcode)
    for record in zone_detail_query:
        if digit_postcode(record.begin) <= postcode_digit <= digit_postcode(record.end):
            zone_id = record.zone_id
            break

    return zone_id


def get_GMA_area_id(postcode):
    """
    获取 GMA area zonal 的 zone_id
    """
    area_id = 0
    area_name = ""
    postcode_digit = digit_postcode(postcode)
    str_postcode = string_postcode(postcode)

    zone_detail_query = LclAreaDetailModel.objects.filter(begin__icontains=str_postcode,
                                                          end__icontains=str_postcode,
                                                          )
    for record in zone_detail_query:
        if digit_postcode(record.begin) <= postcode_digit <= digit_postcode(record.end):
            area_id = record.area_id_id
            area_name = record.area_id
            break

    return area_id, area_name


def get_fuel_charge_rate(company_code, delivery_date):
    fuel_rate = -1  # 不确定
    delivery_date = datetime.datetime.strptime(delivery_date, '%Y-%m-%d')
    queryset = LclFuelChargeModel.objects.filter(company_code=company_code,
                                                 begin_date__lte=delivery_date,
                                                 expire_date__gte=delivery_date)
    if queryset:
        fuel_rate = decimal.Decimal(queryset[0].fuel_charge)
    return fuel_rate


def calculation(company_code, company_calc_list):
    service_code = ['ECONOMY', 'EXPRESS']
    collect_area = company_calc_list[0]
    delivery_date = company_calc_list[1]
    volume = decimal.Decimal(company_calc_list[2])
    weight = decimal.Decimal(company_calc_list[3])
    pallet_qty = int(company_calc_list[4])
    postcode = (company_calc_list[5][:-3]).strip().upper()

    zone_id = get_zone_id(company_code, postcode)

    fuel_charge_Rate = get_fuel_charge_rate(company_code, delivery_date)

    express_amt = 0
    economy_amt = 0
    if company_code == "Public":
        CalcVolume = volume
        CalcWeight = weight / 500
        if CalcVolume < CalcWeight:
            CalcVolume = CalcWeight

        queryset_price = ZoneChargeModel.objects.filter(zone_id=zone_id,
                                                        collect_area=collect_area,
                                                        service_type=service_code[0], )
        if queryset_price:
            economy_amt = queryset_price[0].basic_price
        if CalcVolume < 2:
            CalcVolume = 2
        economy_amt = economy_amt * int(CalcVolume)

    if company_code == "GMA":
        CalcVolume = volume
        CalcWeight = weight * decimal.Decimal(0.0023)
        if volume < CalcWeight:
            CalcVolume = CalcWeight
        find_area = get_GMA_area_id(postcode)
        area_id = find_area[0]
        queryset_zone_id = AreaDetailModel.objects.filter(id__exact=area_id,
                                                          )
        if queryset_zone_id:
            zone_id = queryset_zone_id[0].zone_id

        queryset_price = ZoneChargeModel.objects.filter(zone_id=zone_id,
                                                        cbm_minimum__lt=CalcVolume,
                                                        cbm_maximum__gte=CalcVolume,
                                                        collect_area=collect_area,
                                                        service_type=service_code[0],
                                                        )
        if queryset_price:
            economy_amt = queryset_price[0].basic_price

    if company_code == "ASLONDON":
        CalcVolume = volume
        CalcWeight = weight / 500
        if CalcVolume < CalcWeight:
            CalcVolume = CalcWeight
        queryset_price = ZoneChargeModel.objects.filter(zone_id=zone_id,
                                                        cbm_minimum__lte=CalcVolume,
                                                        cbm_maximum__gte=CalcVolume,
                                                        collect_area=collect_area,
                                                        service_type=service_code[0],
                                                        )
        if queryset_price:
            economy_amt = queryset_price[0].basic_price

    if company_code == "BENNETTS":
        CalcVolume = weight * decimal.Decimal(2.25) / 1000
        CalcWeight = weight
        if CalcVolume < volume:
            CalcWeight = volume / decimal.Decimal(2.25) * 1000

        CalcWeight = int(CalcWeight)
        queryset_price = ZoneChargeModel.objects.filter(zone_id=zone_id,
                                                        weight_minimum__lt=CalcWeight,
                                                        weight_maximum__gte=CalcWeight,
                                                        collect_area=collect_area,
                                                        service_type=service_code[0],
                                                        )
        if queryset_price:
            economy_amt = queryset_price[0].basic_price

    if company_code == "BARTRUMS":
        queryset_price = ZoneChargeModel.objects.filter(zone_id=zone_id,
                                                        service_type__in=service_code,
                                                        weight_minimum__lte=pallet_qty,
                                                        weight_maximum__gte=pallet_qty,
                                                        collect_area=collect_area,
                                                        )
        for record in queryset_price:
            if record.service_type == 'ECONOMY':
                economy_amt = record.basic_price * int(pallet_qty)
            else:
                express_amt = record.basic_price * int(pallet_qty)

    if company_code == "ANGLIA":
        queryset_price = ZoneChargeModel.objects.filter(zone_id=zone_id,
                                                        service_type__in=service_code,
                                                        cbm_minimum__lt=pallet_qty,
                                                        cbm_maximum__gte=pallet_qty,
                                                        collect_area=collect_area,
                                                        )
        for record in queryset_price:
            if record.service_type == 'ECONOMY':
                economy_amt = record.basic_price * int(pallet_qty)
            else:
                express_amt = record.basic_price * int(pallet_qty)

    if company_code == "SIMARCO":
        queryset_price = ZoneChargeModel.objects.filter(zone_id=zone_id,
                                                        service_type__in=service_code,
                                                        cbm_minimum__lte=pallet_qty,
                                                        cbm_maximum__gte=pallet_qty,
                                                        collect_area=collect_area,
                                                        )
        if pallet_qty <= 5:
            qty = 1
        else:
            qty = int(pallet_qty)
        for record in queryset_price:
            if record.service_type == 'ECONOMY':
                economy_amt = record.basic_price * qty
            else:
                express_amt = record.basic_price * qty

    if company_code == "RIVA":
        queryset_price = ZoneChargeModel.objects.filter(zone_id=zone_id,
                                                        service_type__in=service_code,
                                                        cbm_minimum=1,
                                                        collect_area=collect_area,
                                                        )
        for record in queryset_price:
            if record.service_type == 'ECONOMY':
                economy_amt = record.basic_price * int(pallet_qty)
            else:
                express_amt = record.basic_price * int(pallet_qty)

    extra_value = check_postcode_extra(postcode)

    economy_amt = economy_amt + extra_value
    express_amt = express_amt + extra_value

    if fuel_charge_Rate != -1:
        economy_amt = economy_amt * (1 + fuel_charge_Rate / 100)
        express_amt = express_amt * (1 + fuel_charge_Rate / 100)

    # [company_code, fuel_charge_Rate, express_amt, economy_amt]
    return company_code, fuel_charge_Rate, express_amt, economy_amt


# 分离postcode 的字符串及数字
def return_char_number(input_string):
    input_list = list(input_string)
    max_len = len(input_string) - 1
    if isinstance(input_string[max_len], str):
        return input_string, 0
    number_str = ''
    for i in range(max_len):
        char = input_list[max_len - i]
        if char.isdigit():
            number_str = char + number_str
        else:
            break
    char_str = ''.join(input_list[:-len(number_str)])
    if number_str == '':
        number_int = 0
    else:
        number_int = int(number_str)
    return char_str, number_int


# 检查是否是LONDON M24地区的邮编, 是则加费用
def check_postcode_extra(short_postcode):
    value = 0
    result = return_char_number(short_postcode)
    postcode_char_str = result[0]
    get_number = result[1]

    postcode_queryset = LclZoneExtraDetailModel.objects.filter(begin__startswith=postcode_char_str,
                                                               end__startswith=postcode_char_str,
                                                               )

    for record in postcode_queryset:
        result = return_char_number(record.begin)
        char_str = result[0]
        begin_number = result[1]
        result = return_char_number(record.end)
        end_number = result[1]
        if begin_number <= get_number <= end_number and char_str == postcode_char_str:
            return record.charge_price

    return value


class LclCalculationView(View):
    def get(self, request):
        permission_string = get_user_grant_list(request.user.id)

        # 如果权限为2， 则可以显示全部公司的价格
        display_all_company = int(permission_string[3])

        input_para_list = ['FELIX',
                           datetime.date.today(),
                           ]

        collection_queryset = LclCollectAreaModel.objects.only('name').all().order_by('sort_num')
        return render(request, 'lcl_calculate.html', {'menu_active': MY_MENU_LOCAL,
                                                      'menu_grant': get_user_grant_list(request.user.id),
                                                      'input_para_list': input_para_list,
                                                      'collection_queryset': collection_queryset,
                                                      'display_all_company': display_all_company,  # 显示所有公司价格
                                                      'zone_id': 0,  # 禁止结果列表显示
                                                      }, )

    def post(self, request):
        collection_queryset = LclCollectAreaModel.objects.only('name').all().order_by('sort_num')
        query_collect_area = self.request.POST.get('collect_code', 'FELIX')
        query_delivery_date = datetime.datetime.strptime(self.request.POST.get('delivery_date', datetime.date.today()),
                                                         '%Y-%m-%d')
        query_delivery_date = query_delivery_date.strftime('%Y-%m-%d')

        query_volume = float(request.POST.get("volume", 0))
        query_weight = float(request.POST.get("weight", 0))
        query_pallet_qty = int(float(request.POST.get("qty", 0)))
        query_uk_postcode = request.POST.get("postcode", "").upper()

        company_query = LclCompanyModel.objects.filter(~Q(code__icontains='Public'),
                                                       is_used=1,
                                                       )
        company_calc_result = []
        input_para_list = [query_collect_area,
                           query_delivery_date,
                           query_volume,
                           query_weight,
                           query_pallet_qty,
                           query_uk_postcode,
                           ]
        for record in company_query:
            company_code = record.code.strip()
            # 用于保存每个公司的计算结果, [company_code,  fuel_charge_Rate, express_amt, economy_amt]
            company_calc_result.append(calculation(company_code, input_para_list))

        permission_string = get_user_grant_list(request.user.id)

        # 如果权限为2， 则可以显示全部公司的价格
        display_all_company = int(permission_string[3])

        # 过滤掉所有计算结果均为0的公司
        new_result = []
        for company in company_calc_result:
            if company[2] != 0 or company[3] != 0:
                new_result.append([company[0], company[1], "£" + '%.2f' % company[2], "£" + '%.2f' % company[3], ])

        # 计算销售价格
        if query_collect_area == 'FELIX':
            sales_price = [0, calculation('Public', input_para_list)[3], ]
        else:
            economy_sales_price = 0
            express_sales_price = 0
            for company in company_calc_result:
                if company[0] == 'RIVA':
                    express_sales_price = company[2]
                    economy_sales_price = company[3]
            queryset_profit = LclProfitViaAreaDetailModel.objects.filter(via_area=query_collect_area)
            for record in queryset_profit:
                if record.service_type == 'ECONOMY':
                    economy_sales_price = economy_sales_price + record.fix_price
                else:
                    express_sales_price = express_sales_price + record.fix_price
            sales_price = [express_sales_price, economy_sales_price]
        sales_price = ["£" + '%.2f' % sales_price[0], "£" + '%.2f' % sales_price[1]]

        # 设置返回值
        return render(request, 'lcl_calculate.html', {'menu_active': MY_MENU_LOCAL,
                                                      'menu_grant': permission_string,
                                                      'input_para_list': input_para_list,
                                                      'new_result': new_result,
                                                      'collection_queryset': collection_queryset,
                                                      'display_all_company': display_all_company,
                                                      'sales_price': sales_price,
                                                      }, )


# LCL 公司列表
class LclCompanyListView(ListView):
    ordering = ["code", ]
    model = LclCompanyModel
    template_name = 'lcl_company_list.html'
    paginate_by = EACH_PAGE

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_active'] = 'LCL_DATA'
        context['page_tab'] = 2
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
            result = LclCompanyModel.objects.filter(~Q(code__exact='Public'),
                                                    code__icontains=query_code,
                                                    name__icontains=query_name,
                                                    )
        else:
            result = LclCompanyModel.objects.filter(~Q(code__exact='Public'),
                                                    code__icontains=query_code,
                                                    name__icontains=query_name,
                                                    is_used=query_status
                                                    )

        return result


def save_company_form(request, form, template_name):
    data = dict()
    if request.method == "POST":
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
            companies = LclCompanyModel.objects.filter(~Q(code__exact='Public'))
            data['html_company_list'] = render_to_string('company/partial_company_list.html',
                                                         {'object_list': companies},
                                                         )
        else:
            data['form_is_valid'] = False

    context = {'form': form}
    data['html_form'] = render_to_string(template_name, context, request=request, )
    return JsonResponse(data)


def company_create(request):
    if request.method == "POST":
        form = LclCompanyForm(request.POST)
    else:
        form = LclCompanyForm()

    return save_company_form(request, form, 'company/lcl_company_create.html')


def company_update(request, pk):
    company = get_object_or_404(LclCompanyModel, pk=pk)
    if request.method == "POST":
        form = LclCompanyForm(request.POST, instance=company)
    else:
        form = LclCompanyForm(instance=company)

    return save_company_form(request, form, 'company/lcl_company_update.html')


# LCL 燃油费列表
class LclFuelSurchargeListView(ListView):
    ordering = ["-begin_date", ]
    model = LclFuelChargeModel
    template_name = 'lcl_fuel_surcharge_list.html'
    paginate_by = EACH_PAGE

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_active'] = 'LCL_DATA'
        context['page_tab'] = 1
        context['menu_grant'] = get_user_grant_list(self.request.user.id)
        context['company_code'] = self.request.GET.get('company_code', '')
        context['company_name'] = self.request.GET.get('company_name', '')
        return context

    def get_queryset(self):
        query_code = self.request.GET.get('company_code', '')
        query_name = self.request.GET.get('company_name', '')
        result = LclFuelChargeModel.objects.filter(company_code__name__icontains=query_name,
                                                   company_code__code__icontains=query_code,
                                                   )

        return result


def save_fuel_form(request, form, template_name):
    data = dict()
    if request.method == "POST":
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
            fuel_surcharges = LclFuelChargeModel.objects.all()
            data['html_fuel_list'] = render_to_string('fuel_surcharge/partial_fuel_surcharge_list.html',
                                                      {'object_list': fuel_surcharges},
                                                      )
        else:
            data['form_is_valid'] = False

    queryset_company = LclCompanyModel.objects.filter(~Q(code__exact="Public"))
    context = {'form': form, 'all_company': queryset_company}
    data['html_form'] = render_to_string(template_name, context, request=request, )

    return JsonResponse(data)


def fuel_surcharge_create(request):
    if request.method == "POST":
        form = LclFuelSurchargeForm(request.POST)
    else:
        # 初始化日期
        year = datetime.date.today().strftime("%Y")
        month = datetime.date.today().strftime("%m")
        this_month_first_day = datetime.datetime.strptime(year + "-" + month + "-01", "%Y-%m-%d")
        this_month_first_day = this_month_first_day.strftime("%Y-%m-%d")
        next_month_first_day = datetime.datetime.strptime(year + "-" + str(int(month) + 1) + "-01", "%Y-%m-%d")
        this_month_last_day = (next_month_first_day + datetime.timedelta(-1)).strftime("%Y-%m-%d")
        queryset_company = LclCompanyModel.objects.filter(~Q(code__exact='Public'))
        company_code = queryset_company[0].code + " - " + queryset_company[0].name

        form = LclFuelSurchargeForm(initial={'begin_date': this_month_first_day,
                                             'expire_date': this_month_last_day,
                                             'company_code': company_code,
                                             })

    return save_fuel_form(request, form, 'fuel_surcharge/lcl_fuel_surcharge_create.html')


def fuel_surcharge_update(request, pk, slug):
    fuel_surcharge = get_object_or_404(LclFuelChargeModel, company_code_id=pk, begin_date=slug)
    if request.method == "POST":
        form = LclFuelSurchargeForm(request.POST, instance=fuel_surcharge)
    else:
        form = LclFuelSurchargeForm(instance=fuel_surcharge)

    return save_fuel_form(request, form, 'fuel_surcharge/lcl_fuel_surcharge_update.html')
