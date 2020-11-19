# -*- coding: utf-8 -*-
import datetime

from django.db import transaction
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.views.generic.base import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, CreateView
from django.contrib.auth.models import User

from captcha.helpers import captcha_image_url
from captcha.models import CaptchaStore

from .models import EmailVerifyRecord, UserProfile
from .forms import LoginForm, RegisterForm, ForgetPwdForm, ModifyPwdForm, MyProfileForm, QuoteUserForm, ResetPwdForm
from .forms import email_check
from django.shortcuts import redirect
from quote.models import Company, UserSetupProfit, UKRange, EuroCountry

# from utils import send_register_email

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


class LoginView(View):
    def get(self, request):
        # 图片验证码
        # hashkey验证码生成的秘钥，image_url验证码的图片地址
        hashkey = CaptchaStore.generate_key()
        image_url = captcha_image_url(hashkey)
        login_form = LoginForm()
        # Python内置了一个locals()函数，它返回当前所有的本地变量字典
        return render(request, "sign-in.html", locals())
        # return render(request, "sign-in.html", {})

    def post(self, request):
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            input_username = request.POST.get("username", "")
            pass_word = request.POST.get("password", "")

            if email_check(input_username):
                filter_result = User.objects.filter(email__exact=input_username)
                if filter_result:
                    username = filter_result[0].username
            else:
                filter_result = User.objects.filter(username__exact=input_username)
                if filter_result:
                    username = filter_result[0].username
            user = authenticate(username=username, password=pass_word)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    abc = user.profile.staff_role
                    if user.profile.staff_role != 0:
                        return redirect("/slot/list")
                    else:
                        return redirect("/quote/uk")
                else:
                    return render(request, "sign-in.html", {"form": "User is not be Activated!"})
            else:
                # 图片验证码
                # hashkey验证码生成的秘钥，image_url验证码的图片地址
                hashkey = CaptchaStore.generate_key()
                image_url = captcha_image_url(hashkey)
                login_form = LoginForm()
                # Python内置了一个locals()函数，它返回当前所有的本地变量字典
                msg = 'Password is not correct.!'
                return render(request, "sign-in.html", locals(), )
        else:
            msg = login_form.errors
            if "username" in msg:
                msg = "This email or username does not exist."

            if "captcha" in msg:
                msg = "Invalid CAPTCHA"

            hashkey = CaptchaStore.generate_key()
            image_url = captcha_image_url(hashkey)
            login_form = LoginForm()
            # Python内置了一个locals()函数，它返回当前所有的本地变量字典
            return render(request, "sign-in.html", locals(), )


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
                           'reset_pwd_form': reset_pwd_form,
                           "user": user,
                           'password': password,
                           're_password': re_password,
                           })
        else:
            return render(request, "user_profile_detail_reset_password.html", {"menu_active": 'USERS',
                                                                               'reset_pwd_form': reset_pwd_form,
                                                                               "user": user,
                                                                               'password': password,
                                                                               're_password': re_password,
                                                                               })


