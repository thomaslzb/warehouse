from django.contrib import admin
from .models import Sku

PER_PAGE = 18


# Register your models here.
@admin.register(Sku)
class SkuAdmin(admin.ModelAdmin):
    list_display = ('sku_no', 'sku_name', 'sku_length', 'sku_width', 'sku_high', 'sku_weight', 'is_ok', 'last_update')
    list_display_links = ('sku_no', 'sku_name',)
    list_per_page = PER_PAGE
