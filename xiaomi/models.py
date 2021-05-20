from datetime import datetime
from django.utils import timezone
from django.conf import settings
from django.db import models

ITEM_TYPE_CHOICE = (('Delivery', 'Delivery Fee'),
                    ('Handle', 'Handle Fee'),
                    )


# postcode
class PostcodeModel(models.Model):
    id = models.AutoField(primary_key=True)
    postcode_begin = models.CharField(max_length=6, null=False, default="", verbose_name="Postcode_begin", )
    postcode_end = models.CharField(max_length=6, null=False, default="", verbose_name="Postcode_end", )
    express_company = models.CharField(max_length=10, null=False, default="",
                                       verbose_name="express company Code", )
    op_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='op_mi_postcode', on_delete=models.CASCADE,
                                default=1, verbose_name="Operator")
    op_datetime = models.DateTimeField(auto_now=True, blank=True, verbose_name="Operate Datetime", )

    class Meta:
        db_table = "x_mi_postcode"
        verbose_name = "mi_postcode"
        unique_together = ("postcode_begin", "express_company",)


# 小米的主账单
class MiAccountBillMainModel(models.Model):
    id = models.AutoField(primary_key=True)
    bill_year = models.IntegerField(default=2021, null=False, verbose_name="Bill Year")
    bill_month = models.IntegerField(default=1, null=False, verbose_name="Bill Month")
    record_num = models.IntegerField(default=0, null=False, verbose_name="record num.")
    is_used = models.BooleanField(default=False)
    op_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='op_mi_account_main', on_delete=models.CASCADE,
                                default=1, verbose_name="Operator")
    op_datetime = models.DateTimeField(auto_now=True, blank=True, verbose_name="Operate Datetime", )

    class Meta:
        db_table = "x_mi_bill_main"
        verbose_name = "x_mi_bill_main"
        unique_together = ("bill_year", "bill_month",)
        ordering = ['bill_year', 'bill_month', ]


# 小米的账单明细
class MiAccountBillDetailModel(models.Model):
    id = models.AutoField(primary_key=True)
    bill_year = models.IntegerField(default=2021, null=False, verbose_name="Bill Year")
    bill_month = models.IntegerField(default=1, null=False, verbose_name="Bill Month")
    mi_code = models.CharField(max_length=50, null=False, default="", unique=True, verbose_name="Mi Code", )
    express_company = models.CharField(max_length=10, null=False, default="",
                                       verbose_name="express company Code", )
    package_code = models.CharField(max_length=21, default="", null=True, verbose_name="package_code")
    parcel_id = models.CharField(max_length=50, default="", blank=True, null=True, verbose_name="parcel id", )
    country = models.CharField(max_length=20, blank=True, default="", null=True, verbose_name="country")
    county = models.CharField(max_length=50, blank=True, default="", null=True, verbose_name="county")
    town = models.CharField(max_length=50, blank=True, default="", null=True, verbose_name="town")
    postcode = models.CharField(max_length=10, blank=True, default="", null=True, verbose_name="postcode")
    ready_datetime = models.DateTimeField(blank=True, null=True, verbose_name="ready_datetime")
    goods_id = models.CharField(max_length=100, blank=True, default="", null=True, verbose_name="goods_id")
    total_qty = models.IntegerField(default=1, null=False, verbose_name="Total Qty.")
    weight = models.DecimalField(default=0, blank=True, max_digits=12, decimal_places=5, verbose_name='weight')
    delivery_fee_checked = models.BooleanField(default=False)
    update_bill_year = models.IntegerField(default=0, null=False, verbose_name="update_bill_year")
    update_bill_month = models.IntegerField(default=0, null=False, verbose_name="update_bill_year")
    op_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='op_mi_account', on_delete=models.CASCADE,
                                default=1, verbose_name="Operator")
    op_datetime = models.DateTimeField(auto_now=True, blank=True, verbose_name="Operate Datetime", )

    class Meta:
        db_table = "x_mi_bill_detail"
        verbose_name = "x_mi_bill_detail"
        unique_together = ("mi_code",)
        ordering = ['bill_year', 'bill_month', 'mi_code', 'parcel_id']


