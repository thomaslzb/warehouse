from django.db import models
from django.conf import settings

IS_USER_CHOICE = ((1, 'OK'),
                  (0, 'Suspend'),
                  )


class Sku(models.Model):
    id = models.AutoField(primary_key=True)
    sku_no = models.CharField(max_length=30, null=False, default='', verbose_name='SKU No', )
    custom = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=1, verbose_name="Custom")
    sku_name = models.CharField(max_length=200, null=False, default='', verbose_name='Produce Name',)
    sku_length = models.DecimalField(default=0, blank=True, max_digits=6, decimal_places=2, verbose_name='Length(CM)',)
    sku_width = models.DecimalField(default=0, blank=True, max_digits=6, decimal_places=2, verbose_name='Width(CM)',)
    sku_high = models.DecimalField(default=0, blank=True, max_digits=6, decimal_places=2, verbose_name='High(CM)',)
    sku_weight = models.DecimalField(default=0, blank=True, max_digits=6, decimal_places=2, verbose_name='Weight(KG)',)
    is_ok = models.IntegerField(default=1, null=False, choices=IS_USER_CHOICE, verbose_name="Is OK?", )
    last_update = models.DateTimeField(auto_now=True, blank=True, verbose_name="Operate Datetime", )

    class Meta:
        db_table = "sku"
        verbose_name = "SKU"
        unique_together = ('custom', 'sku_no', )

    def __str__(self):
        return '{0}({1})'.format(self.sku_no, self.sku_name)
