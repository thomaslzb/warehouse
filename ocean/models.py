from django.conf import settings
from django.db import models


# 亚马孙仓库
class AmazonWarehouseModel(models.Model):
    id = models.AutoField(primary_key=True)
    fba_code = models.CharField(max_length=20, null=False, default="", unique=True, verbose_name="fba_code", )
    address = models.CharField(max_length=100, default="", blank=True, null=True, verbose_name="address", )
    city = models.CharField(max_length=20, default="", null=True, verbose_name="city", )
    state = models.CharField(max_length=20, default="", blank=True, null=True, verbose_name="state", )
    postcode = models.CharField(max_length=10, default="", null=False, verbose_name="postcode", )
    is_used = models.BooleanField(default=True, null=False, verbose_name="is_used", )
    op_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='op_ocean_amazon',
                                on_delete=models.CASCADE, default=1, verbose_name="Operator")
    op_last_update = models.DateTimeField(auto_now=True, blank=True, verbose_name="Operate Datetime", )

    class Meta:
        db_table = "ocean_amazon_warehouse"
        verbose_name = "ocean_amazon_warehouse"
        ordering = ['fba_code', ]

    def __str__(self):
        return '{0}'.format(self.fba_code)


# 亚马孙仓库整车及散货价格
class AmazonPriceModel(models.Model):
    id = models.AutoField(primary_key=True)
    amazon = models.ForeignKey('AmazonWarehouseModel', to_field='id', related_name='amazon_warehouse_id',
                               verbose_name="amazon_id", on_delete=models.CASCADE)
    whole_price = models.DecimalField(blank=True, default=0, max_digits=8, decimal_places=2,
                                      verbose_name='whole_price')
    pallet_price = models.DecimalField(blank=True, default=0, max_digits=8, decimal_places=2,
                                       verbose_name='pallet_price')
    op_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='op_amazon_price',
                                on_delete=models.CASCADE, default=1, verbose_name="Operator")
    op_last_update = models.DateTimeField(auto_now=True, blank=True, verbose_name="Operate Datetime", )

    class Meta:
        db_table = "ocean_amazon_price"
        verbose_name = "ocean_whole_price"
        ordering = ['amazon', ]


# 散货FBA费用项目列表
class FbaItemPriceModel(models.Model):
    id = models.AutoField(primary_key=True)
    fee_code = models.CharField(max_length=5, null=False, default="", unique=True, verbose_name="fee_code", )
    en_name = models.CharField(max_length=50, null=False, default="", verbose_name="en_name", )
    cn_name = models.CharField(max_length=50, null=False, default="", verbose_name="cn_name", )
    unit = models.CharField(max_length=20, null=False, default="", verbose_name="unit", )
    rate = models.DecimalField(blank=True, default=0, max_digits=8, decimal_places=2,
                               verbose_name='rate')
    minimum_charge = models.DecimalField(blank=True, default=0, max_digits=8, decimal_places=2,
                                         verbose_name='minimum_charge')
    fee_type = models.IntegerField(default="0", verbose_name="fee_type", )  # 费用类型 0 - 固定费用， 1 - 附加费用
    remark = models.CharField(max_length=100, default="", blank=True, null=True, verbose_name="remark", )
    op_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='op_fba_pallet_price',
                                on_delete=models.CASCADE, default=1, verbose_name="Operator")
    op_last_update = models.DateTimeField(auto_now=True, blank=True, verbose_name="Operate Datetime", )

    class Meta:
        db_table = "ocean_fba_item_price"
        verbose_name = "ocean_fba_pallet_price"
        ordering = ['en_name', 'fee_code', ]


# 私人仓费用项目列表
class PrivateItemPriceModel(models.Model):
    id = models.AutoField(primary_key=True)
    fee_code = models.CharField(max_length=5, null=False, default="", unique=True, verbose_name="fee_code", )
    en_name = models.CharField(max_length=50, null=False, default="", verbose_name="en_name", )
    cn_name = models.CharField(max_length=50, null=False, default="", verbose_name="cn_name", )
    unit = models.CharField(max_length=20, null=False, default="", verbose_name="unit", )
    rate = models.DecimalField(blank=True, default=0, max_digits=8, decimal_places=2,
                               verbose_name='rate')
    minimum_charge = models.DecimalField(blank=True, default=0, max_digits=8, decimal_places=2,
                                         verbose_name='minimum_charge')
    fee_type = models.IntegerField(default="0", verbose_name="fee_type", )  # 费用类型 0 - 固定费用， 1 - 附加费用
    remark = models.CharField(max_length=100, default="", blank=True, null=True, verbose_name="remark", )
    op_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='op_private_item_price',
                                on_delete=models.CASCADE, default=1, verbose_name="Operator")
    op_last_update = models.DateTimeField(auto_now=True, blank=True, verbose_name="Operate Datetime", )

    class Meta:
        db_table = "ocean_private_item_price"
        verbose_name = "ocean_private_item_price"
        ordering = ['en_name', ]


# 私人仓 postcode 分类 收费列表
class PostcodePriceModel(models.Model):
    id = models.AutoField(primary_key=True)
    type_name = models.CharField(max_length=50, null=False, default="", unique=True, verbose_name="en_name", )
    price = models.DecimalField(blank=True, default=0, max_digits=8, decimal_places=2,
                                verbose_name='price')
    op_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='op_postcode_type',
                                on_delete=models.CASCADE, default=1, verbose_name="Operator")
    op_last_update = models.DateTimeField(auto_now=True, blank=True, verbose_name="Operate Datetime", )

    class Meta:
        db_table = "ocean_postcode_price"
        verbose_name = "ocean_postcode_price"
        ordering = ['type_name', ]