# UPS 的主账单
class UpsMainBillModel(models.Model):
    id = models.AutoField(primary_key=True)
    bill_date = models.DateField(default=timezone.now, blank=True, verbose_name="Bill Date")
    ups_bill_no = models.CharField(max_length=10, default="", blank=True, null=False, unique=True,
                                   verbose_name="ups bill no", )
    record_num = models.IntegerField(default=0, null=False, verbose_name="record num.")
    total_amount = models.DecimalField(default=0, blank=True, max_digits=12, decimal_places=2,
                                       verbose_name='total_amount')
    op_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='ups_manage_bill_op', on_delete=models.CASCADE,
                                default=1, verbose_name="Operator")
    op_datetime = models.DateTimeField(auto_now=True, blank=True, verbose_name="Operate Datetime", )

    class Meta:
        db_table = "x_ups_bill_main"
        verbose_name = "ups_bill_main"
        unique_together = ("ups_bill_no",)
        ordering = ['bill_date', 'ups_bill_no', ]

    def __str__(self):
        return '{0}'.format(self.ups_bill_no)


# UPS 的 账单明细
class UpsBillDetailModel(models.Model):
    id = models.AutoField(primary_key=True)
    ups_bill_no = models.CharField(max_length=10, default="", blank=True, null=False, verbose_name="ups bill no", )
    # Column 14
    parcel_id = models.CharField(max_length=50, default="", blank=True, null=False, verbose_name="parcel id", )
    # Column 16
    mi_code = models.CharField(max_length=50, null=False, default="", verbose_name="Mi Code", )
    # Column 5
    bill_date = models.DateField(blank=True, verbose_name="finished Datetime")
    # Column 12
    delivery_date = models.DateField(blank=True, verbose_name="delivery Datetime")
    # Column 44
    fee_code = models.CharField(max_length=3, null=False, default="", verbose_name="Fee Code", )
    # Column 46
    fee_desc = models.CharField(max_length=60, null=False, default="", verbose_name="Fee desc", )
    # Column 51
    fee_currency = models.CharField(max_length=3, null=False, default="", verbose_name="Fee Currency", )
    # Column 53
    fee_amount = models.DecimalField(default=0, blank=True, max_digits=12, decimal_places=2, verbose_name='Fee Amount')
    is_use = models.BooleanField(default=False)
    used_bill_year = models.IntegerField(default=0, null=False, verbose_name="used_bill_year")
    used_bill_month = models.IntegerField(default=0, null=False, verbose_name="used_bill_month")
    op_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='op_ups_account', on_delete=models.CASCADE,
                                default=1, verbose_name="Operator")
    op_datetime = models.DateTimeField(auto_now=True, blank=True, verbose_name="Operate Datetime", )

    class Meta:
        db_table = "x_ups_bill_detail"
        verbose_name = "ups_bill_detail"
        ordering = ['bill_date', 'ups_bill_no', 'parcel_id', 'mi_code', ]


# DCG-UK 主账单
class DcgBillModel(models.Model):
    id = models.AutoField(primary_key=True)
    bill_year = models.IntegerField(default=2021, null=False, verbose_name="Bill Year")
    bill_month = models.IntegerField(default=1, null=False, verbose_name="Bill Month")
    express_company = models.CharField(max_length=10, null=False, default="", verbose_name="express company Code", )
    company_bill_list = models.CharField(max_length=400, null=False, default="", verbose_name="Bill List", )
    last_month_record = models.IntegerField(default=1, null=False, verbose_name="last_month_record")
    this_month_record = models.IntegerField(default=1, null=False, verbose_name="this_month_record")
    total_record = models.IntegerField(default=1, null=False, verbose_name="Total Record")
    total_amount = models.DecimalField(default=0, blank=True, max_digits=12, decimal_places=2,
                                       verbose_name='Total Amount')
    nett_cost = models.DecimalField(default=0, blank=True, max_digits=12, decimal_places=2, verbose_name='nett_cost')
    total_vat = models.DecimalField(default=0, blank=True, max_digits=12, decimal_places=2, verbose_name='total_vat')
    total_cost = models.DecimalField(default=0, blank=True, max_digits=12, decimal_places=2, verbose_name='total_cost')
    total_profit = models.DecimalField(default=0, blank=True, max_digits=12, decimal_places=2,
                                       verbose_name='total_profit')
    op_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='op_total_bill', on_delete=models.CASCADE,
                                default=1, verbose_name="Operator")
    op_datetime = models.DateTimeField(auto_now=True, blank=True, verbose_name="Operate Datetime", )

    class Meta:
        db_table = "x_dcg_bill_main"
        verbose_name = "dcg_bill_main"
        unique_together = ('bill_year', 'bill_month', 'express_company',)
        ordering = ['bill_year', 'bill_month', ]


