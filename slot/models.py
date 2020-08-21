from django.db import models
from users.models import UserProfile


# Create your models here.
class Haulier(models.Model):
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=4, null=False, default="", unique=True)
    name = models.CharField(max_length=50)
    contact = models.CharField(max_length=100)
    telephone = models.CharField('Telephone', max_length=100, blank=True)
    email = models.CharField('Email', max_length=250, blank=True)
    is_use = models.IntegerField(default=1, )
    op_id = models.IntegerField(default=0)
    op_datetime = models.DateTimeField(auto_now=True, blank=True)

    class Meta:
        db_table = "Haulier"

    def __str__(self):
        return '{0}({1})'.format(self.code, self.name)


class WarehouseProfile(models.Model):
    id = models.AutoField(primary_key=True)
    position = models.CharField(max_length=2, null=False, default="UK")
    beginworktime = models.TimeField(blank=True)
    overworktime = models.TimeField(blank=True)
    maxslot = models.PositiveIntegerField(null=False, default="2")
    maxinbound = models.PositiveIntegerField(null=False, default="0")
    op_id = models.IntegerField(default=0)
    op_datetime = models.DateTimeField(auto_now=True, blank=True)

    class Meta:
        db_table = "WarehouseProfile"

    def __str__(self):
        return self.position


class FixWeekday(models.Model):
    Haulier = models.ForeignKey('Haulier', to_field='id', on_delete=models.CASCADE, )
    weekday = models.IntegerField(default=1, )
    time = models.TimeField(blank=True, null=False, )
    status = models.PositiveIntegerField(default=1)
    op_id = models.IntegerField(default=0)
    op_datetime = models.DateTimeField(auto_now=True, blank=True)

    class Meta:
        db_table = "Haulier_FixTime"
        unique_together = ("Haulier", "weekday", "time")


class Warehouse(models.Model):
    id = models.AutoField(primary_key=True)
    deliveryref = models.CharField(max_length=25, null=False, default="")
    workdate = models.DateField(null=False)
    slottime = models.TimeField(null=False)
    vehiclereg = models.CharField(max_length=15, null=True, blank=True, default="")
    hailerid = models.IntegerField(default=1, null=False)
    status = models.CharField(max_length=8, null=False, default="INBOUND")
    progress = models.PositiveIntegerField(null=False, default=1)
    havetime = models.PositiveIntegerField(default=1, null=False)
    position = models.CharField(max_length=2, default="UK", null=False)
    op_id = models.IntegerField(default=0)
    op_datetime = models.DateTimeField(auto_now=True, blank=True)
    remark = models.CharField(max_length=80, null=True, blank=True, default="")

    class Meta:
        db_table = "Warehouse"
        unique_together = ("deliveryref", )


class ProgressRecord(models.Model):
    id = models.AutoField(primary_key=True)
    deliveryref = models.CharField(max_length=25, null=False, default="", )
    progress = models.PositiveIntegerField(null=False, default=1)
    progress_name = models.CharField(max_length=10, blank=True, default="")
    position = models.CharField(max_length=2, default="UK", null=False)
    remark = models.CharField(max_length=400, null=True, blank=True, default="")
    op_id = models.IntegerField(default=0)
    op_datetime = models.DateTimeField(auto_now=True, blank=True)

    class Meta:
        db_table = "Progress_record"
