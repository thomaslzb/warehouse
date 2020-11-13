import datetime
import math

from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views import View
from django.views.generic import UpdateView
from django.views.generic.list import ListView
from .forms import QuoteUKForm, QuoteEuroForm, UserSetupProfitForm
from .public_func import parcel
from .models import EuroCountry, UserSetupProfit, UKRange, Company
from utils.tools import is_float
from users.models import UserProfile
from django.contrib.auth.models import User

# Create your views here.
# def get_menu(self, request):
#     user_result = UserProfile.objects.filter(user_id=request.user.id)
#     if user_result:
#         role_result = Permission.objects.filter(role__id=user_result[0].role_id)
#         if role_result:
#             render(request, 'base-menu.html', {"all_menu": role_result})
#             return True
#     return False

MY_MENU_LOCAL = 'USERS'
LAST_POSITION = 10


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

            if (not l_hermes[LAST_POSITION]) and (not l_pacelforce[LAST_POSITION]) and \
                    (not l_dhl[LAST_POSITION]) and (not l_dpd[LAST_POSITION]) and (not l_ups[LAST_POSITION]):
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
        all_euro = EuroCountry.objects.all().filter(belong='EURO')
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

            if (not l_pacelforce[LAST_POSITION]) and (not l_dhl[LAST_POSITION]) \
                    and (not l_dpd[LAST_POSITION]) and (not l_ups[LAST_POSITION]):
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


class UserListView(ListView):
    ordering = ["email"]
    model = UserProfile
    template_name = 'users_list.html'
    paginate_by = 15

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_active'] = MY_MENU_LOCAL
        return context

    def get_queryset(self):
        query_username = self.request.GET.get('username')
        query_email = self.request.GET.get('email')
        if query_username and query_email:
            result = UserProfile.objects.filter(user__email__icontains=query_email,
                                                user__username__icontains=query_username,
                                                staff_role__exact=0,
                                                )
        elif query_email:
            result = UserProfile.objects.filter(user__email__icontains=query_email,
                                                staff_role__exact=0,
                                                )
        elif query_username:
            result = UserProfile.objects.filter(user__username__icontains=query_username,
                                                staff_role__exact=0,
                                                )
        else:
            result = UserProfile.objects.filter(staff_role=0)

        return result


class UserSetupProfitView(View):
    def get(self, request, pk):
        user = User.objects.filter(id=pk)[0]  # 获取当前用户的信息
        all_company = Company.objects.all()
        return render(request, 'user_setup_profit.html', {
            'user': user,
            'all_company': all_company,
            'menu_active': MY_MENU_LOCAL,
            'error': '',
        })

    def post(self, request, pk):
        error = ""
        fav_company = int(request.POST.get("fav_company", 1))
        uk_mode = int(request.POST.get("uk_mode", 0))
        uk_value = float(request.POST.get("uk_value", 0))
        euro_mode = int(request.POST.get("euro_mode", 0))
        euro_value = float(request.POST.get("euro_value", 0))

        # if not is_float(uk_value) or not is_float(euro_value):
        #     error = "Input Value Error: Value must be a number."
        # else:
        #     uk_value = float(uk_value)
        #     euro_value = float(euro_value)
        #     if uk_value <= 0 or euro_value <= 0:
        #         error = "Input Value Error: Value can not be less than zero."
        #
        # if error:
        #     user = User.objects.filter(id=pk)[0]  # 获取当前用户的信息
        #     all_company = Company.objects.all()
        #     return render(request, 'user_setup_profit.html', {
        #         'user': user,
        #         'all_company': all_company,
        #         'menu_active': MY_MENU_LOCAL,
        #         'error': error,
        #     })

        if uk_mode == 0:  # by fix amount
            uk_fix = uk_value
            uk_percent = 0
        else:  # by percent
            uk_fix = 0
            uk_percent = uk_value

        if euro_mode == 0:  # by fix amount
            euro_fix = euro_value
            euro_percent = 0
        else:  # by percent
            euro_fix = 0
            euro_percent = euro_value

        """
        更新主要的数据表 userprofile
        """
        user_profile = UserProfile.objects.get(user_id__exact=pk)
        if user_profile:
            user_profile.favorite_company_id = fav_company
            user_profile.uk_fix_amount = uk_fix
            user_profile.uk_percent = uk_percent
            user_profile.euro_fix_amount = euro_fix
            user_profile.euro_percent = euro_percent
            user_profile.save()

        """
        每个用户均有一个国家代码表，因为不同客户每个国家的利润率可能会单独设置
        所以，必须先检查国家的数据是否全部已经保存，如果没有则新增,
        还有一种情况，系统新增了国家代码，所以用户也必须有新增的国家代码的费用设置
        """
        all_country = EuroCountry.objects.all()  # 所有的欧洲国家
        for country in all_country:
            user_profit_queryset = UserSetupProfit.objects.get(user_id__exact=pk, euro_area__id=country.id)
            if user_profit_queryset:
                user_profit_queryset.fix_amount = euro_fix
                user_profit_queryset.percent = euro_percent
            else:
                user_profit_queryset = UserSetupProfit.objects.create(is_uk=country.belong,
                                                                      fix_amount=euro_fix,
                                                                      percent=euro_percent,
                                                                      user_id=int(pk),
                                                                      euro_area_id=country.id)
            user_profit_queryset.save()

        all_uk_range = UKRange.objects.all()  # 所有的英国本土地区
        for uk_area in all_uk_range:
            user_profit_queryset = UserSetupProfit.objects.get(user_id__exact=pk, uk_area__id=uk_area.id)
            if user_profit_queryset:
                user_profit_queryset.fix_amount = uk_fix
                user_profit_queryset.percent = uk_percent
            else:
                user_profit_queryset = UserSetupProfit.objects.create(is_uk='UK',
                                                                      fix_amount=uk_fix,
                                                                      percent=uk_percent,
                                                                      user_id=int(pk),
                                                                      uk_area_id=uk_area.id)
            user_profit_queryset.save()

        return HttpResponseRedirect(reverse('user-list'))


