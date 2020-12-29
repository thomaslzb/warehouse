from django.shortcuts import render

# Create your views here.
from django.views import View


class LclView(View):
    def get(self, request):
        return render(request, 'lcl_input.html', {'menu_active': 'LCL', }, )
