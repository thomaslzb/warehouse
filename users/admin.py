from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import UserProfile, SlotEmailGroup

admin.site.unregister(User)


# Register your models here.
class UserProfileInline(admin.StackedInline):
    model = UserProfile


class UserProfileAdmin(UserAdmin):
    inlines = [UserProfileInline, ]


@admin.register(SlotEmailGroup)
class SlotEmailGroupAdmin(admin.ModelAdmin):
    list_display = ('id',  'desc', 'email',)


admin.site.register(User, UserProfileAdmin)

admin.site.site_header = "DCG Warehouse Admin"
admin.site.site_title = "DCG Data Admin"
