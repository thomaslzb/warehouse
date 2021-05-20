from django.db import models
from django.conf import settings

from warehouse.settings import MEDIA_ROOT
from .validators import validate_file_extension
from quote.models import Company

IS_USER_CHOICE = ((1, 'OK'),
                  (0, 'Suspend'),
                  )

IS_DB = ((1, 'OK'),
         (0, 'Waiting'),
         )


class Sku(models.Model):
    id = models.AutoField(primary_key=True)
    sku_no = models.CharField(max_length=30, null=False, default='', verbose_name='SKU No', )
    custom = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=1, verbose_name="Custom")
    sku_name = models.CharField(max_length=200, null=False, default='', verbose_name='Produce Name', )
    sku_length = models.DecimalField(default=0, null=False, max_digits=6, decimal_places=2, verbose_name='Length(CM)', )
    sku_width = models.DecimalField(default=0, null=False, max_digits=6, decimal_places=2, verbose_name='Width(CM)', )
    sku_high = models.DecimalField(default=0, null=False, max_digits=6, decimal_places=2, verbose_name='High(CM)', )
    sku_weight = models.DecimalField(default=0, null=False, max_digits=6, decimal_places=2, verbose_name='Weight(KG)', )
    is_ok = models.IntegerField(default=1, null=False, choices=IS_USER_CHOICE, verbose_name="Is OK?", )
    last_update = models.DateTimeField(auto_now=True, blank=True, verbose_name="Operate Datetime", )

    class Meta:
        db_table = "sku"
        verbose_name = "SKU"
        unique_together = ('custom', 'sku_no',)
        ordering = ['sku_no']

    def __str__(self):
        return '{0}({1})'.format(self.sku_no, self.sku_name)


class SkuFileUpload(models.Model):
    id = models.AutoField(primary_key=True)
    custom = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=1, verbose_name="Custom")
    file = models.FileField(upload_to=MEDIA_ROOT, validators=[validate_file_extension])
    file_name = models.CharField(max_length=300, null=False, default='', verbose_name='File Name', )
    is_db = models.IntegerField(default=0, null=False, choices=IS_DB, verbose_name="To DB", )
    upload_date = models.DateTimeField(auto_now=True, blank=True, verbose_name="Upload", )
    db_date = models.DateTimeField(blank=True, null=True, verbose_name="DB Operate", )

    class Meta:
        db_table = "sku_upload"
        verbose_name = "SKU File"


# class SkuQuoteHistory(models.Model):
#     id = models.AutoField(primary_key=True)
#     custom = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=1, verbose_name="Custom")
#     sku = models.ForeignKey('Sku', to_field='id', on_delete=models.CASCADE, default=1, verbose_name="SKU")
#     qty = models.IntegerField(default=0, null=False, verbose_name="Qty.", )
#     destination = models.CharField(max_length=50, null=False, default='', verbose_name='Destination', )
#     favorite_company = models.ForeignKey(Company, to_field='id', default='1', on_delete=models.CASCADE,
#                                          related_name='suk_favorite_company', verbose_name="Favorite Company")
#     basic_price = models.DecimalField(default=0, null=False, max_digits=8,
#                                       decimal_places=2, verbose_name='Basic Price', )
#     oversize = models.DecimalField(default=0, null=False, max_digits=8,
#                                    decimal_places=2, verbose_name='oversize', )
#     overweight = models.DecimalField(default=0, null=False, max_digits=8,
#                                      decimal_places=2, verbose_name='overweight', )
#     additional = models.DecimalField(default=0, null=False, max_digits=8, decimal_places=2,
#                                      verbose_name='Additional', )
#     fuel_percent = models.DecimalField(default=0, null=False, max_digits=8, decimal_places=2,
#                                        verbose_name='Fuel Charge', )
#     last_update = models.DateTimeField(auto_now=True, blank=True, verbose_name="Operate Datetime", )
#
#     class Meta:
#         db_table = "sku_quote_history"
#         verbose_name = "Quote History"
