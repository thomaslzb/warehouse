from django.db import models
from django.conf import settings

IS_USER_CHOICE = ((1, 'Normal'),
                  (0, 'Stop'),
                  )

BELONG_AREA_CHOICE = (('UK', 'UK'),
                      ('EURO', 'EUROPEAN'),
                      )


# Create your models here.
class Company(models.Model):
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=4, null=False, default="", unique=True, verbose_name="Code",)
    name = models.CharField(max_length=100, default="", null=True, verbose_name="Company Name",)
    contact = models.CharField(max_length=100, blank=True, default="", null=True, verbose_name="Contact", )
    telephone = models.CharField(max_length=100, blank=True, default="", null=True, verbose_name="Telephone",)
    email = models.CharField(max_length=250, default="", null=True, blank=True, verbose_name="Email")
    icon_lg = models.CharField(max_length=250, default="", null=True, blank=True, verbose_name="Icon URL(Big)")
    icon_sm = models.CharField(max_length=250, default="", null=True, blank=True, verbose_name="Icon URL(Small)")
    is_use = models.IntegerField(default=1, null=False, choices=IS_USER_CHOICE, verbose_name="Is Normal", )
    op_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                default=1, verbose_name="Operator")
    op_last_update = models.DateTimeField(auto_now=True, blank=True, verbose_name="Operate Datetime", )

    class Meta:
        db_table = "q_company"
        verbose_name = "Company"

    def __str__(self):
        return '{0}({1})'.format(self.code, self.name)


class ServiceType(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20, null=False, default='', verbose_name='ServiceName',)
    company = models.ForeignKey('Company', to_field='id', on_delete=models.CASCADE, verbose_name="Belong Company")
    description = models.CharField(max_length=200, blank=True, null=False, default='', verbose_name='description')
    base_price = models.DecimalField(default=0, blank=True, max_digits=6, decimal_places=2, verbose_name='Base Price')
    max_weight = models.DecimalField(default=0, blank=True, max_digits=4, decimal_places=0,
                                     verbose_name='Max Weight(kg)')
    max_length = models.DecimalField(default=0, blank=True, max_digits=4, decimal_places=0,
                                     verbose_name='Max Length(cm)')
    max_girth = models.DecimalField(default=0, blank=True, max_digits=4, decimal_places=0,
                                    verbose_name='Max Girth(cm)')
    op_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                default=1, verbose_name="Operator")
    op_last_update = models.DateTimeField(auto_now=True, blank=True, verbose_name="Operate Datetime", )

    class Meta:
        db_table = "q_service_type"
        verbose_name = "Service Type"
        unique_together = ('name', 'company',)

    def __str__(self):
        return '{0}({1})'.format(self.name, self.company)


class ZoneName(models.Model):
    id = models.AutoField(primary_key=True)
    company = models.ForeignKey('Company', to_field='id', on_delete=models.CASCADE, verbose_name="Belong Company")
    zone_name = models.CharField(max_length=10, null=False, default='', verbose_name='Zone')
    belong = models.ForeignKey('UKRange', to_field='id', null=True, on_delete=models.CASCADE, verbose_name="Belong UK Range")
    description = models.CharField(max_length=100, blank=True, null=False, default='', verbose_name='description')
    op_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                default=1, verbose_name="Operator")
    op_last_update = models.DateTimeField(auto_now=True, blank=True, verbose_name="Operate Datetime", )

    class Meta:
        db_table = "q_zone"
        verbose_name = "Zone"
        unique_together = ('company', 'zone_name')

    def __str__(self):
        return '{0}({1})'.format(self.zone_name, self.company)


class ZoneDetail(models.Model):
    id = models.AutoField(primary_key=True)
    company = models.ForeignKey('Company', to_field='id', on_delete=models.CASCADE, verbose_name="Belong Company")
    zone = models.ForeignKey('ZoneName', to_field='id', on_delete=models.CASCADE, verbose_name="Zone Name")
    begin = models.CharField(max_length=10, null=False, default='', verbose_name='Begin')
    end = models.CharField(max_length=10, null=False, default='', verbose_name='End')
    op_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                default=1, verbose_name="Operator")
    op_last_update = models.DateTimeField(auto_now=True, blank=True, verbose_name="Operate Datetime", )

    class Meta:
        db_table = "q_zone_detail"
        verbose_name = "Zone Detail"
        unique_together = ('company', 'zone', 'begin')


class Surcharge(models.Model):
    id = models.AutoField(primary_key=True)
    company = models.ForeignKey('Company', to_field='id', on_delete=models.CASCADE, verbose_name="Belong Company")
    surcharge_name = models.CharField(max_length=20, null=False, default='', verbose_name='Surcharge Name')
    description = models.CharField(max_length=300, blank=True, null=False, default='', verbose_name='description')
    price = models.DecimalField(default=0, max_digits=8, blank=True, decimal_places=2, verbose_name='Price')
    percent = models.DecimalField(default=0, max_digits=8, blank=True, decimal_places=2, verbose_name='Percent(%)')
    op_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                default=1, verbose_name="Operator")
    op_last_update = models.DateTimeField(auto_now=True, blank=True, verbose_name="Operate Datetime", )

    class Meta:
        db_table = "q_surcharge"
        verbose_name = "Surcharge"
        unique_together = ('company', 'surcharge_name', )


