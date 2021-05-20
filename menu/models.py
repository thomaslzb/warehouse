from django.db import models
from django.contrib.auth.models import User

NODE_TYPE_CHOICE = ((1, 'WEB PAGE'),
                    (2, 'BUTTON'),
                    (3, 'FILE FOLDER'),
                    )


class Menu(models.Model):
    id = models.AutoField(primary_key=True)
    menu_order = models.CharField(max_length=50, null=False, blank=True, default='', verbose_name='Menu Order')
    menu_name = models.CharField(max_length=50, null=False, blank=True, default='', verbose_name='Menu Name')
    # node_type：节点类型，可以是1-页面或者2-按钮类型3-文件夹
    node_type = models.PositiveSmallIntegerField(default=1, choices=NODE_TYPE_CHOICE, verbose_name='node_type')
    # 页面对应的地址，如果是文件夹或者按钮类型，可以为空
    menu_url = models.CharField(max_length=200, null=True, blank=True, default='', verbose_name='Menu URL')
    # 存icon图标的地址
    menu_icon = models.CharField(max_length=200, null=False, blank=True, default='', verbose_name='Icon URl')
    # 菜单父节点ID，方便递归遍历菜单
    parent_id = models.PositiveSmallIntegerField(default=0, verbose_name='Parent ID')
    # 菜单树的层次，以便于查询指定层级的菜单
    level = models.PositiveSmallIntegerField(default=0, verbose_name='Level')
    # path 树id的路径，主要用于存放从根节点到当前树的父节点的路径，逗号分隔，想要找父节点会特别快。
    path = models.CharField(max_length=200, null=False, blank=True, default='', verbose_name='Path')
    # 是否在用
    is_use = models.BooleanField(default=True, verbose_name="is_use")

    class Meta:
        db_table = "z_menu"
        verbose_name = "Menu"

    def __str__(self):
        return self.menu_name

