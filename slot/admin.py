from django.contrib import admin
from .models import Haulier, WarehouseProfile, FixWeekday, Warehouse, ProgressRecord


# Register your models here.
# admin.site.register(Haulier)
@admin.register(FixWeekday)
class FixWeekdayAdmin(admin.ModelAdmin):
    list_display = ('Haulier', 'weekday', 'time', 'status', 'op_user', 'op_datetime')
    fk_fields = ('op_user_id',)
    list_per_page = 25


@admin.register(Haulier)
class HaulierAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'contact', 'telephone', 'email', 'is_use', 'op_user', 'op_datetime')
    search_fields = ('code', 'name')
    fk_fields = ('op_user_id',)
    list_per_page = 25


@admin.register(ProgressRecord)
class ProgressReoordAdmin(admin.ModelAdmin):
    list_display = ('deliveryref', 'progress', 'remark', 'op_user', 'op_datetime', 'position', )
    search_fields = ('deliveryref', )
    list_filter = ('progress', 'position')
    fk_fields = ('op_user_id',)
    list_per_page = 25


@admin.register(WarehouseProfile)
class WarehouseProfileAdmin(admin.ModelAdmin):
    list_display = ('position', 'beginworktime', 'overworktime', 'maxslot', 'maxinbound', 'op_user', 'op_datetime')
    list_per_page = 25


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    # def time_display(self, obj):
    #     return obj.slottime.strftime("%H:%M")

    list_display = (
                    'deliveryref', 'workdate', 'slottime', 'vehiclereg',
                    'hailerid', 'status', 'progress', 'havetime', 'position',
                    'remark',
                    )
    list_filter = ('progress', 'havetime', 'status', 'position')
    search_fields = ('deliveryref', )
    date_hierarchy = 'workdate'
    ordering = ('-workdate',)
    list_per_page = 25

    # def slottime(self, ojb):
    #     return obj.
