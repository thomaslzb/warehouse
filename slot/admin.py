from django.contrib import admin
from .models import Haulier, WarehouseProfile, FixWeekday, Warehouse, ProgressRecord


# Register your models here.
# admin.site.register(Haulier)
@admin.register(FixWeekday)
class FixWeekday(admin.ModelAdmin):
    list_display = ('Haulier', 'weekday', 'time', 'status', 'op_user', 'op_datetime')


@admin.register(Haulier)
class HaulierAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'contact', 'telephone', 'email',)
    search_fields = ('code', 'name')


@admin.register(ProgressRecord)
class ProgressReoord(admin.ModelAdmin):
    list_display = ('deliveryref', 'progress', 'progress_name', 'position', 'remark', 'op_user', 'op_datetime')
    search_fields = ('deliveryref','op_datetime',)


@admin.register(WarehouseProfile)
class WarehouseProfile(admin.ModelAdmin):
    list_display = ('position', 'beginworktime', 'overworktime', 'maxslot', 'maxinbound', 'op_user', 'op_datetime')


@admin.register(Warehouse)
class Warehouse(admin.ModelAdmin):
    list_display = ('deliveryref', 'workdate', 'slottime', 'vehiclereg', 'hailerid', 'status', 'progress', 'havetime', 'position', 'remark',)
    search_fields = ('deliveryref','workdate',)
