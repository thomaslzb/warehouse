from django.http import HttpResponseForbidden
from django.shortcuts import render
from users.models import UserProfile
from menu.models import Permission, Menu


# Create your views here.
# def get_menu(self, request):
#     user_result = UserProfile.objects.filter(user_id=request.user.id)
#     if user_result:
#         role_result = Permission.objects.filter(role__id=user_result[0].role_id)
#         if role_result:
#             render(request, 'base-menu.html', {"all_menu": role_result})
#             return True
#     return False
