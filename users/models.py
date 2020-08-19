from django.db import models
from datetime import datetime

from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    op_position = models.CharField('Op_position', max_length=2, blank=True)
    telephone = models.CharField('Telephone', max_length=100, blank=True)
    mod_date = models.DateTimeField('Last modified', auto_now=True)
    staff_role = models.CharField('Staff_role', max_length=10, blank=True)

    class Meta:
        verbose_name = 'User Profile'

    def __str__(self):
        return self.user.__str__()


class EmailVerifyRecord(models.Model):
    code = models.CharField(max_length=20, verbose_name="Verify Code")
    email = models.EmailField(max_length=50, verbose_name=u"Email")
    send_type = models.CharField(verbose_name="Verify Type",
                                 choices=(("register", "Register"), ("forget", "Forget Password"), ("update_email", "Modify Email")),
                                 max_length=30)
    send_time = models.DateTimeField(verbose_name="Send Date", default=datetime.now)

    class Meta:
        verbose_name = "Email Verify"
        verbose_name_plural = verbose_name

    def __str__(self):
        return '{0}({1})'.format(self.code, self.email)

