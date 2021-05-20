from django.conf import settings
from django.db import models


class LclCompanyModel(models.Model):
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=10, null=False, default="", unique=True, verbose_name="Code", )
    name = models.CharField(max_length=100, default="", null=False, verbose_name="Company Name", )
    telephone = models.CharField(max_length=100, default="", blank=True, null=True, verbose_name="telephone", )
    email = models.CharField(max_length=100, default="", blank=True, null=True, verbose_name="email", )
    contact = models.CharField(max_length=20, default="", blank=True, null=True, verbose_name="contact", )
    remark = models.CharField(max_length=20, default="", blank=True, null=True, verbose_name="remark", )
    is_used = models.BooleanField(default=True, null=False, verbose_name="is_used", )
    op_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='op_lcl_company',
                                on_delete=models.CASCADE, default=1, verbose_name="Operator")
    op_last_update = models.DateTimeField(auto_now=True, blank=True, verbose_name="Operate Datetime", )

    class Meta:
        db_table = "lcl_company"
        verbose_name = "Lcl Company"
        ordering = ['code', ]

    def __str__(self):
        return '{0}({1})'.format(self.id, self.name)


class LclCollectAreaModel(models.Model):
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=5, null=False, default="", unique=True, verbose_name="Code", )
    name = models.CharField(max_length=100, default="", null=False, verbose_name="Name", )
    telephone = models.CharField(max_length=100, default="", null=True, verbose_name="telephone", )
    email = models.CharField(max_length=100, default="", null=True, verbose_name="email", )
    contact = models.CharField(max_length=20, default="", blank=True, null=True, verbose_name="contact", )
    sort_num = models.IntegerField(default=0, verbose_name='sort_by')
    remark = models.CharField(max_length=20, default="", blank=True, null=True, verbose_name="remark", )
    op_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='op_lcl_warehouse',
                                on_delete=models.CASCADE, default=1, verbose_name="Operator")
    op_last_update = models.DateTimeField(auto_now=True, blank=True, verbose_name="Operate Datetime", )

    class Meta:
        db_table = "lcl_collect_area"
        verbose_name = "lcl_collect_area"

    def __str__(self):
        return '{0}({1})'.format(self.id, self.name)


class LclZoneModel(models.Model):
    id = models.AutoField(primary_key=True)
    zone_name = models.CharField(max_length=10, null=False, default='', verbose_name='Zone_name')
    company = models.ForeignKey('LclCompanyModel', to_field='code', on_delete=models.CASCADE,
                                verbose_name="Company Name")
    op_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='op_lcl_zone',
                                on_delete=models.CASCADE, default=1, verbose_name="Operator")
    op_last_update = models.DateTimeField(auto_now=True, blank=True, verbose_name="Operate Datetime", )

    class Meta:
        db_table = "lcl_zone"
        verbose_name = "lcl_zone"

    def __str__(self):
        return '{0}({1})'.format(self.zone_name, self.company)


class LclZoneDetailModel(models.Model):
    id = models.AutoField(primary_key=True)
    zone = models.ForeignKey('LclZoneModel', to_field='id', on_delete=models.CASCADE, verbose_name="Zone Name")
    begin = models.CharField(max_length=10, null=False, default='', verbose_name='Begin')
    end = models.CharField(max_length=10, null=False, default='', verbose_name='End')
    op_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='op_lcl_zone_detail',
                                on_delete=models.CASCADE, default=1, verbose_name="Operator")
    op_last_update = models.DateTimeField(auto_now=True, blank=True, verbose_name="Operate Datetime", )

    class Meta:
        db_table = "lcl_zone_detail"
        verbose_name = "Lcl Zone Detail"


class LclAreaDetailModel(models.Model):
    id = models.AutoField(primary_key=True)
    area_id = models.ForeignKey('AreaDetailModel', to_field='id', on_delete=models.CASCADE, verbose_name="Area Name")
    begin = models.CharField(max_length=10, null=False, default='', verbose_name='Begin')
    end = models.CharField(max_length=10, null=False, default='', verbose_name='End')
    op_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='op_lcl_area_detail',
                                on_delete=models.CASCADE, default=1, verbose_name="Operator")
    op_last_update = models.DateTimeField(auto_now=True, blank=True, verbose_name="Operate Datetime", )

    class Meta:
        db_table = "lcl_area_detail"
        verbose_name = "Lcl Area Detail"