class ChangePwdView(View):
    def get(self, request, pk):
        user = User.objects.get(id=pk)
        return render(request, "user_change_password.html", {"menu_active": MY_MENU_LOCAL,
                                                             'user': user
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
                hashkey = CaptchaStore.generate_key()
                image_url = captcha_image_url(hashkey)
                login_form = LoginForm()
                # Python内置了一个locals()函数，它返回当前所有的本地变量字典
                return render(request, "sign-in.html", locals(), )
            else:
                return render(request, "user_change_password.html", {"menu_active": MY_MENU_LOCAL,
                                                                     'change_pwd_form': change_pwd_form,
                                                                     'message': '',
                                                                     'old_password': old_password,
                                                                     'password': password,
                                                                     're_password': re_password,
                                                                     })

        else:
            return render(request, 'user_change_password.html', {'menu_active': MY_MENU_LOCAL,
                                                                 "message": "Old password is wrong. Try again",
                                                                 'old_password': old_password,
                                                                 'password': password,
                                                                 're_password': re_password,
                                                                 })


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


class MyProfile(DetailView):
    model = User
    template_name = 'my_profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_company = Company.objects.all()
        context['menu_active'] = MY_MENU_LOCAL
        context['all_company'] = all_company
        return context


class MyProfileUpdateView(UpdateView):
    model = User
    form_class = MyProfileForm
    template_name = 'my_profile_update.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_company = Company.objects.all()
        context['menu_active'] = MY_MENU_LOCAL
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


class AddUserView(View):
    def get(self, request):
        all_company = Company.objects.all()
        return render(request, "add_user_profile.html", {'menu_active': 'USERS',
                                                         'all_company': all_company,
                                                         })

    def post(self, request):
        user_form = QuoteUserForm(request.POST)
        all_company = Company.objects.all()
        if not user_form.is_valid():
            return render(request, "add_user_profile.html", {'user_form': user_form,
                                                             'menu_active': 'USERS',
                                                             'all_company': all_company,
                                                             })
        # 新增记录, 需要写3个表 auth_user, users_userprofile, q_user_setup_profit
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
        telephone = request.POST.get('telephone', 0)
        role = int(request.POST.get('role'))
        fav_company = request.POST.get('fav_company')
        uk_mode = request.POST.get('uk_mode')
        uk_value = float(request.POST.get('uk_value'))
        euro_mode = request.POST.get('euro_mode')
        euro_value = float(request.POST.get('euro_value'))

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
        if uk_mode == '0':  # fix_amount
            uk_fix_amount = uk_value
            uk_percent = 0
        else:
            uk_fix_amount = 0
            uk_percent = uk_value

        if euro_mode == '0':  # fix_amount
            euro_fix_amount = euro_value
            euro_percent = 0
        else:
            euro_fix_amount = 0
            euro_percent = euro_value

        fav_company = Company.objects.get(name__exact=fav_company)

        with transaction.atomic():
            UserProfile.objects.create(user_id=user.id,
                                       telephone=telephone,
                                       mod_date=datetime.datetime.now(),
                                       staff_role=0,
                                       role_id=role,
                                       favorite_company=fav_company,
                                       euro_fix_amount=euro_fix_amount,
                                       euro_percent=euro_percent,
                                       uk_fix_amount=uk_fix_amount,
                                       uk_percent=uk_percent,
                                       )
        with transaction.atomic():
            for uk in uk_range:
                UserSetupProfit.objects.create(is_uk='UK',
                                               fix_amount=uk_fix_amount,
                                               percent=uk_percent,
                                               uk_area_id=uk.id,
                                               user_id=user.id,
                                               )

            for euro in euro_country:
                UserSetupProfit.objects.create(is_uk='EURO',
                                               fix_amount=euro_fix_amount,
                                               percent=euro_percent,
                                               euro_area_id=euro.id,
                                               user_id=user.id,
                                               )

        return HttpResponseRedirect(reverse('user-list'))


class EditUserView(View):
    def get(self, request, pk):
        all_company = Company.objects.all()
        user = User.objects.get(id=pk)
        return render(request, "user_profile_detail.html", {'menu_active': 'USERS',
                                                            'all_company': all_company,
                                                            'user': user,
                                                            })

    def post(self, request):
        user_form = QuoteUserForm(request.POST)
        all_company = Company.objects.all()
        # workdate = request.POST.get("workdate", datetime.datetime.now())  # 抵达日期
        if not user_form.is_valid():
            return render(request, "add_user_profile.html", {'user_form': user_form,
                                                             'menu_active': 'USERS',
                                                             'all_company': all_company,
                                                             })
        # 新增记录, 需要写3个表 auth_user, users_userprofile, q_user_setup_profit
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
        telephone = request.POST.get('telephone', 0)
        role = int(request.POST.get('role'))
        fav_company = request.POST.get('fav_company')
        uk_mode = request.POST.get('uk_mode')
        uk_value = float(request.POST.get('uk_value'))
        euro_mode = request.POST.get('euro_mode')
        euro_value = float(request.POST.get('euro_value'))

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
        if uk_mode == '0':  # fix_amount
            uk_fix_amount = uk_value
            uk_percent = 0
        else:
            uk_fix_amount = 0
            uk_percent = uk_value

        if euro_mode == '0':  # fix_amount
            euro_fix_amount = euro_value
            euro_percent = 0
        else:
            euro_fix_amount = 0
            euro_percent = euro_value

        fav_company = Company.objects.get(name__exact=fav_company)

        with transaction.atomic():
            UserProfile.objects.create(user_id=user.id,
                                       telephone=telephone,
                                       mod_date=datetime.datetime.now(),
                                       staff_role=0,
                                       role_id=role,
                                       favorite_company=fav_company,
                                       euro_fix_amount=euro_fix_amount,
                                       euro_percent=euro_percent,
                                       uk_fix_amount=uk_fix_amount,
                                       uk_percent=uk_percent,
                                       )
        with transaction.atomic():
            for uk in uk_range:
                UserSetupProfit.objects.create(is_uk='UK',
                                               fix_amount=uk_fix_amount,
                                               percent=uk_percent,
                                               uk_area_id=uk.id,
                                               user_id=user.id,
                                               )

            for euro in euro_country:
                UserSetupProfit.objects.create(is_uk='EURO',
                                               fix_amount=euro_fix_amount,
                                               percent=euro_percent,
                                               euro_area_id=euro.id,
                                               user_id=user.id,
                                               )

        return HttpResponseRedirect(reverse('user-list'))
