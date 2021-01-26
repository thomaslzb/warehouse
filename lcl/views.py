from django.shortcuts import render

# Create your views here.
from django.views import View

from air_freight.views import digit_postcode, string_postcode
from .models import LclZoneDetail, LclCompany


def get_zone_id(company_code, postcode):
    """
    获取 zonal 的 zone_id
    """
    zone_id = 0
    postcode_digit = digit_postcode(postcode)
    str_postcode = string_postcode(postcode)

    if company_code == "24HOURS":
        queryset = LclZoneDetail.objects.filter(begin__icontains=str_postcode, end__icontains=str_postcode)
    else:
        queryset = LclZoneDetail.objects.filter(begin__icontains=str_postcode, end__icontains=str_postcode)
    for record in queryset:
        if digit_postcode(record.begin) <= postcode_digit <= digit_postcode(record.end):
            zone_id = record.zone_id
            break

    return zone_id


def calc_volume(company_code, weight, volume):
    CalcVolume = volume
    if company_code == "Public" or company_code == "GMA":
        InputWeight = weight * 0.0023
        if CalcVolume < InputWeight:
            CalcVolume = InputWeight

    return CalcVolume


def CalcResult(company_code, service_code, volume, weight, postcode, pallet_qty):

    return 0


class LclView(View):
    def get(self, request):
        return render(request, 'lcl_calculation.html', {'menu_active': 'LCL', }, )

    def post(self, request):
        volume = float(request.POST.get("volume", 0))
        weight = float(request.POST.get("weight", 0))
        pallet_qty = float(request.POST.get("qty", 0))
        uk_postcode = request.POST.get("postcode", "")

        postcode = (uk_postcode[:-3]).strip().upper()
        # zone_id = get_zone_id(quote_type, postcode)
        # zone_id = 1
        # if zone_id == 0:
        #     # 返回错误，邮编不存在
        #     return render(request, 'lcl_calculation.html', {'menu_active': 'LCL',
        #                                                     'qty': pallet_qty,
        #                                                     'volume': volume,
        #                                                     'weight': weight,
        #                                                     'uk_postcode': uk_postcode,
        #                                                     'uk_area': uk_area,
        #                                                     'error': 'Postcode can not be found.',
        #                                                     'zone_id': 0,
        #                                                     })

        uk_area = ""
        sales_price = 0
        gma = 0
        as_london = 0
        bennetts = 0
        bartrums_express = 0
        bartrums_economy = 0
        anglia_next_day = 0
        anglia_economy = 0

        company_query = LclCompany.objects.all()
        for record in company_query:
            company_code = record.code.strip()
            service_code = ""
            if company_code == "Public":
                sales_price = "£" + '%.2f' % \
                              CalcResult(company_code, service_code, volume, weight, postcode, pallet_qty)
            if company_code == "GMA":
                uk_area = ""
                gma = "£" + '%.2f' % \
                      CalcResult("GMA", volume, service_code, weight, postcode, pallet_qty)
            if company_code == "ASLONDON":
                as_london = "£" + '%.2f' % \
                            CalcResult(company_code, service_code, volume, weight, postcode, pallet_qty)
            if company_code == "BENNETTS":
                bennetts = "£" + '%.2f' % \
                           CalcResult(company_code, service_code, volume, weight, postcode, pallet_qty)
            if company_code == "BARTRUMS":
                service_code = "EXPRESS"
                bartrums_express = "£" + '%.2f' % \
                                   CalcResult(company_code, service_code, volume, weight, postcode, pallet_qty)

                service_code = "ECONOMY"
                bartrums_economy = "£" + '%.2f' % \
                                   CalcResult(company_code, service_code, volume, weight, postcode, pallet_qty)
            if company_code == "ANGLIA":
                service_code = "NEXT DAY"
                anglia_next_day = "£" + '%.2f' % \
                                  CalcResult(company_code, service_code, volume, weight, postcode, pallet_qty)
                service_code = "ECONOMY"
                anglia_economy = "£" + '%.2f' % \
                                 CalcResult(company_code, service_code, volume, weight, postcode, pallet_qty)
        # 设置返回值
        return render(request, 'lcl_calculation.html', {'menu_active': 'LCL',
                                                        'qty': pallet_qty,
                                                        'volume': volume,
                                                        'weight': weight,
                                                        'uk_postcode': uk_postcode,
                                                        'uk_area': uk_area,
                                                        'sales_price': sales_price,
                                                        'gma': gma,
                                                        'as_london': as_london,
                                                        'bennetts': bennetts,
                                                        'bartrums_express': bartrums_express,
                                                        'bartrums_economy': bartrums_economy,
                                                        'anglia_next_day': anglia_next_day,
                                                        'anglia_economy': anglia_economy,
                                                        }, )
