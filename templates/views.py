from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.


def Home(request):
    context = {'result': 0.0}
    if request.method =='POST':
        length = float(request.POST['length'])
        #Width = float(request.POST['width'])
        #High = float(request.POST['high'])
        #weight = float(request.POST['weight'])
        postcode = request.POST['postcode']
        context['result'] = round(length, 2)
    return render(request, "index.html", context=context)

