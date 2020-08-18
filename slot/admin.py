from django.contrib import admin
from .models import Haulier, WarehouseProfile, FixWeekday, Warehouse


# Register your models here.
admin.site.register(Haulier)
admin.site.register(WarehouseProfile)
admin.site.register(FixWeekday)
admin.site.register(Warehouse)