# DCG-UK 主账单sub Total 明细汇总
class DcgBillDetailTotalModel(models.Model):
    id = models.AutoField(primary_key=True)
    bill_year = models.IntegerField(default=2021, null=False, verbose_name="Bill Year")
    bill_month = models.IntegerField(default=1, null=False, verbose_name="Bill Month")
    display_order = models.IntegerField(default=0, null=False, verbose_name="display order")
    express_company = models.CharField(max_length=10, null=False, default="",
                                       verbose_name="express company Code", )
    item_type = models.CharField(max_length=10, default="Delivery", choices=ITEM_TYPE_CHOICE,
                                 verbose_name="Item Type", )
    item = models.CharField(max_length=150, null=False, default="", verbose_name="Item", )
    record_num = models.IntegerField(default=1, null=False, verbose_name="Record Num")
    qty = models.IntegerField(default=0, blank=True, verbose_name='qty')
    unit_price = models.DecimalField(default=0, blank=True, max_digits=10, decimal_places=2,
                                     verbose_name='unit_price')
    sub_total_amount = models.DecimalField(default=0, blank=True, max_digits=10, decimal_places=2,
                                           verbose_name='sub_total_amount')
    op_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='op_dcg_bill_detail_total',
                                on_delete=models.CASCADE, default=1, verbose_name="Operator")
    op_datetime = models.DateTimeField(auto_now=True, blank=True, verbose_name="Operate Datetime", )

    class Meta:
        db_table = "x_dcg_bill_detail_total"
        verbose_name = "dcg_bill_detail_total"
        ordering = ['bill_year', 'bill_month', ]


# DCG-UK 账单明细 Handle 列表
class DcgBillDetailHandleModel(models.Model):
    id = models.AutoField(primary_key=True)
    bill_year = models.IntegerField(default=2021, null=False, verbose_name="Bill Year")
    bill_month = models.IntegerField(default=1, null=False, verbose_name="Bill Month")
    mi_code = models.CharField(max_length=50, null=False, default="", unique=True, verbose_name="Mi Code", )
    package_code = models.CharField(max_length=21, default="", null=True, verbose_name="package_code")
    express_company = models.CharField(max_length=10, null=False, default="",
                                       verbose_name="express company Code", )
    parcel_id = models.CharField(max_length=50, default="", blank=True, null=True, verbose_name="ups parcel id", )
    postcode = models.CharField(max_length=10, blank=True, default="", null=True, verbose_name="postcode")
    ready_datetime = models.DateTimeField(blank=True, null=True, verbose_name="ready_datetime")
    goods_id = models.CharField(max_length=100, blank=True, default="", null=True, verbose_name="goods_id")
    total_qty = models.IntegerField(default=1, null=False, verbose_name="Total Qty.")
    weight = models.DecimalField(default=0, blank=True, max_digits=12, decimal_places=5, verbose_name='weight')

    handle_fee = models.DecimalField(default=0, blank=True, max_digits=12, decimal_places=2,
                                     verbose_name='handle_fee')
    extra_handle_fee = models.DecimalField(default=0, blank=True, max_digits=12, decimal_places=2,
                                           verbose_name='extra_handle_fee')
    special_item_fee = models.DecimalField(default=0, blank=True, max_digits=12, decimal_places=2,
                                           verbose_name='special_item_fee')
    package_fee = models.DecimalField(default=0, blank=True, max_digits=12, decimal_places=2,
                                      verbose_name='package_fee')
    total_amount = models.DecimalField(default=0, blank=True, max_digits=12, decimal_places=2,
                                       verbose_name='total_amount')
    total_cost = models.DecimalField(default=0, blank=True, max_digits=12, decimal_places=2,
                                     verbose_name='total_cost')
    total_profit = models.DecimalField(default=0, blank=True, max_digits=12, decimal_places=2,
                                       verbose_name='total_profit')

    op_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='op_bill_detail_handle',
                                on_delete=models.CASCADE, default=1, verbose_name="Operator")
    op_datetime = models.DateTimeField(auto_now=True, blank=True, verbose_name="Operate Datetime", )

    class Meta:
        db_table = "x_detail_handle"
        verbose_name = "dcg_bill_detail_handle"
        ordering = ['bill_year', 'bill_month', ]


