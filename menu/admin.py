from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Menu, Role, Permission, FirstMenu

PER_PAGE = 15


# Register your models here.
@admin.register(FirstMenu)
class FirstMenuAdmin(admin.ModelAdmin):
    list_display = ('menu_order', 'menu_name', 'menu_url', 'menu_remark')
    ordering = ('menu_order', )
    list_per_page = PER_PAGE


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ('first_menu', 'menu_order', 'menu_name', 'menu_url', 'menu_remark')
    ordering = ('first_menu', 'menu_order', )
    list_per_page = PER_PAGE


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('role_name', 'role_remark')
    list_per_page = PER_PAGE


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ('role', 'first_menu', 'menu', 'is_list', 'is_update', 'is_delete',)
    fk_fields = ('role', 'first_menu', 'menu_id', )
    list_per_page = PER_PAGE


