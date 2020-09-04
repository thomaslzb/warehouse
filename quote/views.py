from django.shortcuts import render


# Create your views here.
def index(request):
    return render(request, 'base-menu.html')
    # return render(request, 'input_data.html')