# DCG-UK 账单明细 UPS 快递费列表
class DcgBillDetailUPSModel(models.Model):
    id = models.AutoField(primary_key=True)
    bill_year = models.IntegerField(default=2021, null=False, verbose_name="Bill Year")
    bill_month = models.IntegerField(default=1, null=False, verbose_name="Bill Month")
    mi_code = models.CharField(max_length=50, null=False, default="", verbose_name="Mi Code", )
    package_code = models.CharField(max_length=21, default="", null=True, verbose_name="package_code")
    express_company = models.CharField(max_length=10, null=False, default="",
                                       verbose_name="express company Code", )
    parcel_id = models.CharField(max_length=50, default="", blank=True, null=True, verbose_name="ups parcel id", )
    postcode = models.CharField(max_length=10, blank=True, default="", null=True, verbose_name="postcode")
    ready_datetime = models.DateTimeField(blank=True, null=True, verbose_name="ready_datetime")
    goods_id = models.CharField(max_length=100, blank=True, default="", null=True, verbose_name="goods_id")
    total_qty = models.IntegerField(default=1, null=False, verbose_name="Total Qty.")
    weight = models.DecimalField(default=0, blank=True, max_digits=12, decimal_places=5, verbose_name='weight')

    standard_delivery_fee = models.DecimalField(default=0, blank=True, max_digits=12, decimal_places=2,
                                                verbose_name='standard_delivery_fee')
    residential = models.DecimalField(default=0, blank=True, max_digits=12, decimal_places=2,
                                      verbose_name='residential')
    dom_standard_undeliverable_return = models.DecimalField(default=0, blank=True, max_digits=12, decimal_places=2,
                                                            verbose_name='dom_standard_undeliverable_return')
    extended_area_surcharge_destination = models.DecimalField(default=0, blank=True, max_digits=12, decimal_places=2,
                                                              verbose_name='extended_area_surcharge_destination')
    uk_border_fee = models.DecimalField(default=0, blank=True, max_digits=12, decimal_places=2,
                                        verbose_name='um_border_fee')
    additional_handling = models.DecimalField(default=0, blank=True, max_digits=12, decimal_places=2,
                                              verbose_name='additional_handling')
    peak_surcharge_additional_handling = models.DecimalField(default=0, blank=True, max_digits=12, decimal_places=2,
                                                             verbose_name='peak_surcharge_additional_handling')
    address_correction_dom_standard = models.DecimalField(default=0, blank=True, max_digits=12, decimal_places=2,
                                                          verbose_name='address_correction_dom_standard')
    fuel_surcharge_rate = models.DecimalField(default=0, blank=True, max_digits=12, decimal_places=2,
                                              verbose_name='fuel_surcharge_rate')
    fuel_surcharge = models.DecimalField(default=0, blank=True, max_digits=12, decimal_places=2,
                                         verbose_name='fuel_surcharge')
    total_amount = models.DecimalField(default=0, blank=True, max_digits=12, decimal_places=2,
                                       verbose_name='total_amount')
    nett_cost = models.DecimalField(default=0, blank=True, max_digits=12, decimal_places=2, verbose_name='nett_cost')
    total_vat = models.DecimalField(default=0, blank=True, max_digits=12, decimal_places=2, verbose_name='total_vat')
    total_cost = models.DecimalField(default=0, blank=True, max_digits=12, decimal_places=2,
                                     verbose_name='total_cost')
    total_profit = models.DecimalField(default=0, blank=True, max_digits=12, decimal_places=2,
                                       verbose_name='total_profit')

    update_year = models.IntegerField(default=2021, null=False, verbose_name="Update Year")
    update_month = models.IntegerField(default=1, null=False, verbose_name="Update Month")
    ups_bill_no_list = models.CharField(max_length=100, default="", blank=True, null=True,
                                        verbose_name="ups_bill_no_list,")
    op_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='op_bill_detail_ups',
                                on_delete=models.CASCADE, default=1, verbose_name="Operator")
    op_datetime = models.DateTimeField(auto_now=True, blank=True, verbose_name="Operate Datetime", )

    class Meta:
        db_table = "x_detail_ups"
        verbose_name = "dcg_bill_detail_ups"
        unique_together = ("mi_code", "update_year", "update_month")
        ordering = ['bill_year', 'bill_month', ]


