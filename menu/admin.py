from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Menu, Role, Permission

PER_PAGE = 15


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ('menu_order', 'menu_name', 'node_type', 'menu_url', 'menu_icon', 'parent_id',
                    'level', 'path', )
    ordering = ('menu_order', )
    list_per_page = PER_PAGE


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('role_name', 'role_remark')
    list_per_page = PER_PAGE


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ('role', 'menu', )
    fk_fields = ('role', 'menu_id', )
    list_per_page = PER_PAGE


