from django.db import models
from django.conf import settings
from users.models import UserProfile

PROGRESS_CHOICE = ((1, 'Booked'),
                   (2, 'Arrived'),
                   (3, 'Loading'),
                   (4, 'Finished'),
                   (5, 'Abnormal'),
                   )

IS_USER_CHOICE = ((1, 'Normal'),
                  (0, 'Stop'),
                  )

STATUS_CHOICE = ((1, 'Normal'),
                 (0, 'Stop'),
                 )

HAVETIME_CHOICE = ((1, 'YES, HAVE SLOT TIME'),
                   (0, 'NO SLOT TIME'),
                   )

WEEKS_CHOICE = ((1, 'MON'),
                (2, 'TUE'),
                (3, 'WED'),
                (4, 'TUR'),
                (5, 'FIR'),
                (6, 'SAT'),
                (7, 'SUN'),
                )


class WarehouseProfile(models.Model):
    id = models.AutoField(primary_key=True)
    position = models.CharField(max_length=10, null=False, default="UK", verbose_name="Position", unique=True)
    desc = models.CharField(max_length=10, null=False, default="CHELMSFORD", verbose_name="Position", unique=True)
    beginworktime = models.TimeField(blank=True, default="", verbose_name="Open Time", )
    overworktime = models.TimeField(blank=True, default="", verbose_name="Close time", )
    maxslot = models.PositiveIntegerField(null=False, default="2", verbose_name="Max Slot Num", )
    maxinbound = models.PositiveIntegerField(null=False, default="0", verbose_name="Max Inbound Num", )
    time_gap = models.IntegerField(default=30, null=False, verbose_name="Time Gap", )
    op_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='op_warehouse_profile',
                                on_delete=models.CASCADE, default=1, verbose_name="Operator")
    op_datetime = models.DateTimeField(auto_now=True, blank=True, verbose_name="Operate Datetime")

    class Meta:
        db_table = "WarehouseProfile"

    def __str__(self):
        return self.position


class Haulier(models.Model):
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=6, null=False, default="", unique=False, verbose_name="Code")
    name = models.CharField(max_length=50, default="", null=True, verbose_name="Company Name")
    contact = models.CharField(max_length=100, default="",  blank=True, null=True, verbose_name="Contact", )
    telephone = models.CharField(max_length=100, blank=True, default="", null=True, verbose_name="Telephone")
    email = models.CharField(max_length=250, default="", null=True, blank=True, verbose_name="Email")
    position = models.ForeignKey(WarehouseProfile, to_field="position", default="UK",
                                 on_delete=models.CASCADE, related_name='haulier_warehouse_position',
                                 verbose_name="Haulier Position")
    is_use = models.IntegerField(default=1, null=False, choices=IS_USER_CHOICE, verbose_name="Is Normal", )
    op_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='op_haulier', on_delete=models.CASCADE,
                                default=1, verbose_name="Operator")
    op_datetime = models.DateTimeField(auto_now=True, blank=True, verbose_name="Operate Datetime", )

    class Meta:
        db_table = "Haulier"
        verbose_name = "Haulier List"
        unique_together = ("code", "position",)

    def __str__(self):
        return '{0}({1})'.format(self.code, self.name)


class FixWeekday(models.Model):
    Haulier = models.ForeignKey('Haulier', to_field='id', on_delete=models.CASCADE, verbose_name="Haulier Code (Name)")
    weekday = models.IntegerField(default=1, choices=WEEKS_CHOICE, verbose_name="Weeks")
    time = models.TimeField(blank=True, null=False, default="", verbose_name="Schedule Time")
    status = models.PositiveIntegerField(default=1, choices=STATUS_CHOICE, verbose_name="Status")
    op_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='op_fixweekday', on_delete=models.CASCADE,
                                verbose_name="Operator")
    op_datetime = models.DateTimeField(auto_now=True, blank=True, verbose_name="Operate Datetime")

    class Meta:
        db_table = "Haulier_FixTime"
        unique_together = ("Haulier", "weekday", "time")
        verbose_name = "Haulier Scheduled Time"


class Warehouse(models.Model):
    id = models.AutoField(primary_key=True)
    deliveryref = models.CharField(max_length=25, null=False, default="", verbose_name="Delivery Ref.", )
    workdate = models.DateField(null=False, default="", verbose_name="Date")
    slottime = models.TimeField(null=False, default="", verbose_name="Time")
    vehiclereg = models.CharField(max_length=15, null=True, blank=True, default="", verbose_name="Vehicle Reg.")
    hailerid = models.ForeignKey(Haulier, to_field='id', related_name='haulier_warehouse',
                                 on_delete=models.CASCADE, default=1, verbose_name="Haulier")
    status = models.CharField(max_length=8, null=False, default="INBOUND", verbose_name="In/Outbound")
    progress = models.PositiveIntegerField(null=False, default=1, choices=PROGRESS_CHOICE, verbose_name="Progress")
    havetime = models.PositiveIntegerField(default=1, null=False, choices=HAVETIME_CHOICE, verbose_name="Is Scheduled")
    position = models.ForeignKey(WarehouseProfile, to_field="position", default="UK",
                                 on_delete=models.CASCADE, related_name='position_warehouse', verbose_name="Position")
    op_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='op_warehouse',
                                on_delete=models.CASCADE, default=1, verbose_name="Operator")
    op_datetime = models.DateTimeField(auto_now=False, blank=True, verbose_name="Operator")
    remark = models.CharField(max_length=80, null=True, blank=True, default="", verbose_name="Remark")
    last_update = models.DateTimeField(auto_now=True, blank=True, verbose_name="Last Update")

    class Meta:
        db_table = "Warehouse"
        unique_together = ("deliveryref",)
        verbose_name = "Slot List"


class SlotFiles(models.Model):
    delivery_ref = models.ForeignKey('Warehouse', to_field='id', on_delete=models.CASCADE, verbose_name="Delivery Ref.")
    file_name = models.CharField(max_length=80, null=True, blank=True, default="", verbose_name="File name")
    files_profile = models.CharField(max_length=80, null=True, blank=True, default="", verbose_name="File profile")
    local_file_name = models.CharField(max_length=80, null=True, blank=True, default="", verbose_name="Local file name")
    uploaded_at = models.DateTimeField(auto_now=True, blank=True, verbose_name="Upload DateTime")
    is_void = models.BooleanField(default=0, verbose_name="Is Void")
    order = models.IntegerField(default=0, verbose_name="Order")
    op_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='op_file_user',
                                on_delete=models.CASCADE, default=1, verbose_name="Operator")

    class Meta:
        db_table = "slot_files"
        verbose_name = "Slot Files"


class ProgressRecord(models.Model):
    id = models.AutoField(primary_key=True)
    deliveryref = models.CharField(max_length=25, null=False, default="", verbose_name="Delivery Ref.")
    progress = models.PositiveIntegerField(null=False, default=1, choices=PROGRESS_CHOICE, verbose_name="Progress")
    progress_name = models.CharField(max_length=10, blank=True, default="", verbose_name="Progress Name")
    position = models.CharField(max_length=10, default="UK", null=False, verbose_name="Position")
    remark = models.CharField(max_length=400, null=True, blank=True, default="", verbose_name="Action")
    op_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='op_progressrecord', on_delete=models.CASCADE,
                                default=1, verbose_name="Operator")
    op_datetime = models.DateTimeField(auto_now=True, blank=True, verbose_name="Operate Datetime")

    class Meta:
        db_table = "Progress_record"