# DCG-UK 账单明细 DPD 快递费列表
class DcgBillDetailDPDModel(models.Model):
    id = models.AutoField(primary_key=True)
    bill_year = models.IntegerField(default=2021, null=False, verbose_name="Bill Year")
    bill_month = models.IntegerField(default=1, null=False, verbose_name="Bill Month")
    mi_code = models.CharField(max_length=50, null=False, default="", verbose_name="Mi Code", )
    package_code = models.CharField(max_length=21, default="", null=True, verbose_name="package_code")
    express_company = models.CharField(max_length=10, null=False, default="",
                                       verbose_name="express company Code", )
    parcel_id = models.CharField(max_length=50, default="", blank=True, verbose_name="parcel id", )
    postcode = models.CharField(max_length=10, blank=True, default="", null=True, verbose_name="postcode")
    ready_datetime = models.DateTimeField(blank=True, null=True, verbose_name="ready_datetime")
    goods_id = models.CharField(max_length=100, blank=True, default="", null=True, verbose_name="goods_id")
    total_qty = models.IntegerField(default=1, null=False, verbose_name="Total Qty.")
    weight = models.DecimalField(default=0, blank=True, max_digits=12, decimal_places=5, verbose_name='weight')

    standard_delivery_fee = models.DecimalField(default=0, blank=True, max_digits=12, decimal_places=5,
                                                verbose_name='standard_delivery_fee')
    additional_fee = models.DecimalField(default=0, blank=True, max_digits=12, decimal_places=5,
                                         verbose_name='additional_fee')
    fuel_surcharge_rate = models.DecimalField(default=0, blank=True, max_digits=12, decimal_places=2,
                                              verbose_name='fuel_surcharge_rate')
    fuel_surcharge = models.DecimalField(default=0, blank=True, max_digits=12, decimal_places=2,
                                         verbose_name='fuel_surcharge')
    total_amount = models.DecimalField(default=0, blank=True, max_digits=12, decimal_places=2,
                                       verbose_name='total_amount')
    nett_cost = models.DecimalField(default=0, blank=True, max_digits=12, decimal_places=2, verbose_name='nett_cost')
    total_vat = models.DecimalField(default=0, blank=True, max_digits=12, decimal_places=2, verbose_name='total_vat')
    total_cost = models.DecimalField(default=0, blank=True, max_digits=12, decimal_places=2,
                                     verbose_name='total_cost')
    total_profit = models.DecimalField(default=0, blank=True, max_digits=12, decimal_places=2,
                                       verbose_name='total_profit')

    update_year = models.IntegerField(default=2021, null=False, verbose_name="Update Year")
    update_month = models.IntegerField(default=1, null=False, verbose_name="Update Month")
    dpd_bill_no_list = models.CharField(max_length=100, default="", blank=True, null=True,
                                        verbose_name="ups_bill_no_list,")
    op_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='op_bill_detail_dpd',
                                on_delete=models.CASCADE, default=1, verbose_name="Operator")
    op_datetime = models.DateTimeField(auto_now=True, blank=True, verbose_name="Operate Datetime", )

    class Meta:
        db_table = "x_detail_dpd"
        verbose_name = "dcg_bill_detail_dpd"
        unique_together = ("mi_code", "update_year", "update_month")
        ordering = ['bill_year', 'bill_month', ]


#  需要计算的项目表
class CalculateItemModel(models.Model):
    id = models.AutoField(primary_key=True)
    # 暂时分为两个类别， 快递费Delivery， 处理费 Handle
    item_type = models.CharField(max_length=10, default="Delivery", choices=ITEM_TYPE_CHOICE,
                                 verbose_name="Item Type", )
    item = models.CharField(max_length=50, null=False, default="", verbose_name="Item", )
    item_desc = models.CharField(max_length=100, null=True, default="", verbose_name="Item_desc", )
    express_company = models.CharField(max_length=10, null=False, default="",
                                       verbose_name="express company Code", )
    zone = models.CharField(max_length=10, null=True, default="ZONE1", verbose_name="Zone Area", )
    max_qty = models.IntegerField(default=0, verbose_name='max qty')
    min_weight = models.DecimalField(default=0, max_digits=10, decimal_places=2, verbose_name='min weight')
    max_weight = models.DecimalField(default=0, max_digits=10, decimal_places=2, verbose_name='min weight')
    unit_price = models.DecimalField(default=0, max_digits=10, decimal_places=2, verbose_name='Unit Price')
    remark = models.CharField(max_length=100, default="", null=True, verbose_name="Item_remark", )
    order_by = models.IntegerField(default=0, null=False, verbose_name="order by")
    is_used = models.BooleanField(default=True, verbose_name='is Used')
    op_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='op_calc_item', on_delete=models.CASCADE,
                                default=1, verbose_name="Operator")
    op_datetime = models.DateTimeField(auto_now=True, blank=True, verbose_name="Operate Datetime", )

    class Meta:
        db_table = "x_calc_item"
        verbose_name = "calc_item"
        ordering = ['express_company', 'item_type', 'order_by', ]


