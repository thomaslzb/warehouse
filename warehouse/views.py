
from django.http import HttpResponse


def hello(request):
    return HttpResponse("Hello DCG, I am Coming...")

