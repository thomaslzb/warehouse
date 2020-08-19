"""
WSGI config for warehouse project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/wsgi/
"""

import os
import sys

from os.path import join, dirname, abspath

PROJECT_DIR = dirname(dirname(abspath(__file__)))

sys.path.insert(0, PROJECT_DIR)

sys.path.append(r"/var/www/warehouse/isoEnv/lib/python3.8/site-packages")

import django.core.handlers.wsgi

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'warehouse.settings')

application = get_wsgi_application()
