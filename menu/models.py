from django.db import models


class FirstMenu(models.Model):
    id = models.AutoField(primary_key=True)
    menu_order = models.CharField(max_length=50, null=False, blank=True, default='', verbose_name='Menu Order')
    menu_name = models.CharField(max_length=50, null=False, blank=True, default='', verbose_name='Menu Name')
    menu_url = models.CharField(max_length=200, null=False, blank=True, default='', verbose_name='Menu URL')
    menu_remark = models.CharField(max_length=200, null=False, blank=True, default='', verbose_name='Remark')

    class Meta:
        db_table = "z_first_menu"
        verbose_name = "First Menu"

    def __str__(self):
        return self.menu_name


class Menu(models.Model):
    id = models.AutoField(primary_key=True)
    first_menu = models.ForeignKey('FirstMenu', to_field='id', on_delete=models.CASCADE, related_name='first_menu',
                                   verbose_name="First Menu")
    menu_order = models.CharField(max_length=50, null=False, blank=True, default='', verbose_name='Menu Order')
    menu_name = models.CharField(max_length=50, null=False, blank=True, default='', verbose_name='Menu Name')
    menu_url = models.CharField(max_length=200, null=False, blank=True, default='', verbose_name='Menu URL')
    menu_remark = models.CharField(max_length=200, null=False, blank=True, default='', verbose_name='Remark')

    class Meta:
        db_table = "z_menu"
        verbose_name = "Menu"

    def __str__(self):
        return self.menu_name


class Role(models.Model):
    id = models.AutoField(primary_key=True)
    role_name = models.CharField(max_length=20, null=False, blank=True, default='', verbose_name='Role Name')
    role_remark = models.CharField(max_length=200, null=False, blank=True, default='', verbose_name='Remark')

    class Meta:
        db_table = "z_role"
        verbose_name = "Role"

    def __str__(self):
        return self.role_name


class Permission(models.Model):
    id = models.AutoField(primary_key=True)
    first_menu = models.ForeignKey('FirstMenu', to_field='id', on_delete=models.CASCADE, related_name='p_first_menu',
                                   verbose_name="First Menu")
    is_display = models.BooleanField(default=True, verbose_name="is_display_first_menu")
    menu = models.ForeignKey('Menu', to_field='id', on_delete=models.CASCADE, related_name='permission_menu',
                             verbose_name="Menu")
    role = models.ForeignKey('Role', to_field='id', on_delete=models.CASCADE, related_name='permission_role',
                             verbose_name="Role")
    is_list = models.BooleanField(default=True, verbose_name="is_List")
    is_update = models.BooleanField(default=True, verbose_name="is_Update")
    is_delete = models.BooleanField(default=True, verbose_name="is_Delete")

    class Meta:
        db_table = "z_permission"
        verbose_name = "Permission"
