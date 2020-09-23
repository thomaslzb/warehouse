# -*- coding: utf-8 -*-
import datetime

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.views.generic.base import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView
from django.contrib.auth.models import User

from captcha.helpers import captcha_image_url
from captcha.models import CaptchaStore

from .models import EmailVerifyRecord, UserProfile
from .forms import LoginForm, RegisterForm, ForgetPwdForm, ModifyPwdForm, ModifyPwdForm, MyProfileForm, UserProfileForm
from django.shortcuts import redirect


# from utils import send_register_email

MY_MENU_LOCAL = 'USER'

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
            InputEmail = request.POST.get("username", "")
            pass_word = request.POST.get("password", "")

            filter_result = User.objects.filter(email__exact=InputEmail)
            if filter_result:
                username = filter_result[0].username
            user = authenticate(username=username, password=pass_word)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    # return render(request, "slotList.html", {"search_date": today})
                    abc = user.profile.staff_role
                    if user.profile.staff_role != 0:
                        today = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d")
                        request.session['searching_date'] = today
                        return redirect("/slot/")
                    else:
                        return redirect("/quote/UK")
                    # return redirect("/slot")

                else:
                    return render(request, "sign-in.html", {"form": "User is Activated!"})
            else:
                # 图片验证码
                # hashkey验证码生成的秘钥，image_url验证码的图片地址
                hashkey = CaptchaStore.generate_key()
                image_url = captcha_image_url(hashkey)
                login_form = LoginForm()
                # Python内置了一个locals()函数，它返回当前所有的本地变量字典
                msg = "UserName or Email or Password isn't correct."
                return render(request, "sign-in.html", locals(), )
                # return render(request, "sign-in.html", {"msg": "UserName or Email or Password isn't correct.", })
        else:
            # 图片验证码
            # hashkey验证码生成的秘钥，image_url验证码的图片地址
            hashkey = CaptchaStore.generate_key()
            image_url = captcha_image_url(hashkey)
            login_form = LoginForm()
            # Python内置了一个locals()函数，它返回当前所有的本地变量字典
            msg = "Captcha isn't Correct."
            return render(request, "sign-in.html", locals())
            # return render(request, "sign-in.html", {"login_form": login_form})


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


class PasswordResetView(View):
    def get(self, request, active_code):
        all_record = EmailVerifyRecord.objects.filter(code=active_code)
        if all_record:
            for record in all_record:
                email = record.email
            return render(request, "password_reset.html", {'email': email})
        else:
            return render(request, "active_failure.html")


class ModifyPwdView(View):
    def post(self, request):
        modifypwdform = ModifyPwdForm(request.POST)
        email = request.POST.get("email", "")
        if modifypwdform.is_valid():
            pass1 = request.POST.get("password1", "")
            pass2 = request.POST.get("password2", "")
            if pass1 != pass2:
                return render(request, "password_reset.html", {"modifypwd_form": modifypwdform,
                                                               "email": email,
                                                               "msg": "The two passwords entered are inconsistent."})
        else:
            return render(request, "password_reset.html", {"modifypwd_form": modifypwdform, "email": email})


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


class MyProfileUpdateView(UpdateView):
    model = User
    form_class = MyProfileForm
    template_name = 'my_profile_update.html'
    success_url = '/quote/users/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_active'] = MY_MENU_LOCAL
        context['form_user_profit'] = UserProfileForm
        return context

    def form_invalid(self, form):  # 定义表对象没有添加失败后跳转到的页面。
        response = super().form_invalid(form)
        return response

    # def form_valid(self, form):
    #     context = self.get_context_data(form=form)
    #     user = form.save()
    #     user_profile = context['form_user_profit'].save(commit=False)
    #     user_profile.telephone = user
    #     user_profile.profit_percent = user
    #     user_profile.save()
    #
    #     return super(MyProfileUpdateView, self).form_valid(form)

