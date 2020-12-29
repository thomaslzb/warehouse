from django.db import models


# Create your models here.
class LclCompany(models.Model):
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=20, null=False, default="", unique=True, verbose_name="Code",)
    name = models.CharField(max_length=100, default="", null=True, verbose_name="Company Name",)
    fuel_charge = models.DecimalField(default=0, blank=True, max_digits=6, decimal_places=2, verbose_name='Fuel Charge')
    op_last_update = models.DateTimeField(auto_now=True, blank=True, verbose_name="Operate Datetime", )

    class Meta:
        db_table = "lcl_company"
        verbose_name = "Lcl Company"

    def __str__(self):
        return '{0}({1})'.format(self.id, self.name)


# Create your models here.
class LclZone(models.Model):
    id = models.AutoField(primary_key=True)
    zone_name = models.CharField(max_length=10, null=False, default='', verbose_name='Zone_name')
    company = models.ForeignKey('LclCompany', to_field='code', on_delete=models.CASCADE, verbose_name="Company Name")

    class Meta:
        db_table = "lcl_zone"
        verbose_name = "lcl_zone"

    def __str__(self):
        return '{0}({1})'.format(self.zone_name, self.company)


class LclZoneDetail(models.Model):
    id = models.AutoField(primary_key=True)
    zone = models.ForeignKey('LclZone', to_field='id', on_delete=models.CASCADE, verbose_name="Zone Name")
    begin = models.CharField(max_length=10, null=False, default='', verbose_name='Begin')
    end = models.CharField(max_length=10, null=False, default='', verbose_name='End')

    class Meta:
        db_table = "lcl_zone_detail"
        verbose_name = "Lcl Zone Detail"


class ZoneCharge(models.Model):
    id = models.AutoField(primary_key=True)
    zone = models.ForeignKey('LclZone', to_field='id', on_delete=models.CASCADE, verbose_name="Zone Name")
    weight_minimum = models.IntegerField(null=False, default=0, verbose_name='Weight Minimum')
    weight_maximum = models.IntegerField(null=False, default=0, verbose_name='Weight Maximum')
    cbm_minimum = models.DecimalField(blank=True, default=0, max_digits=6, decimal_places=2, verbose_name='CBM Minimum')
    cbm_maximum = models.DecimalField(blank=True, default=0, max_digits=6, decimal_places=2, verbose_name='CBM Maximum')
    basic_price = models.DecimalField(default=0, blank=True, max_digits=14, decimal_places=9, verbose_name='Base Price')
    service_type = models.CharField(max_length=200, null=False, default='', verbose_name='Service Type')
    op_last_update = models.DateTimeField(auto_now=True, blank=True, verbose_name="Operate Datetime", )

    class Meta:
        db_table = "lcl_zone_charge"
        verbose_name = "Lcl Zone Charge"

