from django.contrib import admin
from .models import Haulier, WarehouseProfile, FixWeekday, Warehouse, ProgressRecord


# Register your models here.
admin.site.register(Haulier)
admin.site.register(WarehouseProfile)
admin.site.register(Warehouse)
admin.site.register(ProgressRecord)
admin.site.register(FixWeekday)



