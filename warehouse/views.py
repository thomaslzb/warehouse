
from django.http import HttpResponse
from django.shortcuts import render


def hello(request):
    return HttpResponse("Hello DCG, I am Coming...")


def bad_request(request, template_name='errors/page_404.html'):   # 400
    return render(request, template_name, status=400)


def permission_denied(request, template_name='errors/page_403.html'):  # 403 - ok
    return render(request, template_name, status=403)


def page_not_found(request, template_name='errors/page_404.html'):  # 404 - ok
    return render(request, template_name, status=404)


def server_error(request, template_name='errors/page_500.html'):  # 500 - ok
    return render(request, template_name, status=500)


