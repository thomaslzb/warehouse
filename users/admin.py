from django.contrib import admin
from .models import UserProfile


# Register your models here.
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'op_position', 'telephone', 'mod_date')


admin.site.site_header = "DCG Warehouse Admin"
admin.site.site_title = "DCG Data Adminstration"
