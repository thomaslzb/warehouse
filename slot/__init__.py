from django.apps import AppConfig
import os

default_app_config = 'slot.SlotConfig'
VERBOSE_APP_NAME = "Warehouse Manage"


def get_current_app_name(_file):
    return os.path.split(os.path.dirname(_file))[-1]


class SlotConfig(AppConfig):
    name = get_current_app_name(__file__)
    verbose_name = VERBOSE_APP_NAME


