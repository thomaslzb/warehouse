from django.db import models


# Create your models here.
class Haulier(models.Model):
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=4, null=False, default="", unique=True)
    name = models.CharField(max_length=50)
    contact = models.CharField(max_length=100)
    telephone = models.CharField('Telephone', max_length=100, blank=True)
    email = models.CharField('Email', max_length=250, blank=True)
    is_use = models.IntegerField(default=1,)
    op_user = models.CharField(max_length=20, null=False, default="")
    op_datetime = models.DateTimeField(auto_now=True, blank=True)

    class Meta:
        db_table = "haulier"

    def __str__(self):
        return '{0}({1})'.format(self.code, self.name)


class WarehouseProfile(models.Model):
    id = models.AutoField(primary_key=True)
    position = models.CharField(max_length=2, null=False, default="UK")
    beginworktime = models.TimeField(blank=True)
    overworktime = models.TimeField(blank=True)
    maxslot = models.PositiveIntegerField(null=False, default="2")
    maxinbound = models.PositiveIntegerField(null=False, default="0")
    op_user = models.CharField(max_length=20, null=False, default="Admin")
    op_datetime = models.DateTimeField(auto_now=True, blank=True)

    class Meta:
        db_table = "warehouse_profile"

    def __str__(self):
        return self.position


class FixWeekday(models.Model):
    hailer = models.ForeignKey('Haulier', to_field='id', on_delete=models.CASCADE, related_name='list_haulier')
    weekday = models.IntegerField(default=1, )
    time = models.TimeField(blank=True, null=False, )
    status = models.PositiveIntegerField(default=1)
    op_user = models.CharField(max_length=20, null=False, default="")
    op_datetime = models.DateTimeField(auto_now=True, blank=True)

    class Meta:
        db_table = "fix_weekday"
        unique_together = ("hailer", "weekday", "time")


class Warehouse(models.Model):
    deliveryref = models.CharField(max_length=25, null=False, default="", primary_key=True)
    workdate = models.DateField(null=False)
    slottime = models.TimeField(null=False)
    vehiclereg = models.CharField(max_length=15, null=True, blank=True, default="")
    hailerid = models.IntegerField(default=1, null=False)
    status = models.CharField(max_length=8, null=False, default="INBOUND")
    progress = models.PositiveIntegerField(null=False, default=1)
    havetime = models.PositiveIntegerField(default=1, null=False)
    position = models.IntegerField(default=1, null=False)
    op_user = models.CharField(max_length=20, null=False, default="")
    op_datetime = models.DateTimeField(auto_now=True, blank=True)

    class Meta:
        db_table = "warehouse"


