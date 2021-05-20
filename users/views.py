# -*- coding: utf-8 -*-
import datetime

from django.db import transaction
from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import auth, messages
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.views.generic.base import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView
from django.contrib.auth.models import User

from captcha.helpers import captcha_image_url
from captcha.models import CaptchaStore

from menu.views import get_user_grant_list
from .models import UserProfile, SlotEmailGroup
from .forms import LoginForm, RegisterForm, ForgetPwdForm, ModifyPwdForm, MyProfileForm, QuoteUserForm, ResetPwdForm
from .forms import SlotUserUpdateForm, SlotUserForm
from .forms import email_check
from django.shortcuts import redirect
from quote.models import Company, UserSetupProfit, UKRange, EuroCountry

MY_MENU_LOCAL = 'MY_PROFILE'


@login_required
def logout(request):
    auth.logout(request)
    return HttpResponseRedirect("/user/login")


@login_required
def pwd_change(request, pk):
    user = get_object_or_404(User, pk=pk)

    if request.method == "POST":
        form = ModifyPwdForm(request.POST)
        if form.is_valid():

            password = form.cleaned_data['old_password']
            username = user.username

            user = auth.authenticate(username=username, password=password)

            if user is not None and user.is_active:
                new_password = form.changed_data['password2']
                user.set_password(new_password)
                user.save()
                return HttpResponseRedirect("user/login")

            else:
                return render(request, 'password_reset.html', {"form": form,
                                                               "user": user,
                                                               "message": "Old password is wrong. Try again",
                                                               'menu_active': 'PA',
                                                               })

    else:
        form = ModifyPwdForm()

    return render(request, 'password_reset.html', {'form': form, 'user': user})


# 用户登录
class LoginView(View):
    def get(self, request):
        # 图片验证码
        # hashkey验证码生成的秘钥，image_url验证码的图片地址
        hashkey = CaptchaStore.generate_key()
        image_url = captcha_image_url(hashkey)
        login_form = LoginForm()
        # Python内置了一个locals()函数，它返回当前所有的本地变量字典
        return render(request, "sign-in.html", locals())

    def post(self, request):
        login_form = LoginForm(request.POST)
        username = request.POST.get("username", "")
        pass_word = request.POST.get("password", "")
        system_name = request.POST.get("system_name", "BOOKING-SYSTEM")
        if login_form.is_valid():
            if email_check(username):
                filter_result = User.objects.filter(email__exact=username)
                if filter_result:
                    username = filter_result[0].username
            else:
                filter_result = User.objects.filter(username__exact=username)
                if filter_result:
                    username = filter_result[0].username
            user = authenticate(username=username, password=pass_word)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    # 分别登陆两个系统
                    if system_name in user.profile.system_menu:
                        if system_name == "BOOKING-SYSTEM":
                            return redirect("slot:slot_list")  # 登陆BOOKING-SYSTEM系统
                        else:
                            return redirect("users:my_profile", pk=user.id)  # 登陆 Quote 系统
                    else:
                        # 直接导向用户可以登录的系统
                        if user.profile.system_menu == "BOOKING-SYSTEM":
                            return redirect("slot:slot_list")  # 登陆BOOKING-SYSTEM系统
                        else:
                            return redirect("users:my_profile", pk=user.id)  # 登陆 Quote 系统
                else:
                    hashkey = CaptchaStore.generate_key()
                    image_url = captcha_image_url(hashkey)
                    msg = "User is be suspend. Please contact system administrator."
                    return render(request, "sign-in.html", locals())
            else:
                # 图片验证码
                # hashkey验证码生成的秘钥，image_url验证码的图片地址
                hashkey = CaptchaStore.generate_key()
                image_url = captcha_image_url(hashkey)
                msg = "Error username or password."
                # Python内置了一个locals()函数，它返回当前所有的本地变量字典
                return render(request, "sign-in.html", locals())
        else:
            hashkey = CaptchaStore.generate_key()
            image_url = captcha_image_url(hashkey)
            # Python内置了一个locals()函数，它返回当前所有的本地变量字典
            return render(request, "sign-in.html", locals())


# 用户注册 - 尚未完成
class RegisterView(View):
    def get(self, request):
        register_form = RegisterForm()
        return render(request, "register.html", {"register_form": register_form})

    def post(self, request):
        register_form = RegisterForm(request.POST)
        if register_form.is_valid():
            user_name = request.POST.get("email", "")
            pass_word = request.POST.get("password", "")

            if UserProfile.objects.filter(email=user_name):
                return render(request, "register.html", {"register_form": register_form, "msg": "email is existed"})

            # send_register_email(user_name, "register")
            return render(request, "register_mail_success.html")
        else:
            return render(request, "register.html", {"register_form": register_form})


