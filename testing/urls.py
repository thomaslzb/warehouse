"""progress_bar_demo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import url
from django.contrib import admin
from django.urls import path

from testing.views import process_data, show_progress, show_progress_page, TestView, new_main_page, demo

app_name = 'testing'

urlpatterns = [
    path('show_progress_page/', show_progress_page, name='show_progress_page'),
    path('process_data/', process_data, name='process_data'),
    path('show_progress/', show_progress, name='show_progress'),

    path('test/', TestView.p1, name='test_pop'),
    path('test/test1/', TestView.p2, name='pop_windows'),

    path('new/', new_main_page, name='new_start'),
    path('demo/', demo, name='demo'),

]
