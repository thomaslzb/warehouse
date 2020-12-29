from django.db import models


# Create your models here.
class AirZone24(models.Model):
    id = models.AutoField(primary_key=True)
    zone_name = models.CharField(max_length=10, null=False, default='', verbose_name='Zone24_name')

    class Meta:
        db_table = "air_zone_24"
        verbose_name = "air_zone_24"

    def __str__(self):
        return '{0}({1})'.format(self.id, self.zone_name)


class Zone24Detail(models.Model):
    id = models.AutoField(primary_key=True)
    zone = models.ForeignKey('AirZone24', to_field='id', on_delete=models.CASCADE, verbose_name="Zone24 Name")
    begin = models.CharField(max_length=10, null=False, default='', verbose_name='Begin')
    end = models.CharField(max_length=10, null=False, default='', verbose_name='End')

    class Meta:
        db_table = "air_zone_24detail"
        verbose_name = "Zone 24 Detail"


class AirZone48(models.Model):
    id = models.AutoField(primary_key=True)
    zone_name = models.CharField(max_length=10, null=False, default='', verbose_name='Zone48_name')

    class Meta:
        db_table = "air_zone_48"
        verbose_name = "air_zone_48"

    def __str__(self):
        return '{0}({1})'.format(self.id, self.zone_name)


class Zone48Detail(models.Model):
    id = models.AutoField(primary_key=True)
    zone = models.ForeignKey('AirZone48', to_field='id', on_delete=models.CASCADE, verbose_name="Zone48 Name")
    begin = models.CharField(max_length=10, null=False, default='', verbose_name='Begin')
    end = models.CharField(max_length=10, null=False, default='', verbose_name='End')

    class Meta:
        db_table = "air_zone_48detail"
        verbose_name = "Zone 48 Detail"


class GeneralCharge(models.Model):
    id = models.AutoField(primary_key=True)
    charge_item = models.CharField(max_length=50, null=False, default='', verbose_name='Item')
    price = models.DecimalField(default=0, blank=True, max_digits=6, decimal_places=2, verbose_name='Base Price')
    minimum_charge = models.DecimalField(default=0, blank=True, max_digits=6, decimal_places=2,
                                         verbose_name='minimum charge')
    unit_description = models.CharField(max_length=40, null=False, default='', verbose_name='Unit')
    remark = models.CharField(max_length=100, null=False, default='', verbose_name='Remark')

    class Meta:
        db_table = "air_general_charge"
        verbose_name = "General Charge"


class Charge24(models.Model):
    id = models.AutoField(primary_key=True)
    zone = models.ForeignKey('AirZone24', to_field='id', on_delete=models.CASCADE, verbose_name="Zone24 Name")
    minimum = models.IntegerField(null=False, default=0, verbose_name='Minimum')
    maximum = models.IntegerField(null=False, default=0, verbose_name='maximum')
    unit_description = models.CharField(max_length=20, null=False, default='KILOS', verbose_name='Unit')
    basic_price = models.DecimalField(default=0, blank=True, max_digits=6, decimal_places=2, verbose_name='Base Price')
    plus_price = models.DecimalField(default=0, blank=True, max_digits=6, decimal_places=2, verbose_name='Base Price')

    class Meta:
        db_table = "air_charge24"
        verbose_name = "24Hour Charge"


class Charge48(models.Model):
    id = models.AutoField(primary_key=True)
    zone = models.ForeignKey('AirZone48', to_field='id', on_delete=models.CASCADE, verbose_name="Zone48 Name")
    minimum = models.IntegerField(null=False, default=0, verbose_name='Minimum')
    maximum = models.IntegerField(null=False, default=0, verbose_name='maximum')
    unit_description = models.CharField(max_length=20, null=False, default='CBB', verbose_name='Unit')
    basic_price = models.DecimalField(default=0, blank=True, max_digits=6, decimal_places=2, verbose_name='Base Price')
    plus_price = models.DecimalField(default=0, blank=True, max_digits=6, decimal_places=2, verbose_name='Base Price')
    postcode_description = models.CharField(max_length=200, null=False, default='',
                                            verbose_name='Postcode description')

    class Meta:
        db_table = "air_charge48"
        verbose_name = "48Hour Charge"

