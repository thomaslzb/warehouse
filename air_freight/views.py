from django.shortcuts import render

# Create your views here.

from django.views import View


class AirFreightView(View):
    def get(self, request):
        return render(request, 'air_freight.html', {'menu_active': 'AIR', }, )
