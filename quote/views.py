from django.http import HttpResponseForbidden
from django.shortcuts import render
from django.views import View
from users.models import UserProfile
from menu.models import Permission
from menu.views import get_menu

# Create your views here.
# def index(request):
#     return render(request, 'base-menu.html')
#     # return render(request, 'input_data.html')
#


class QuoteIndex(View):
    def get(self, request):
        if get_menu:
            return render(request, 'base-menu.html',)
        else:
            return HttpResponseForbidden()

    def post(self):
        pass