# 忘记密码 - 尚未完成
class ForgetPwdView(View):
    def get(self, request):
        forgetpwd_form = ForgetPwdForm()
        return render(request, "forgetpwd.html", {"forgetPwd_form": forgetpwd_form})

    def post(self, request):
        forgetpwd_form = ForgetPwdForm(request.POST)
        if forgetpwd_form.is_valid():
            email = request.POST.get("email", "")
            if not (UserProfile.objects.filter(email=email)):
                return render(request, "forgetpwd.html",
                              {"forgetPwd_form": forgetpwd_form, "msg": "Email address can't be found."})

            # send a new mail for reset password

            # send_register_email(email, "forget")
            return render(request, "send_resetPwd_success.html")
        else:
            return render(request, "forgetpwd.html", {"forgetPwd_form": forgetpwd_form})


# 重置 QUOTE 系统 用户密码
class ResetPwdView(View):
    def get(self, request, pk):
        user = User.objects.get(id=pk)
        return render(request, "user_profile_detail_reset_password.html", {"menu_active": 'USERS',
                                                                           'user': user
                                                                           })

    def post(self, request, pk):
        reset_pwd_form = ResetPwdForm(request.POST)
        user = User.objects.get(id=pk)
        password = request.POST.get("password", "")
        re_password = request.POST.get("re_password", "")
        if reset_pwd_form.is_valid():
            user.set_password(password)
            user.save()
            # return redirect('users:edit_quote_user', pk=pk)
            return render(request, "user_profile_detail_reset_password_success.html",
                          {"menu_active": 'USERS',
                           'menu_grant': get_user_grant_list(request.user.id),
                           'reset_pwd_form': reset_pwd_form,
                           "user": user,
                           'password': password,
                           're_password': re_password,
                           })
        else:
            return render(request, "user_profile_detail_reset_password.html", {"menu_active": 'USERS',
                                                                               'menu_grant': get_user_grant_list(
                                                                                   request.user.id),
                                                                               'reset_pwd_form': reset_pwd_form,
                                                                               "user": user,
                                                                               'password': password,
                                                                               're_password': re_password,
                                                                               })


# 更新 QUOTE system 的用户密码
class ChangeQuoteUserPwdView(View):
    def get(self, request, pk):
        user = User.objects.get(id=pk)
        return render(request, "user_change_password.html", {"menu_active": MY_MENU_LOCAL,
                                                             'menu_grant': get_user_grant_list(request.user.id),
                                                             'user': user,
                                                             })

    def post(self, request, pk):
        old_password = request.POST.get("old_password", "")
        password = request.POST.get("password", "")
        re_password = request.POST.get("re_password", "")
        user = auth.authenticate(username=request.user.username, password=old_password)

        if user is not None and user.is_active:
            new_password = request.POST.get("password", "")
            change_pwd_form = ModifyPwdForm(request.POST)
            if change_pwd_form.is_valid():
                user.set_password(new_password)
                user.save()
                return redirect('users:login')
            else:
                return render(request, "user_change_password.html", {"menu_active": MY_MENU_LOCAL,
                                                                     'menu_grant': get_user_grant_list(request.user.id),
                                                                     'change_pwd_form': change_pwd_form,
                                                                     'message': '',
                                                                     'old_password': old_password,
                                                                     'password': password,
                                                                     're_password': re_password,
                                                                     })

        else:
            return render(request, 'user_change_password.html', {'menu_active': MY_MENU_LOCAL,
                                                                 'menu_grant': get_user_grant_list(request.user.id),
                                                                 "message": "Old password is wrong. Try again",
                                                                 'old_password': old_password,
                                                                 'password': password,
                                                                 're_password': re_password,
                                                                 })


# 退出系统
class LogoutView(View):
    def get(self, request):
        logout(request)
        # 图片验证码
        # hashkey验证码生成的秘钥，image_url验证码的图片地址
        hashkey = CaptchaStore.generate_key()
        image_url = captcha_image_url(hashkey)
        login_form = LoginForm()
        # Python内置了一个locals()函数，它返回当前所有的本地变量字典
        return render(request, "sign-in.html", locals())