# 特殊的货品列表
class SpecialItemModel(models.Model):
    id = models.AutoField(primary_key=True)
    item_code = models.CharField(max_length=10, default="", verbose_name="Item code", )
    op_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='op_special_item', on_delete=models.CASCADE,
                                default=1, verbose_name="Operator")
    op_datetime = models.DateTimeField(auto_now=True, blank=True, verbose_name="Operate Datetime", )

    class Meta:
        db_table = "x_special_item"
        verbose_name = "special item"
        ordering = ['item_code']


# DPD 的主账单
class DPDMainBillModel(models.Model):
    id = models.AutoField(primary_key=True)
    bill_date = models.DateField(default=timezone.now, blank=True, verbose_name="Bill Date")
    dpd_account_no = models.CharField(max_length=10, default="", blank=True, null=False,
                                      verbose_name="dpd account no", )
    dpd_invoice_no = models.CharField(max_length=10, default="", blank=True, null=False,
                                      verbose_name="dpd invoice no", )
    record_num = models.IntegerField(default=0, null=False, verbose_name="record num.")
    invoice_value = models.DecimalField(default=0, max_digits=10, decimal_places=2, verbose_name='Invoice Value')
    vat = models.DecimalField(default=0, max_digits=10, decimal_places=2, verbose_name='vat Value')
    gross_invoice_value = models.DecimalField(default=0, max_digits=10, decimal_places=2, verbose_name='Invoice Value')
    op_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='dpd_bill_main_op', on_delete=models.CASCADE,
                                default=1, verbose_name="Operator")
    op_datetime = models.DateTimeField(auto_now=True, blank=True, verbose_name="Operate Datetime", )

    class Meta:
        db_table = "x_dpd_bill_main"
        verbose_name = "dpd_bill_main"
        unique_together = ("dpd_account_no", "dpd_invoice_no")
        ordering = ['bill_date', 'dpd_account_no', 'dpd_invoice_no', ]