class ZoneSurcharge(models.Model):
    id = models.AutoField(primary_key=True)
    company = models.ForeignKey('Company', to_field='id', on_delete=models.CASCADE, verbose_name="Belong Company")
    service_type = models.ForeignKey('ServiceType', to_field='id', on_delete=models.CASCADE,
                                     verbose_name="Service Type")
    zone = models.ForeignKey('ZoneName', to_field='id', on_delete=models.CASCADE, verbose_name="Zone Name")
    minimum_price = models.DecimalField(default=0, max_digits=8, decimal_places=2, blank=True,
                                        verbose_name='Minimum Price')
    percent = models.DecimalField(default=0, max_digits=8, decimal_places=2, blank=True, verbose_name='Percent(%)')
    plus_price = models.DecimalField(default=0, max_digits=8, decimal_places=2, blank=True,
                                     verbose_name='plus_price')
    description = models.CharField(max_length=300, null=False, blank=True, default='', verbose_name='description')
    op_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                default=1, verbose_name="Operator")
    op_last_update = models.DateTimeField(auto_now=True, blank=True, verbose_name="Operate Datetime", )

    class Meta:
        db_table = "q_zone_surcharge"
        verbose_name = "Zone Surcharge"
        unique_together = ('company', 'service_type', 'zone')


class EuroCountry(models.Model):
    id = models.AutoField(primary_key=True)
    country = models.CharField(max_length=50, null=False, default='', verbose_name='Country', )
    belong = models.CharField(max_length=4, null=False, default='EURO', verbose_name='Belong',
                              choices=BELONG_AREA_CHOICE,)
    op_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=1, verbose_name="Operator")
    op_last_update = models.DateTimeField(auto_now=True, blank=True, verbose_name="Operate Datetime", )

    class Meta:
        db_table = "q_euro_country"
        verbose_name = "Country"
        unique_together = ('country', 'belong',)

    def __str__(self):
        return '{0}({1})'.format(self.country, self.belong)


class EuroPrice(models.Model):
    id = models.AutoField(primary_key=True)
    country = models.ForeignKey('EuroCountry', to_field='id', on_delete=models.CASCADE, verbose_name="Country")
    company = models.ForeignKey('Company', to_field='id', on_delete=models.CASCADE, verbose_name="Belong Company")
    basic_price = models.DecimalField(default=0, max_digits=8, blank=True, decimal_places=2, verbose_name='Basic_Price')
    over_weight_price = models.DecimalField(default=0, max_digits=8, blank=True, decimal_places=2,
                                            verbose_name='OverWeight Price')
    clearance_charge = models.DecimalField(default=0, max_digits=8, blank=True, decimal_places=2,
                                           verbose_name='Clearance Charge')
    minimum_charge = models.DecimalField(default=0, max_digits=8, blank=True, decimal_places=2,
                                         verbose_name='minimum_charge(PerItem)')
    description = models.CharField(max_length=300, null=False, blank=True, default='', verbose_name='description')
    op_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=1, verbose_name="Operator")
    op_last_update = models.DateTimeField(auto_now=True, blank=True, verbose_name="Operate Datetime", )

    class Meta:
        db_table = "q_euro_price"
        verbose_name = "Euro Price"
        unique_together = ('company', 'country',)


class UKRange(models.Model):
    id = models.AutoField(primary_key=True)
    area = models.CharField(max_length=50, null=False, default='', verbose_name='Area', unique=True)
    example_postcode = models.CharField(max_length=10, null=False, default='', verbose_name='Example Postcode')
    op_last_update = models.DateTimeField(auto_now=True, blank=True, verbose_name="Operate Datetime", )

    class Meta:
        db_table = "q_uk_range"
        verbose_name = "UK Area"
        unique_together = ('area', )

    def __str__(self):
        return self.area


class UKPostcodeRange(models.Model):
    id = models.AutoField(primary_key=True)
    area = models.ForeignKey('UKRange', to_field='id', on_delete=models.CASCADE, verbose_name="UK Area")
    postcode_begin = models.CharField(max_length=10, null=False, default='', verbose_name='Begin')
    postcode_end = models.CharField(max_length=10, null=False, default='', verbose_name='End')
    op_last_update = models.DateTimeField(auto_now=True, blank=True, verbose_name="Operate Datetime", )

    class Meta:
        db_table = "q_uk_postcode"
        verbose_name = "UK Postcode Range"
        unique_together = ('area', 'postcode_begin')


class UserSetupProfit(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=1, verbose_name="Customer")
    is_uk = models.CharField(max_length=4, null=False, default='UK', verbose_name='Belong', choices=BELONG_AREA_CHOICE,)
    uk_area = models.ForeignKey('UKRange', to_field='id', null=True, blank=True, default='',
                                on_delete=models.CASCADE, verbose_name="UK Area",)
    euro_area = models.ForeignKey('EuroCountry', to_field='id', null=True, blank=True, default='',
                                  on_delete=models.CASCADE, verbose_name="Euro Country")
    fix_amount = models.DecimalField(default=0, max_digits=8, blank=True, decimal_places=2, verbose_name='Fix Amount')
    percent = models.DecimalField(default=0, max_digits=8, blank=True, decimal_places=2, verbose_name='Percent')
    op_last_update = models.DateTimeField(auto_now=True, blank=True, verbose_name="Operate Datetime", )

    class Meta:
        db_table = "q_user_setup_profit"
        verbose_name = "Profit Setup"
        unique_together = ('user', 'is_uk', 'uk_area', 'euro_area',)
        ordering = ('user', 'is_uk', 'uk_area', 'euro_area',)