# 用户资料
class MyProfile(DetailView):
    model = User
    template_name = 'my_profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_company = Company.objects.all()
        context['menu_active'] = MY_MENU_LOCAL
        context['menu_grant'] = get_user_grant_list(self.request.user.id)
        context['all_company'] = all_company
        return context


# 更新 QUOTE 用户资料
class MyProfileUpdateView(UpdateView):
    model = User
    form_class = MyProfileForm
    template_name = 'my_profile_update.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_company = Company.objects.all()
        context['menu_active'] = MY_MENU_LOCAL
        context['menu_grant'] = get_user_grant_list(self.request.user.id)
        context['all_company'] = all_company
        return context

    def form_invalid(self, form):  # 定义表对象没有添加失败后跳转到的页面。
        response = super().form_invalid(form)
        return response

    def form_valid(self, form):
        user_profile = UserProfile.objects.filter(user_id=self.kwargs['pk'])
        user_profile.update(telephone=form.data['telephone'], favorite_company=form.data['favorite_company'])

        return super(MyProfileUpdateView, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy("users:my_profile", kwargs={'pk': self.object.pk})


# 新增 QUOTE 用户
class AddUserView(View):
    def get(self, request):
        all_company = Company.objects.all()
        return render(request, "add_user_profile.html", {'menu_active': 'USERS',
                                                         'menu_grant': get_user_grant_list(request.user.id),
                                                         'all_company': all_company,
                                                         })

    def post(self, request):
        user_form = QuoteUserForm(request.POST)
        all_company = Company.objects.all()
        if not user_form.is_valid():
            return render(request, "add_user_profile.html", {'user_form': user_form,
                                                             'menu_active': 'USERS',
                                                             'menu_grant': get_user_grant_list(request.user.id),
                                                             'all_company': all_company,
                                                             })
        # 新增记录, 需要写2个表 auth_user, users_userprofile
        # auth_user默认值设置
        # user.is_staff = 0 不是staff
        # user.is_active = 1 是
        # user.is_superuser = 0 不是

        uk_range = UKRange.objects.all()
        euro_country = EuroCountry.objects.all()

        # get all data from user_form
        email = request.POST.get("email", "")

        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        telephone = request.POST.get('telephone', '')
        permission = "000000000000"

        booking_system = request.POST.get("booking_system", "")
        quote_system = request.POST.get("quote_system", "")
        if booking_system and quote_system:
            system_menu = "BOOKING-SYSTEM|QUOTE-SYSTEM"
        else:
            if booking_system:
                system_menu = "BOOKING-SYSTEM"
            else:
                system_menu = "QUOTE-SYSTEM"
        # 新增用户
        with transaction.atomic():
            User.objects.create(username=username,
                                email=email,
                                first_name=first_name,
                                last_name=last_name,
                                is_staff=0,
                                is_active=1,
                                is_superuser=0,
                                last_login=timezone.now(),
                                date_joined=timezone.now(),
                                )
        # 保存密码
        user = User.objects.get(username__exact=username)
        if user is not None and user.is_active:
            password = request.POST.get('password')
            user.set_password(password)
            user.save()

        # 新增用户附加资料
        uk_percent = 0
        uk_fix_amount = 0

        euro_percent = 0
        euro_fix_amount = 0

        fav_company = 1  # 默认用户最喜爱的公司为1 - PARCEL FORCE

        with transaction.atomic():  # 新增用户附加资料 users_userprofile
            UserProfile.objects.create(user_id=user.id,
                                       telephone=telephone,
                                       mod_date=datetime.datetime.now(),
                                       staff_role=0,
                                       favorite_company_id=fav_company,
                                       euro_fix_amount=euro_fix_amount,
                                       euro_percent=euro_percent,
                                       uk_fix_amount=uk_fix_amount,
                                       uk_percent=uk_percent,
                                       menu_grant=permission,
                                       system_menu=system_menu,
                                       )
        with transaction.atomic():
            for uk in uk_range:  # 英国本地的利润率 新增用户的利润设置表 q_user_setup_profit
                UserSetupProfit.objects.create(is_uk='UK',
                                               fix_amount=uk_fix_amount,
                                               percent=uk_percent,
                                               uk_area_id=uk.id,
                                               user_id=user.id,
                                               )

            for euro in euro_country:  # 欧洲的利润率，新增用户的利润设置表 q_user_setup_profit
                UserSetupProfit.objects.create(is_uk='EURO',
                                               fix_amount=euro_fix_amount,
                                               percent=euro_percent,
                                               euro_area_id=euro.id,
                                               user_id=user.id,
                                               )

        return HttpResponseRedirect(reverse('quote:user-list'))


# 编辑 QUOTE 用户
class EditUserView(View):
    def get(self, request, pk):
        all_company = Company.objects.all()
        user = User.objects.get(id=pk)
        return render(request, "user_profile_detail.html", {'menu_active': 'USERS',
                                                            'menu_grant': get_user_grant_list(request.user.id),
                                                            'all_company': all_company,
                                                            'user': user,
                                                            })

    def post(self, request):
        user_form = QuoteUserForm(request.POST)
        all_company = Company.objects.all()
        if not user_form.is_valid():
            return render(request, "add_user_profile.html", {'user_form': user_form,
                                                             'menu_active': 'USERS',
                                                             'menu_grant': get_user_grant_list(request.user.id),
                                                             'all_company': all_company,
                                                             })
        # # 新增记录, 需要写3个表 auth_user, users_userprofile, q_user_setup_profit
        # # auth_user默认值设置
        # # user.is_staff = 0 不是staff
        # # user.is_active = 1 是
        # # user.is_superuser = 0 不是
        #
        # uk_range = UKRange.objects.all()
        # euro_country = EuroCountry.objects.all()
        #
        # # get all data from user_form
        # email = request.POST.get("email", "")
        #
        # username = request.POST.get('username')
        # first_name = request.POST.get('first_name')
        # last_name = request.POST.get('last_name')
        # telephone = request.POST.get('telephone', 0)
        # role = int(request.POST.get('role'))
        # fav_company = request.POST.get('fav_company')
        # uk_mode = request.POST.get('uk_mode')
        # uk_value = float(request.POST.get('uk_value'))
        # euro_mode = request.POST.get('euro_mode')
        # euro_value = float(request.POST.get('euro_value'))
        #
        # # 新增用户
        # with transaction.atomic():
        #     User.objects.create(username=username,
        #                         email=email,
        #                         first_name=first_name,
        #                         last_name=last_name,
        #                         is_staff=0,
        #                         is_active=1,
        #                         is_superuser=0,
        #                         last_login=timezone.now(),
        #                         date_joined=timezone.now(),
        #                         )
        # # 保存密码
        # user = User.objects.get(username__exact=username)
        # if user is not None and user.is_active:
        #     password = request.POST.get('password')
        #     user.set_password(password)
        #     user.save()
        #
        # # 新增用户附加资料
        # if uk_mode == '0':  # fix_amount
        #     uk_fix_amount = uk_value
        #     uk_percent = 0
        # else:
        #     uk_fix_amount = 0
        #     uk_percent = uk_value
        #
        # if euro_mode == '0':  # fix_amount
        #     euro_fix_amount = euro_value
        #     euro_percent = 0
        # else:
        #     euro_fix_amount = 0
        #     euro_percent = euro_value
        #
        # fav_company = Company.objects.get(name__exact=fav_company)
        #
        # with transaction.atomic():
        #     UserProfile.objects.create(user_id=user.id,
        #                                telephone=telephone,
        #                                mod_date=datetime.datetime.now(),
        #                                staff_role=0,
        #                                role_id=role,
        #                                favorite_company=fav_company,
        #                                euro_fix_amount=euro_fix_amount,
        #                                euro_percent=euro_percent,
        #                                uk_fix_amount=uk_fix_amount,
        #                                uk_percent=uk_percent,
        #                                )
        # with transaction.atomic():
        #     for uk in uk_range:
        #         UserSetupProfit.objects.create(is_uk='UK',
        #                                        fix_amount=uk_fix_amount,
        #                                        percent=uk_percent,
        #                                        uk_area_id=uk.id,
        #                                        user_id=user.id,
        #                                        )
        #
        #     for euro in euro_country:
        #         UserSetupProfit.objects.create(is_uk='EURO',
        #                                        fix_amount=euro_fix_amount,
        #                                        percent=euro_percent,
        #                                        euro_area_id=euro.id,
        #                                        user_id=user.id,
        #                                        )

        return HttpResponseRedirect(reverse('quote:user-list'))


# 修改 QUOTE 的用户菜单的权限
class SetUserPermissionView(View):
    def get(self, request, pk):
        user = User.objects.get(id=pk)
        permission_list = get_user_grant_list(pk)
        return render(request, "user_set_permission.html", {'menu_active': 'USERS',
                                                            'menu_grant': get_user_grant_list(request.user.id),
                                                            'user': user,
                                                            'permission_list': permission_list,
                                                            })

    def post(self, request, pk):
        booking_system = request.POST.get("booking_system", "0")
        quote_system = request.POST.get("quote_system", "0")
        express_price = request.POST.get("express_price", "0")
        sku_list = request.POST.get("sku_list", "0")
        air_freight = request.POST.get("air_freight", "0")
        lcl_price = request.POST.get("lcl_price", "0")
        user_maintenance = request.POST.get("user_maintenance", "0")
        xiaomi_bill = request.POST.get("xiaomi_bill", "0")

        lcl_data_maintenance = request.POST.get("lcl_data_maintenance", "0")
        flc_quote = request.POST.get("flc_quote", "0")
        flc_data_maintenance = request.POST.get("flc_data_maintenance", "0")
        ocean_quote = request.POST.get("ocean_quote", "0")

        permission_string = express_price + sku_list + air_freight + lcl_price + user_maintenance + xiaomi_bill \
                            + lcl_data_maintenance + flc_quote + flc_data_maintenance + ocean_quote + "0000"

        booking_system_string = ""
        if booking_system == "1":
            booking_system_string = "BOOKING-SYSTEM"

        quote_system_string = ""
        if quote_system == "1":
            quote_system_string = "QUOTE-SYSTEM"
        if booking_system_string and quote_system_string:
            system_menu = booking_system_string + "|" + quote_system_string
        else:
            system_menu = booking_system_string + quote_system_string

        permission_queryset = UserProfile.objects.filter(user_id=pk)

        if permission_queryset[0].staff_role == 0:
            staff_role = 1
        else:
            staff_role = permission_queryset[0].staff_role

        if permission_queryset:
            permission_queryset.update(menu_grant=permission_string,
                                       system_menu=system_menu,
                                       staff_role=staff_role,
                                       )

        return redirect("users:edit_quote_user", pk=pk)


# 显示 Slot 用户资料
class SlotUserProfile(DetailView):
    model = User
    template_name = 'slot_user_profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        email_group_queryset = SlotEmailGroup.objects.filter(position__exact=self.request.user.profile.op_position)
        context['all_email_group'] = email_group_queryset
        context['menu_grant'] = get_user_grant_list(self.request.user.id, "BOOKING-SYSTEM")
        context['page_tab'] = 3
        return context


# 更新 Slot 用户资料
class SlotUserProfileUpdateView(UpdateView):
    model = User
    form_class = SlotUserUpdateForm
    template_name = 'slot_user_profile_update.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        email_group_queryset = SlotEmailGroup.objects.filter(position__exact=self.request.user.profile.op_position)
        context['all_email_group'] = email_group_queryset
        context['menu_grant'] = get_user_grant_list(self.request.user.id, "BOOKING-SYSTEM")
        context['page_tab'] = 3
        return context

    def form_invalid(self, form):  # 定义表对象没有添加失败后跳转到的页面。
        response = super().form_invalid(form)
        return response

    def form_valid(self, form):
        user_profile = UserProfile.objects.filter(user_id=self.kwargs['pk'])
        user_profile.update(telephone=form.data['telephone'])
        user_profile.update(staff_role=form.data['role'])
        user_profile.update(email_group_id=form.data['email_group'])

        return super(SlotUserProfileUpdateView, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy("users:slot_user_profile", kwargs={'pk': self.object.pk})


# 更新 SLOT 的用户密码
class ChangeSlotUserPwdView(View):
    def get(self, request, pk, ):
        user = User.objects.get(id=pk)
        parameter = {'user': user,
                     "page_tab": 3,
                     'menu_grant': get_user_grant_list(
                         request.user.id, "BOOKING-SYSTEM"),
                     }
        return render(request, "slot_user_change_password.html", parameter)
        # return render(request, "slot_user_change_password.html", change_pwd_get(request, pk, 1))

    def post(self, request, pk):
        username = request.POST.get("username", "")
        old_password = request.POST.get("old_password", "")
        password = request.POST.get("password", "")
        re_password = request.POST.get("re_password", "")

        # 需要在这里分别处理， 如果是经理修改其它用户的密码， 这不需要验证原密码，用户自己修改密码，则需要验证原密码
        if request.user.profile.staff_role == 3 and request.user.username != username:
            user = User.objects.filter(username__exact=username)[0]
        else:
            user = auth.authenticate(username=request.user.username, password=old_password)

        if user is not None and user.is_active:
            new_password = request.POST.get("password", "")
            change_pwd_form = ModifyPwdForm(request.POST)
            if change_pwd_form.is_valid():
                user.set_password(new_password)
                user.save()
                # Python内置了一个locals()函数，它返回当前所有的本地变量字典
                if request.user.username == username:
                    return redirect("users:login")
                else:
                    return redirect("users:slot_user_update", pk=user.id)
            else:
                return render(request, 'slot_user_change_password.html', {"message": "",
                                                                          'old_password': old_password,
                                                                          'password': password,
                                                                          're_password': re_password,
                                                                          'change_pwd_form': change_pwd_form,
                                                                          'user': user,
                                                                          "page_tab": 3,
                                                                          'menu_grant': get_user_grant_list(
                                                                              request.user.id, "BOOKING-SYSTEM"),
                                                                          })

        else:
            user = User.objects.filter(id=request.user.id)[0]
            return render(request, 'slot_user_change_password.html', {"message": "Old password is wrong. Try again",
                                                                      'old_password': old_password,
                                                                      'password': password,
                                                                      're_password': re_password,
                                                                      'user': user,
                                                                      "page_tab": 3,
                                                                      'menu_grant': get_user_grant_list(
                                                                          request.user.id, "BOOKING-SYSTEM"),
                                                                      })


# 新增SLOT的用户
class SlotAddUserView(View):
    def get(self, request):
        all_email_group = SlotEmailGroup.objects.filter(~Q(id=1), position__exact=request.user.profile.op_position)
        return render(request, "slot_add_user_profile.html", {"page_tab": 3,
                                                              'menu_grant': get_user_grant_list(
                                                                  request.user.id, "BOOKING-SYSTEM"),
                                                              "all_email_group": all_email_group,
                                                              })

    def post(self, request):
        user_form = SlotUserForm(request.POST)
        all_email_group = SlotEmailGroup.objects.filter(~Q(id=1), position__exact=request.user.profile.op_position)
        if not user_form.is_valid():
            return render(request, "slot_add_user_profile.html", {'user_form': user_form,
                                                                  "page_tab": 3,
                                                                  'menu_grant': get_user_grant_list(request.user.id,
                                                                                                    "BOOKING-SYSTEM"),
                                                                  'all_email_group': all_email_group,
                                                                  })
        # 新增记录, 需要写2个表 auth_user, users_userprofile
        # auth_user默认值设置
        # user.is_staff = 0 不是staff
        # user.is_active = 1 是
        # user.is_superuser = 0 不是

        # get all data from user_form
        email = request.POST.get("email", "")

        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        telephone = request.POST.get('telephone', 0)
        email_group = request.POST.get('email_group')
        role = request.POST.get('role')
        status = request.POST.get('status', 0)

        # 经理级别的可以增加，修改，暂停
        permission = "11111111111111111"  # 系统权限默认值，目前没有用，主要是用经理级别来控制，系统从第二位开始判断
        # 新增用户
        with transaction.atomic():
            User.objects.create(username=username,
                                email=email,
                                first_name=first_name,
                                last_name=last_name,
                                is_staff=0,
                                is_active=status,
                                is_superuser=0,
                                last_login=timezone.now(),
                                date_joined=timezone.now(),
                                )
        # 保存密码
        user = User.objects.get(username__exact=username)
        if user is not None and user.is_active:
            password = request.POST.get('password')
            user.set_password(password)
            user.save()

        # 新增用户附加资料
        uk_percent = 0
        uk_fix_amount = 0

        euro_percent = 0
        euro_fix_amount = 0

        fav_company = 1  # 默认用户最喜爱的公司为1 - PARCEL FORCE

        with transaction.atomic():  # 新增用户附加资料 users_userprofile
            UserProfile.objects.create(user_id=user.id,
                                       telephone=telephone,
                                       mod_date=datetime.datetime.now(),
                                       email_group_id=email_group,
                                       staff_role=role,
                                       favorite_company_id=fav_company,
                                       euro_fix_amount=euro_fix_amount,
                                       euro_percent=euro_percent,
                                       uk_fix_amount=uk_fix_amount,
                                       uk_percent=uk_percent,
                                       op_position=request.user.profile.op_position,
                                       menu_grant=permission,
                                       system_menu='SLOT',
                                       )

        return HttpResponseRedirect(reverse('slot:slot_user_list'))
