from django.contrib import admin
from .models import Sku, SkuFileUpload

PER_PAGE = 18


# Register your models here.
@admin.register(Sku)
class SkuAdmin(admin.ModelAdmin):
    list_display = ('sku_no', 'sku_name', 'sku_length', 'sku_width', 'sku_high', 'sku_weight', 'is_ok', 'last_update')
    list_display_links = ('sku_no', 'sku_name',)
    list_per_page = PER_PAGE


@admin.register(SkuFileUpload)
class SkuFileUploadAdmin(admin.ModelAdmin):
    list_display = ('file_name', 'custom', 'upload_date', 'is_db', 'db_date',)
    list_filter = ('custom', 'is_db',)
    fk_fields = ('custom',)
    ordering = ['upload_date', ]
    list_per_page = PER_PAGE