class AreaDetailModel(models.Model):
    id = models.AutoField(primary_key=True)
    zone_id = models.ForeignKey('LclZoneModel', to_field='id', on_delete=models.CASCADE, verbose_name="Zone Name")
    area_name = models.CharField(max_length=50, null=False, default='', verbose_name='Area Name')
    op_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='op_area_detail',
                                on_delete=models.CASCADE, default=1, verbose_name="Operator")
    op_last_update = models.DateTimeField(auto_now=True, blank=True, verbose_name="Operate Datetime", )

    class Meta:
        db_table = "lcl_zone_area"
        verbose_name = "Lcl Zone Area"

    def __str__(self):
        return '{0}'.format(self.area_name)


class ZoneChargeModel(models.Model):
    id = models.AutoField(primary_key=True)
    zone = models.ForeignKey('LclZoneModel', to_field='id', on_delete=models.CASCADE, verbose_name="Zone Name")
    weight_minimum = models.IntegerField(null=False, default=0, verbose_name='Weight Minimum')
    weight_maximum = models.IntegerField(null=False, default=0, verbose_name='Weight Maximum')
    cbm_minimum = models.DecimalField(blank=True, default=0, max_digits=6, decimal_places=2, verbose_name='CBM Minimum')
    cbm_maximum = models.DecimalField(blank=True, default=0, max_digits=6, decimal_places=2, verbose_name='CBM Maximum')
    basic_price = models.DecimalField(default=0, blank=True, max_digits=14, decimal_places=9, verbose_name='Base Price')
    service_type = models.CharField(max_length=20, null=False, default='', verbose_name='Service Type')
    collect_area = models.ForeignKey('LclCollectAreaModel', to_field='code', default='FELIX', on_delete=models.CASCADE,
                                     verbose_name="Collection Area")
    op_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='op_zone_charge',
                                on_delete=models.CASCADE, default=1, verbose_name="Operator")
    op_last_update = models.DateTimeField(auto_now=True, blank=True, verbose_name="Operate Datetime", )

    class Meta:
        db_table = "lcl_zone_charge"
        verbose_name = "Lcl Zone Charge"


# Thomas 我们LCL CALCULATOR所有在这个蓝色范围内的点都需要增加10镑/shipment
# https://www.carcaptain.com/postcodes-within-the-m25-london/
class LclZoneExtraDetailModel(models.Model):
    id = models.AutoField(primary_key=True)
    begin = models.CharField(max_length=10, null=False, default='', verbose_name='Begin')
    end = models.CharField(max_length=10, null=False, default='', verbose_name='End')
    charge_price = models.DecimalField(default=0, blank=True, max_digits=5, decimal_places=2,
                                       verbose_name='charge Price')
    op_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='op_lcl_zone_extra_detail',
                                on_delete=models.CASCADE, default=1, verbose_name="Operator")
    op_last_update = models.DateTimeField(auto_now=True, blank=True, verbose_name="Operate Datetime", )

    class Meta:
        db_table = "lcl_zone_extra"
        verbose_name = "Lcl Zone Extra"


class LclProfitViaAreaDetailModel(models.Model):
    id = models.AutoField(primary_key=True)
    via_area = models.CharField(max_length=50, null=False, default='', verbose_name='via_area')
    service_type = models.CharField(max_length=20, null=False, default='', verbose_name='Service Type')
    fix_price = models.DecimalField(default=0, blank=True, max_digits=5, decimal_places=2,
                                    verbose_name='fix_price')
    percent_price = models.DecimalField(default=0, blank=True, max_digits=5, decimal_places=2,
                                        verbose_name='percent_price')
    op_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='op_lcl_profit',
                                on_delete=models.CASCADE, default=1, verbose_name="Operator")
    op_last_update = models.DateTimeField(auto_now=True, blank=True, verbose_name="Operate Datetime", )

    class Meta:
        db_table = "lcl_profit"
        verbose_name = "lcl_profit"


class LclFuelChargeModel(models.Model):
    id = models.AutoField(primary_key=True)
    company_code = models.ForeignKey(LclCompanyModel, to_field='code', related_name='lcl_company_code',
                                     on_delete=models.CASCADE, verbose_name='company')
    begin_date = models.DateField(blank=True, null=True, verbose_name="begin_date")
    expire_date = models.DateField(blank=True, null=True, verbose_name="expire_date")
    fuel_charge = models.DecimalField(default=0, max_digits=10, decimal_places=2, blank=True,
                                      verbose_name='fuel_charge')
    op_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='op_lcl_fuel_surcharge',
                                on_delete=models.CASCADE, default=1, verbose_name="Operator")
    op_last_update = models.DateTimeField(auto_now=True, blank=True, verbose_name="Operate Datetime", )

    class Meta:
        db_table = "lcl_fuel_surcharge"
        verbose_name = "lcl_fuel_surcharge"
        unique_together = ('company_code', 'begin_date')
        ordering = ('company_code', '-begin_date', )

    def __str__(self):
        return '{0}({1})'.format(self.id, self.company_code)
