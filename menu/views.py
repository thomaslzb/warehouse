from users.models import UserProfile


# Create your views here.

def get_user_grant_list(user_id, system_name="QUOTE-SYSTEM"):
    menu_grant = ['0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0']
    queryset = UserProfile.objects.filter(user_id=user_id, system_menu__icontains=system_name)
    if queryset:
        grant_string = queryset[0].menu_grant
        menu_grant = [char for char in grant_string]

    return menu_grant