# DPD 的 账单明细
class DPDBillDetailModel(models.Model):
    id = models.AutoField(primary_key=True)
    bill_date = models.DateField(default=timezone.now, blank=True, verbose_name="Bill Date")
    dpd_account_no = models.CharField(max_length=10, default="", blank=True, null=False,
                                      verbose_name="dpd account no", )
    dpd_invoice_no = models.CharField(max_length=10, default="", blank=True, null=False,
                                      verbose_name="dpd invoice no", )
    parcel_id = models.CharField(max_length=50, default="", blank=True, null=False, verbose_name="parcel_id", )
    product_code = models.CharField(max_length=18, blank=True, null=False, default="", verbose_name="product_code", )
    product_description = models.CharField(max_length=18, blank=True, null=False, default="",
                                           verbose_name="product_description", )
    service_code = models.IntegerField(default=0, blank=True, null=False, verbose_name="service_code")
    service_description = models.CharField(max_length=10, blank=True, null=False, default="",
                                           verbose_name="service_description", )
    mi_code = models.CharField(max_length=50, blank=True, null=False, default="", verbose_name="mi_code", )
    weight = models.DecimalField(default=0, blank=True, max_digits=7, decimal_places=2, verbose_name='weight')
    qty = models.IntegerField(default=0, blank=True, null=False, verbose_name="qty")
    revenue = models.DecimalField(default=0, blank=True, max_digits=10, decimal_places=2, verbose_name='revenue')
    fuel_surcharge = models.DecimalField(default=0, blank=True, max_digits=10, decimal_places=2,
                                         verbose_name='fuel_surcharge')
    third_party_collection = models.DecimalField(default=0, blank=True, max_digits=10, decimal_places=2,
                                                 verbose_name='third_party_collection')
    fourth_party_collection = models.DecimalField(default=0, blank=True, max_digits=10, decimal_places=2,
                                                  verbose_name='fourth_party_collection')
    congestion = models.DecimalField(default=0, blank=True, max_digits=10, decimal_places=2, verbose_name='congestion')
    eu_clearance = models.DecimalField(default=0, blank=True, max_digits=10, decimal_places=2,
                                       verbose_name='eu_clearance')
    return_charge = models.DecimalField(default=0, blank=True, max_digits=10, decimal_places=2, verbose_name='revenue')
    failed_collection = models.DecimalField(default=0, blank=True, max_digits=10, decimal_places=2,
                                            verbose_name='failed_collection')
    scottish_zone = models.DecimalField(default=0, blank=True, max_digits=10, decimal_places=2,
                                        verbose_name='scottish_zone')
    tax_prepaid = models.DecimalField(default=0, blank=True, max_digits=10, decimal_places=2,
                                      verbose_name='tax_prepaid')
    handling = models.DecimalField(default=0, blank=True, max_digits=10, decimal_places=2, verbose_name='revenue')
    contractual_liability = models.DecimalField(default=0, blank=True, max_digits=10, decimal_places=2,
                                                verbose_name='contractual_liability')
    oversize_exports = models.DecimalField(default=0, blank=True, max_digits=10, decimal_places=2,
                                           verbose_name='oversize_exports')
    unsuccessful_eu_export = models.DecimalField(default=0, blank=True, max_digits=10, decimal_places=2,
                                                 verbose_name='unsuccessful_eu_export')
    eu_export_return = models.DecimalField(default=0, blank=True, max_digits=10, decimal_places=2,
                                           verbose_name='eu_export_return')
    is_use = models.BooleanField(default=False)
    used_bill_year = models.IntegerField(default=0, null=False, verbose_name="used_bill_year")
    used_bill_month = models.IntegerField(default=0, null=False, verbose_name="used_bill_month")

    op_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='op_dpd_detail_op', on_delete=models.CASCADE,
                                default=1, verbose_name="Operator")
    op_datetime = models.DateTimeField(auto_now=True, blank=True, verbose_name="Operate Datetime", )

    class Meta:
        db_table = "x_dpd_bill_detail"
        verbose_name = "dpd_bill_detail"
        ordering = ['bill_date', 'dpd_account_no', 'dpd_invoice_no', 'parcel_id', ]
        unique_together = ("dpd_account_no", "dpd_invoice_no", "parcel_id",)


# dpd_congestion_postcode
class DPDCongestionPostcodeModel(models.Model):
    id = models.AutoField(primary_key=True)
    postcode_begin = models.CharField(max_length=6, null=False, default="", verbose_name="Postcode_begin", )
    postcode_end = models.CharField(max_length=6, null=False, default="", verbose_name="Postcode_end", )
    express_company = models.CharField(max_length=10, null=False, default="",
                                       verbose_name="express company Code", )
    op_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='op_dpd_congestion_postcode',
                                on_delete=models.CASCADE, default=1, verbose_name="Operator")
    op_datetime = models.DateTimeField(auto_now=True, blank=True, verbose_name="Operate Datetime", )

    class Meta:
        db_table = "x_mi_dpd_congestion_postcode"
        verbose_name = "dpd_congestion_postcode"
        unique_together = ("postcode_begin", "express_company",)


# 燃油费明细
class FuelSurchargeModel(models.Model):
    id = models.AutoField(primary_key=True)
    express_company = models.CharField(max_length=10, null=False, default="UPS", verbose_name="express company Code", )
    begin_date = models.DateField(blank=True, verbose_name="finished Datetime")
    end_date = models.DateField(blank=True, verbose_name="finished Datetime")
    fuel_surcharge = models.DecimalField(default=0, max_digits=6, decimal_places=2, verbose_name='Fuel Surcharge')
    range = models.CharField(max_length=10, null=False, default="UK", verbose_name="within_range", )
    op_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='op_fuel_surcharge', on_delete=models.CASCADE,
                                default=1, verbose_name="Operator")
    op_datetime = models.DateTimeField(auto_now=True, blank=True, verbose_name="Operate Datetime", )

    class Meta:
        db_table = "x_fuel_surcharge"
        verbose_name = "fuel_surcharge_detail"
        unique_together = ('begin_date', 'express_company', 'range',)
        ordering = ['-begin_date', ]


