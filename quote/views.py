import datetime
import math

from django.shortcuts import render
from django.views import View
from .forms import QuoteUKForm, QuoteEuroForm
from .public_func import parcel
from .models import EuroCountry


# Create your views here.
# def get_menu(self, request):
#     user_result = UserProfile.objects.filter(user_id=request.user.id)
#     if user_result:
#         role_result = Permission.objects.filter(role__id=user_result[0].role_id)
#         if role_result:
#             render(request, 'base-menu.html', {"all_menu": role_result})
#             return True
#     return False


class QuoteInquireUK(View):
    def get(self, request):
        return render(request, 'inquire_uk.html', {'menu_active': 'UK', })

    def post(self, request):
        quote_uk_form = QuoteUKForm(request.POST)
        if quote_uk_form.is_valid():
            length = int(request.POST.get("length", ""))
            width = int(request.POST.get("width", ""))
            high = int(request.POST.get("high", ""))
            # 确定长，宽，高的正确顺序 length > width > high
            list_sort = [length, width, high]
            list_sort.sort()
            high = list_sort[0]
            width = list_sort[1]
            length = list_sort[2]

            is_uk = True
            weight = math.ceil(float(request.POST.get("weight", "")))
            qty = int(request.POST.get("qty", ""))
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
                                                            'menu_active': 'UK',
                                                            "quote_uk_form": quote_uk_form,
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
                'menu_active': 'UK',
            })
        return render(request, "inquire_uk.html", {
            "quote_uk_form": quote_uk_form,
            'menu_active': 'UK',
            })


class QuoteInquireEuro(View):
    def get(self, request):
        all_euro = EuroCountry.objects.all().order_by('country')
        return render(request, 'inquire_euro.html', {'all_euro': all_euro, 'menu_active': 'EURO', }, )

    def post(self, request):
        all_euro = EuroCountry.objects.all().order_by('country')
        quote_euro_form = QuoteEuroForm(request.POST)
        if quote_euro_form.is_valid():
            is_uk = True
            length = int(request.POST.get("length", ""))
            width = int(request.POST.get("width", ""))
            high = int(request.POST.get("high", ""))
            # 确定长，宽，高的正确顺序 length > width > high
            list_sort = [length, width, high]
            list_sort.sort()
            high = list_sort[0]
            width = list_sort[1]
            length = list_sort[2]

            is_uk = False
            weight = math.ceil(float(request.POST.get("weight", "")))
            qty = int(request.POST.get("qty", 0))
            address_type = request.POST.get("addresstype", "").upper()
            user_id = request.user.id
            postcode = request.POST.get("euro", "")

            company_code = 'PASC'
            l_pacelforce = parcel(company_code, length, width, high, weight, postcode, qty, user_id, is_uk)
            company_code = 'DHL'
            l_dhl = parcel(company_code, length, width, high, weight, postcode, qty, user_id, is_uk)
            company_code = 'DPD'
            l_dpd = parcel(company_code, length, width, high, weight, postcode, qty, user_id, is_uk)
            company_code = 'UPS'
            l_ups = parcel(company_code, length, width, high, weight, postcode, qty, user_id, is_uk)

            if (not l_pacelforce[5]) and (not l_dhl[5]) and (not l_dpd[5]) and (not l_ups[5]):
                return render(request, 'quote_error.html', {'go': 'EURO',
                                                            'length': length,
                                                            'width': width,
                                                            'high': high,
                                                            'weight': weight,
                                                            'qty': qty,
                                                            'postcode': postcode,
                                                            'address_type': address_type,
                                                            'menu_active': 'EURO',
                                                            "quote_euro_form": quote_euro_form,
                                                            })

            l_pacelforce = l_pacelforce[:-1]
            l_dhl = l_dhl[:-1]
            l_dpd = l_dpd[:-1]
            return render(request, 'list_price.html', {
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
                'menu_active': 'EURO',
            })
        return render(request, "inquire_euro.html", {
            "quote_euro_form": quote_euro_form,
            'all_euro': all_euro,
            'menu_active': 'EURO',
        })