# 私人仓 postcode 分类
class PostcodeModel(models.Model):
    id = models.AutoField(primary_key=True)
    postcode_type = models.ForeignKey('PostcodePriceModel', to_field='id', verbose_name="postcode_type",
                                      on_delete=models.CASCADE)
    begin_code = models.CharField(max_length=10, null=False, default="", unique=True, verbose_name="begin_code", )
    end_code = models.CharField(max_length=10, null=False, default="", verbose_name="end_code", )
    op_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='op_postcode_detail',
                                on_delete=models.CASCADE, default=1, verbose_name="Operator")
    op_last_update = models.DateTimeField(auto_now=True, blank=True, verbose_name="Operate Datetime", )

    class Meta:
        db_table = "ocean_postcode_detail"
        verbose_name = "ocean_postcode_detail"
        ordering = ['postcode_type', 'begin_code', ]


# 私人仓 london postcode 收取拥堵费的邮编
class LondonPostcodeModel(models.Model):
    id = models.AutoField(primary_key=True)
    begin_code = models.CharField(max_length=10, null=False, default="", unique=True, verbose_name="begin_code", )
    end_code = models.CharField(max_length=10, null=False, default="", verbose_name="end_code", )
    op_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='op_postcode_london',
                                on_delete=models.CASCADE, default=1, verbose_name="Operator")
    op_last_update = models.DateTimeField(auto_now=True, blank=True, verbose_name="Operate Datetime", )

    class Meta:
        db_table = "ocean_postcode_london"
        verbose_name = "ocean_postcode_london"
        ordering = ['begin_code', ]


# 提货港口
class OceanPortModel(models.Model):
    id = models.AutoField(primary_key=True)
    country = models.CharField(max_length=2, null=False, default="GB", verbose_name="country", )
    port_code = models.CharField(max_length=3, null=False, default="", unique=True, verbose_name="port_code", )
    port_name = models.CharField(max_length=100, null=False, default="", verbose_name="port_name", )
    op_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='op_ocean_port', on_delete=models.CASCADE,
                                default=1, verbose_name="Operator")
    op_datetime = models.DateTimeField(auto_now=True, blank=True, verbose_name="Operate Datetime", )

    class Meta:
        db_table = "ocean_port"
        verbose_name = "ocean_port"
        unique_together = ("port_code",)
        ordering = ['country', 'port_code', ]

    def __str__(self):
        return '{0}'.format(self.port_name)


# 海运整柜收费列表
class CabinetItemPriceModel(models.Model):
    id = models.AutoField(primary_key=True)
    fee_code = models.CharField(max_length=5, null=False, default="", unique=True, verbose_name="fee_code", )
    en_name = models.CharField(max_length=50, null=False, default="", verbose_name="en_name", )
    cn_name = models.CharField(max_length=50, null=False, default="", verbose_name="cn_name", )
    unit = models.CharField(max_length=20, null=False, default="", verbose_name="unit", )
    rate = models.DecimalField(blank=True, default=0, max_digits=8, decimal_places=2,
                               verbose_name='rate')
    minimum_charge = models.DecimalField(blank=True, default=0, max_digits=8, decimal_places=2,
                                         verbose_name='minimum_charge')
    fee_type = models.IntegerField(default="0", verbose_name="fee_type", )  # 费用类型 0 - 固定费用， 1 - 附加费用
    remark = models.CharField(max_length=100, default="", blank=True, null=True, verbose_name="remark", )
    op_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='op_cabinet_item_price',
                                on_delete=models.CASCADE, default=1, verbose_name="Operator")
    op_last_update = models.DateTimeField(auto_now=True, blank=True, verbose_name="Operate Datetime", )

    class Meta:
        db_table = "ocean_cabinet_item_price"
        verbose_name = "ocean_cabinet_item_price"
        ordering = ['en_name', ]


class ContainModel(models.Model):
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=4, null=False, default="", unique=True, verbose_name="code", )
    name = models.CharField(max_length=100, null=False, default="GB", verbose_name="contain name", )
    max_volume = models.IntegerField(default="0", verbose_name="max_volume", )
    op_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='op_ocean_container', on_delete=models.CASCADE,
                                default=1, verbose_name="Operator")
    op_datetime = models.DateTimeField(auto_now=True, blank=True, verbose_name="Operate Datetime", )

    class Meta:
        db_table = "ocean_container"
        verbose_name = "ocean_container"
        unique_together = ("code",)
        ordering = ['code', ]

    def __str__(self):
        return '{0}'.format(self.name)


class ExchangeModel(models.Model):
    id = models.AutoField(primary_key=True)
    exchange_rate = models.DecimalField(blank=True, default=0, max_digits=8, decimal_places=4,
                                        verbose_name='exchange_rate')
    op_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='op_exchange_rate', on_delete=models.CASCADE,
                                default=1, verbose_name="Operator")
    op_datetime = models.DateTimeField(auto_now=True, blank=True, verbose_name="Operate Datetime", )

    class Meta:
        db_table = "ocean_exchange_rate"
        verbose_name = "ocean_exchange_rate"