class ProfitDetailListView(ListView):
    model = UserSetupProfit
    template_name = 'user_setup_profit_detail.html'
    ordering = ['is_uk', 'uk_area_id', 'euro_area_id']
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_info = User.objects.get(id=self.kwargs['pk'])
        context['menu_active'] = MY_MENU_LOCAL
        context['user_info'] = user_info
        return context

    def get_queryset(self):
        query_range = self.request.GET.get('range')
        query_region = self.request.GET.get('region')
        if not query_range:
            query_range = 'ALL'

        result = UserSetupProfit.objects.filter(user_id__exact=self.kwargs['pk'])

        if query_region and query_range == 'ALL':
            result = UserSetupProfit.objects.filter(user_id__exact=self.kwargs['pk'],
                                                    euro_area__country__icontains=query_region)

        if not query_region and query_range != 'ALL':
            result = UserSetupProfit.objects.filter(user_id__exact=self.kwargs['pk'], is_uk__exact=query_range)

        if query_region and query_range == 'EURO':
            result = UserSetupProfit.objects.filter(
                user_id__exact=self.kwargs['pk'],
                is_uk__exact=query_range,
                euro_area__country__icontains=query_region,
            )

        if query_region and query_range == 'UK':
            result = UserSetupProfit.objects.filter(
                user_id__exact=self.kwargs['pk'],
                is_uk__exact=query_range,
                uk_area__area__icontains=query_region,
            )

        return result


class ProfitDetailUpdateView(UpdateView):
    model = UserSetupProfit
    template_name = 'user_setup_profit_detail_update.html'
    # fields = ['fix_amount', 'percent', ]
    form_class = UserSetupProfitForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_info = User.objects.get(id=self.kwargs['user_id'])
        context['menu_active'] = MY_MENU_LOCAL
        context['user_info'] = user_info
        return context

    def get_object(self, queryset=None):
        # <user_id>/<euro_id>/<uk_id> /<is_uk>
        if self.kwargs['is_uk'] != 'EURO':
            queryset = get_object_or_404(self.model,
                                         user_id=self.kwargs['user_id'],
                                         uk_area_id=self.kwargs['uk_id'],
                                         is_uk=self.kwargs['is_uk'],
                                         )
        else:
            queryset = get_object_or_404(self.model,
                                         user_id=self.kwargs['user_id'],
                                         euro_area_id=self.kwargs['euro_id'],
                                         is_uk=self.kwargs['is_uk'],
                                         )
        return queryset

    def get_success_url(self):
        return reverse('profit-detail', args=[self.kwargs['user_id'], ])

    def form_invalid(self, form):
        return HttpResponseRedirect(self.get_success_url())

    def form_valid(self, form):
        profit_mode = int(form.data["profit_mode"])
        value = form.data["value"]

        post = form.save(commit=False)
        if profit_mode == 0:
            post.fix_amount = value
            post.percent = 0
        else:
            post.fix_amount = 0
            post.percent = value
        post.save()

        return HttpResponseRedirect(self.get_success_url())