# Rental Bill 的主账单
class RentalBillModel(models.Model):
    id = models.AutoField(primary_key=True)
    bill_year = models.IntegerField(default=0, null=False, verbose_name="bill_year")
    bill_month = models.IntegerField(default=0, null=False, verbose_name="bill_year")
    record_num = models.IntegerField(default=0, null=False, verbose_name="record num.")
    fee_unit = models.DecimalField(default=0, blank=True, max_digits=10, decimal_places=4, verbose_name='fee_unit')
    fee_total = models.DecimalField(default=0, blank=True, max_digits=10, decimal_places=2, verbose_name='fee_total')
    op_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='dpd_rental_bill_op', on_delete=models.CASCADE,
                                default=1, verbose_name="Operator")
    op_datetime = models.DateTimeField(auto_now=True, blank=True, verbose_name="Operate Datetime", )

    class Meta:
        db_table = "x_rental_main"
        verbose_name = "x_rental_main"
        unique_together = ("bill_year", "bill_month")
        ordering = ['bill_year', 'bill_month', ]


# Rental 的账单明细
class RentalBillDetailModel(models.Model):
    id = models.AutoField(primary_key=True)
    bill_date = models.DateField(default=timezone.now, blank=True, verbose_name="Bill Date")
    sku = models.CharField(max_length=10, default="", blank=True, null=False, verbose_name="sku", )
    goods_id = models.CharField(max_length=10, default="", blank=True, null=False, verbose_name="goods id", )
    unit_volume = models.DecimalField(default=0, blank=True, max_digits=9, decimal_places=6,
                                      verbose_name='unit_volume')
    qty = models.IntegerField(default=0, blank=True, null=False, verbose_name="qty")
    pallet_qty = models.IntegerField(default=0, blank=True, null=False, verbose_name='unit_volume')
    total_volume = models.DecimalField(default=0, blank=True, max_digits=9, decimal_places=4,
                                       verbose_name='unit_volume')
    fee_unit = models.DecimalField(default=0, blank=True, max_digits=10, decimal_places=4, verbose_name='fee_unit')
    fee_total = models.DecimalField(default=0, blank=True, max_digits=10, decimal_places=4, verbose_name='fee_total')
    op_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='op_rental_detail_op', on_delete=models.CASCADE,
                                default=1, verbose_name="Operator")
    op_datetime = models.DateTimeField(auto_now=True, blank=True, verbose_name="Operate Datetime", )

    class Meta:
        db_table = "x_rental_detail"
        verbose_name = "x_rental_detail"
        ordering = ['bill_date', 'sku', ]
        unique_together = ('bill_date', 'sku',)


# Rental unit price 仓租费用的单价维护
class RentalPriceModel(models.Model):
    id = models.AutoField(primary_key=True)
    fee_unit = models.DecimalField(default=0, blank=True, max_digits=10, decimal_places=4, verbose_name='fee_total')
    op_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='dpd_rental_price_op', on_delete=models.CASCADE,
                                default=1, verbose_name="Operator")
    op_datetime = models.DateTimeField(auto_now=True, blank=True, verbose_name="Operate Datetime", )

    class Meta:
        db_table = "x_rental_price"
        verbose_name = "x_rental_price"


class FLCTempModel(models.Model):
    id = models.AutoField(primary_key=True)
    order_no = models.CharField(max_length=100, null=False, blank=True, default='',  verbose_name="order_no", )
    deliver_no = models.CharField(max_length=100, null=False,  blank=True, default='',  verbose_name="deliver_no",)
    is_scan = models.IntegerField(default=0, blank=True, null=False, verbose_name='is_scan')

    class Meta:
        db_table = "flc_temp"
        verbose_name = "flc_temp"


class FLCTempCounterModel(models.Model):
    id = models.AutoField(primary_key=True)
    counter = models.CharField(max_length=10, null=False, blank=True, default='',  verbose_name="counter", )
    qty = models.IntegerField(default=0, blank=True, null=False, verbose_name='qty')

    class Meta:
        db_table = "flc_temp_counter"
        verbose_name = "flc_temp_counter"
