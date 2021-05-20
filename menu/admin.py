from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Menu

PER_PAGE = 15


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ('menu_name', 'id',  'parent_id', 'level', 'path', 'node_type',
                    'menu_order', 'menu_url', 'menu_icon',)
    ordering = ('menu_order', )
    list_per_page = PER_PAGE

