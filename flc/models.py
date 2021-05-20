import datetime

from django.conf import settings
from django.db import models
from django.utils import timezone


class FlcCompanyModel(models.Model):
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=10, null=False, default="", unique=True, verbose_name="Code", )
    name = models.CharField(max_length=100, default="", null=False, verbose_name="Company Name", )
    telephone = models.CharField(max_length=100, default="", blank=True, null=True, verbose_name="telephone", )
    email = models.CharField(max_length=100, default="", blank=True, null=True, verbose_name="email", )
    contact = models.CharField(max_length=20, default="", blank=True, null=True, verbose_name="contact", )
    remark = models.CharField(max_length=20, default="", blank=True, null=True, verbose_name="remark", )
    is_used = models.BooleanField(default=True, null=False, verbose_name="is_used", )
    op_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='op_flc_company',
                                on_delete=models.CASCADE, default=1, verbose_name="Operator")
    op_last_update = models.DateTimeField(auto_now=True, blank=True, verbose_name="Operate Datetime", )

    class Meta:
        db_table = "flc_company"
        verbose_name = "flc_company"
        ordering = ('code',)

    def __str__(self):
        return '{0}({1})'.format(self.id, self.name)


class FlcFuelChargeModel(models.Model):
    id = models.AutoField(primary_key=True)
    company_code = models.ForeignKey(FlcCompanyModel, to_field='code', related_name='flc_company_code', null=True,
                                     on_delete=models.CASCADE, verbose_name='company')
    begin_date = models.DateField(blank=True, null=True, verbose_name="begin_date")
    expire_date = models.DateField(blank=True, null=True, verbose_name="expire_date")
    fuel_charge = models.DecimalField(default=0, max_digits=10, decimal_places=2, blank=True,
                                      verbose_name='fuel_charge')
    op_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='op_flc_fuel_surcharge',
                                on_delete=models.CASCADE, default=1, verbose_name="Operator")
    op_last_update = models.DateTimeField(auto_now=True, blank=True, verbose_name="Operate Datetime", )

    class Meta:
        db_table = "flc_fuel_surcharge"
        verbose_name = "flc_fuel_surcharge"
        ordering = ('company_code', '-begin_date')
        unique_together = ('company_code', 'begin_date')

    def __str__(self):
        return '{0}({1})'.format(self.id, self.company_code)


class FLCPortModel(models.Model):
    id = models.AutoField(primary_key=True)
    country = models.CharField(max_length=2, null=False, default="GB", verbose_name="country", )
    port_code = models.CharField(max_length=3, null=False, default="", unique=True, verbose_name="port_code", )
    port_name = models.CharField(max_length=100, null=False, default="", verbose_name="port_name", )
    op_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='op_flc_port', on_delete=models.CASCADE,
                                default=1, verbose_name="Operator")
    op_datetime = models.DateTimeField(auto_now=True, blank=True, verbose_name="Operate Datetime", )

    class Meta:
        db_table = "flc_port"
        verbose_name = "flc_port"
        unique_together = ("port_code",)
        ordering = ['country', 'port_code', ]

    def __str__(self):
        return '{0}'.format(self.port_name)


class FLCContainModel(models.Model):
    id = models.AutoField(primary_key=True)
    code_1984 = models.CharField(max_length=4, null=False, default="", unique=True, verbose_name="code_1984", )
    code_1995 = models.CharField(max_length=4, null=False, default="", verbose_name="code_1995", )
    name = models.CharField(max_length=40, null=False, default="GB", verbose_name="contain name", )
    op_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='op_flc_contain', on_delete=models.CASCADE,
                                default=1, verbose_name="Operator")
    op_datetime = models.DateTimeField(auto_now=True, blank=True, verbose_name="Operate Datetime", )

    class Meta:
        db_table = "flc_contain"
        verbose_name = "flc_contain"
        unique_together = ("code_1984",)
        ordering = ['code_1984', ]

    def __str__(self):
        return '{0}'.format(self.name)


class FLCPostcodeModel(models.Model):
    id = models.AutoField(primary_key=True)
    postcode = models.CharField(max_length=8, null=False, unique=True, verbose_name="postcode", db_index=True)
    county = models.CharField(max_length=50, null=True, verbose_name="county", db_index=True)
    district = models.CharField(max_length=50, null=True, verbose_name="district", db_index=True)
    country = models.CharField(max_length=20, null=True, verbose_name="country", )
    postcode_area = models.CharField(max_length=8, null=False, verbose_name="postcode_area", )
    postcode_district = models.CharField(max_length=8, null=False, verbose_name="postcode_district", )
    latitude = models.DecimalField(max_digits=14, decimal_places=6, blank=True, verbose_name='latitude')
    longitude = models.DecimalField(max_digits=14, decimal_places=6, blank=True, verbose_name='longitude')
    easting = models.DecimalField(max_digits=14, decimal_places=0, blank=True, verbose_name='easting')
    north = models.DecimalField(max_digits=14, decimal_places=0, blank=True, verbose_name='north')
    op_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='op_uk_postcode', on_delete=models.CASCADE,
                                default=1, verbose_name="Operator")
    op_datetime = models.DateTimeField(auto_now=True, blank=True, verbose_name="Operate Datetime", )

    class Meta:
        db_table = "flc_uk_postcode"
        verbose_name = "flc_uk_postcode"
        unique_together = ("postcode",)
        ordering = ['postcode', 'county', ]

    def __str__(self):
        return '{0}'.format(self.postcode)


date_type = (('Pickup Date', 'Pickup Date'), ('ETA Date', 'ETA Date'), )
address_type = (('POSTCODE', 'POSTCODE'),  ('CITY', 'CITY'), )


class FLCPriceModel(models.Model):
    id = models.AutoField(primary_key=True)
    company_code = models.ForeignKey(FlcCompanyModel, to_field='code', null=True, related_name='flc_price_company',
                                     on_delete=models.CASCADE, verbose_name='company')
    port_code = models.ForeignKey(FLCPortModel, to_field='port_code', default='', null=True,
                                  related_name='flc_price_port', on_delete=models.CASCADE, verbose_name='port')
    destination = models.CharField(max_length=100, null=False, blank=True, default='',  verbose_name="address", )
    destination_type = models.CharField(max_length=10, null=False,  blank=True, default='',  verbose_name="address_type", )
    begin_date = models.DateField(blank=True, null=False, default=timezone.localdate, verbose_name="begin_date")
    expire_date = models.DateField(blank=True, null=False, default=timezone.localdate, verbose_name="expire_date")
    date_type = models.CharField(max_length=20, choices=date_type, verbose_name="date_type", )
    container = models.ForeignKey(FLCContainModel, to_field='id', related_name='flc_price_container', null=True,
                                  on_delete=models.CASCADE, verbose_name='price_container')
    price = models.DecimalField(default=0, max_digits=10, decimal_places=2, blank=True, verbose_name='price')
    op_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='op_flc_price', on_delete=models.CASCADE,
                                default=1, verbose_name="Operator")
    op_datetime = models.DateTimeField(auto_now=True, blank=True, verbose_name="Operate Datetime", )

    class Meta:
        db_table = "flc_price_list"
        verbose_name = "flc_price_list"
        unique_together = ['company_code', 'port_code', 'destination_type', 'destination', 'container', 'begin_date', ]
        ordering = ['company_code', 'port_code', 'destination', 'container', '-begin_date', ]



