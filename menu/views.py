from django.http import HttpResponseForbidden
from django.shortcuts import render
from users.models import UserProfile
from menu.models import Permission


# Create your views here.
def get_menu(self, request):
    user_result = UserProfile.objects.filter(user_id=request.user.id)
    if user_result:
        role = Permission.objects.filter(role__id=user_result[0].role)
        render(request, 'base-menu.html', {"all_menu": role})
        return True
    return False
