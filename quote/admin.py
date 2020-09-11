from django.contrib import admin
from .models import Company, ServiceType, Surcharge, ZoneName, ZoneDetail, ZoneSurcharge, EuroCountry, EuroPrice

PER_PAGE = 15


# Register your models here.
@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'contact', 'telephone', 'email', 'is_use', 'op_user', 'op_last_update')
    list_display_links = ('code', 'name', )
    fk_fields = ('op_user_id',)
    list_per_page = PER_PAGE


@admin.register(ServiceType)
class ServiceTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'company', 'base_price', 'max_length', 'max_weight', 'max_girth',
                    'op_user', 'op_last_update')
    fk_fields = ('op_user_id',)
    list_filter = ('company',)
    list_per_page = PER_PAGE


@admin.register(Surcharge)
class SurchargeAdmin(admin.ModelAdmin):
    list_display = ('company', 'surcharge_name', 'price', 'percent', 'description', 'op_user', 'op_last_update')
    list_display_links = ('company', 'surcharge_name', )
    list_filter = ('company',)
    fk_fields = ('op_user_id',)
    list_per_page = PER_PAGE


@admin.register(ZoneName)
class ZoneNameAdmin(admin.ModelAdmin):
    list_display = ('company', 'zone_name', 'description', 'op_user', 'op_last_update')
    list_display_links = ('company', 'zone_name', )
    list_filter = ('company',)
    fk_fields = ('op_user_id',)
    list_per_page = PER_PAGE


@admin.register(ZoneSurcharge)
class ZoneSurchargeAdmin(admin.ModelAdmin):
    list_display = ('company', 'service_type', 'zone', 'minimum_price', 'percent', 'plus_price', 'description',
                    'op_user', 'op_last_update')
    list_display_links = ('company', 'service_type', 'zone', )
    list_filter = ('company', 'service_type', )
    fk_fields = ('op_user_id',)
    list_per_page = PER_PAGE


@admin.register(ZoneDetail)
class ZoneDetailAdmin(admin.ModelAdmin):
    list_display = ('company', 'zone', 'begin', 'end', 'op_user', 'op_last_update')
    search_fields = ('begin', 'end', )
    list_filter = ('company', 'zone', )
    list_display_links = ('begin', 'end', )
    fk_fields = ('op_user_id',)
    list_per_page = PER_PAGE


@admin.register(EuroCountry)
class EuroCountryAdmin(admin.ModelAdmin):
    list_display = ('country', 'op_user', 'op_last_update')
    fk_fields = ('op_user_id',)
    search_fields = ('country',)
    ordering = ('country',)
    list_per_page = PER_PAGE


@admin.register(EuroPrice)
class EuroPriceAdmin(admin.ModelAdmin):
    list_display = ('company', 'country', 'basic_price', 'over_weight_price', 'minimum_charge', 'clearance_charge',
                    'description', 'op_user', 'op_last_update')
    list_filter = ('company', 'country', )
    list_display_links = ('company', 'country', )
    fk_fields = ('op_user_id', 'company')

    list_per_page = PER_PAGE

