from django.db import models
from datetime import datetime

from django.db import models
from django.contrib.auth.models import User
from menu.models import Role

STAFF_ROLE_CHOICE = ((0, 'Custom'),
                     (1, 'Staff-OP'),
                     (2, 'Staff-Warehouse'),
                     (3, 'Staff-Manager'),
                     )

PERCENT_CHOICE = ((0, 'By Fix Amount'),
                  (1, 'By Percent'),
                  )


class SlotEmailGroup(models.Model):
    email = models.EmailField(max_length=200, verbose_name=u"Email")
    desc = models.CharField(max_length=20, verbose_name="Description")

    class Meta:
        verbose_name = 'Email Group'

    def __str__(self):
        return self.desc.__str__()


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    op_position = models.CharField('Op_position', max_length=2, blank=True, default='UK')
    telephone = models.CharField('Telephone', max_length=100, blank=True)
    mod_date = models.DateTimeField('Last modified', auto_now=True)
    profit_percent = models.BooleanField(default=0, choices=PERCENT_CHOICE, verbose_name='Profit Mode')
    role = models.ForeignKey(Role, to_field='id', default='1', on_delete=models.CASCADE, related_name='user_role',
                             verbose_name="System Role")
    email_group = models.ForeignKey(SlotEmailGroup, to_field='id', default='1', on_delete=models.CASCADE,
                                    related_name='to_email_group', verbose_name="Email Group")

    # OPERATOR  WAREHOUSE MANAGER
    staff_role = models.IntegerField('Staff_role', blank=True, default=0, choices=STAFF_ROLE_CHOICE, )

    class Meta:
        verbose_name = 'User Profile'

    def __str__(self):
        return self.user.__str__()


class EmailVerifyRecord(models.Model):
    code = models.CharField(max_length=20, verbose_name="Verify Code")
    email = models.EmailField(max_length=50, verbose_name=u"Email")
    send_type = models.CharField(verbose_name="Verify Type",
                                 choices=(("register", "Register"), ("forget", "Forget Password"),
                                          ("update_email", "Modify Email")),
                                 max_length=30)
    send_time = models.DateTimeField(verbose_name="Send Date", default=datetime.now)

    class Meta:
        verbose_name = "Email Verify"
        verbose_name_plural = verbose_name

    def __str__(self):
        return '{0}({1})'.format(self.code, self.email)
