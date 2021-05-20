"""warehouse URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from users.views import LoginView
from . import views

urlpatterns = [
    path('', LoginView.as_view(), name="index"),
    path('slot/', include('slot.urls')),
    path('quote/', include('quote.urls')),
    path('dcgadmin/', admin.site.urls),
    path("user/", include('users.urls')),
    path("sku/", include('sku.urls')),
    path('captcha/', include('captcha.urls')),
    path('lcl/', include('lcl.urls')),
    path('air_freight/', include('air_freight.urls')),
    path('xiaomi/', include('xiaomi.urls')),
    path('flc/', include('flc.urls')),
    path('testing/', include('testing.urls')),
    path('ocean/', include('ocean.urls')),

    # Third url
    # path('celery-progress/', include('celery_progress.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler400 = views.bad_request
handler403 = views.permission_denied
handler404 = views.page_not_found
handler500 = views.server_error
