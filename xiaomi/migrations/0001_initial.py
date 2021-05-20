# Generated by Django 3.1.11 on 2021-05-18 15:33

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='FLCTempCounterModel',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('counter', models.CharField(blank=True, default='', max_length=10, verbose_name='counter')),
                ('qty', models.IntegerField(blank=True, default=0, verbose_name='qty')),
            ],
            options={
                'verbose_name': 'flc_temp_counter',
                'db_table': 'flc_temp_counter',
            },
        ),
        migrations.CreateModel(
            name='FLCTempModel',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('order_no', models.CharField(blank=True, default='', max_length=100, verbose_name='order_no')),
                ('deliver_no', models.CharField(blank=True, default='', max_length=100, verbose_name='deliver_no')),
                ('is_scan', models.IntegerField(blank=True, default=0, verbose_name='is_scan')),
            ],
            options={
                'verbose_name': 'flc_temp',
                'db_table': 'flc_temp',
            },
        ),
        migrations.CreateModel(
            name='UpsBillDetailModel',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('ups_bill_no', models.CharField(blank=True, default='', max_length=10, verbose_name='ups bill no')),
                ('parcel_id', models.CharField(blank=True, default='', max_length=50, verbose_name='parcel id')),
                ('mi_code', models.CharField(default='', max_length=50, verbose_name='Mi Code')),
                ('bill_date', models.DateField(blank=True, verbose_name='finished Datetime')),
                ('delivery_date', models.DateField(blank=True, verbose_name='delivery Datetime')),
                ('fee_code', models.CharField(default='', max_length=3, verbose_name='Fee Code')),
                ('fee_desc', models.CharField(default='', max_length=60, verbose_name='Fee desc')),
                ('fee_currency', models.CharField(default='', max_length=3, verbose_name='Fee Currency')),
                ('fee_amount', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=12, verbose_name='Fee Amount')),
                ('is_use', models.BooleanField(default=False)),
                ('used_bill_year', models.IntegerField(default=0, verbose_name='used_bill_year')),
                ('used_bill_month', models.IntegerField(default=0, verbose_name='used_bill_month')),
                ('op_datetime', models.DateTimeField(auto_now=True, verbose_name='Operate Datetime')),
                ('op_user', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='op_ups_account', to=settings.AUTH_USER_MODEL, verbose_name='Operator')),
            ],
            options={
                'verbose_name': 'ups_bill_detail',
                'db_table': 'x_ups_bill_detail',
                'ordering': ['bill_date', 'ups_bill_no', 'parcel_id', 'mi_code'],
            },
        ),
        migrations.CreateModel(
            name='SpecialItemModel',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('item_code', models.CharField(default='', max_length=10, verbose_name='Item code')),
                ('op_datetime', models.DateTimeField(auto_now=True, verbose_name='Operate Datetime')),
                ('op_user', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='op_special_item', to=settings.AUTH_USER_MODEL, verbose_name='Operator')),
            ],
            options={
                'verbose_name': 'special item',
                'db_table': 'x_special_item',
                'ordering': ['item_code'],
            },
        ),
        migrations.CreateModel(
            name='RentalPriceModel',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('fee_unit', models.DecimalField(blank=True, decimal_places=4, default=0, max_digits=10, verbose_name='fee_total')),
                ('op_datetime', models.DateTimeField(auto_now=True, verbose_name='Operate Datetime')),
                ('op_user', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='dpd_rental_price_op', to=settings.AUTH_USER_MODEL, verbose_name='Operator')),
            ],
            options={
                'verbose_name': 'x_rental_price',
                'db_table': 'x_rental_price',
            },
        ),
        migrations.CreateModel(
            name='DcgBillDetailTotalModel',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('bill_year', models.IntegerField(default=2021, verbose_name='Bill Year')),
                ('bill_month', models.IntegerField(default=1, verbose_name='Bill Month')),
                ('display_order', models.IntegerField(default=0, verbose_name='display order')),
                ('express_company', models.CharField(default='', max_length=10, verbose_name='express company Code')),
                ('item_type', models.CharField(choices=[('Delivery', 'Delivery Fee'), ('Handle', 'Handle Fee')], default='Delivery', max_length=10, verbose_name='Item Type')),
                ('item', models.CharField(default='', max_length=150, verbose_name='Item')),
                ('record_num', models.IntegerField(default=1, verbose_name='Record Num')),
                ('qty', models.IntegerField(blank=True, default=0, verbose_name='qty')),
                ('unit_price', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, verbose_name='unit_price')),
                ('sub_total_amount', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, verbose_name='sub_total_amount')),
                ('op_datetime', models.DateTimeField(auto_now=True, verbose_name='Operate Datetime')),
                ('op_user', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='op_dcg_bill_detail_total', to=settings.AUTH_USER_MODEL, verbose_name='Operator')),
            ],
            options={
                'verbose_name': 'dcg_bill_detail_total',
                'db_table': 'x_dcg_bill_detail_total',
                'ordering': ['bill_year', 'bill_month'],
            },
        ),
        migrations.CreateModel(
            name='DcgBillDetailHandleModel',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('bill_year', models.IntegerField(default=2021, verbose_name='Bill Year')),
                ('bill_month', models.IntegerField(default=1, verbose_name='Bill Month')),
                ('mi_code', models.CharField(default='', max_length=50, unique=True, verbose_name='Mi Code')),
                ('package_code', models.CharField(default='', max_length=21, null=True, verbose_name='package_code')),
                ('express_company', models.CharField(default='', max_length=10, verbose_name='express company Code')),
                ('parcel_id', models.CharField(blank=True, default='', max_length=50, null=True, verbose_name='ups parcel id')),
                ('postcode', models.CharField(blank=True, default='', max_length=10, null=True, verbose_name='postcode')),
                ('ready_datetime', models.DateTimeField(blank=True, null=True, verbose_name='ready_datetime')),
                ('goods_id', models.CharField(blank=True, default='', max_length=100, null=True, verbose_name='goods_id')),
                ('total_qty', models.IntegerField(default=1, verbose_name='Total Qty.')),
                ('weight', models.DecimalField(blank=True, decimal_places=5, default=0, max_digits=12, verbose_name='weight')),
                ('handle_fee', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=12, verbose_name='handle_fee')),
                ('extra_handle_fee', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=12, verbose_name='extra_handle_fee')),
                ('special_item_fee', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=12, verbose_name='special_item_fee')),
                ('package_fee', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=12, verbose_name='package_fee')),
                ('total_amount', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=12, verbose_name='total_amount')),
                ('total_cost', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=12, verbose_name='total_cost')),
                ('total_profit', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=12, verbose_name='total_profit')),
                ('op_datetime', models.DateTimeField(auto_now=True, verbose_name='Operate Datetime')),
                ('op_user', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='op_bill_detail_handle', to=settings.AUTH_USER_MODEL, verbose_name='Operator')),
            ],
            options={
                'verbose_name': 'dcg_bill_detail_handle',
                'db_table': 'x_detail_handle',
                'ordering': ['bill_year', 'bill_month'],
            },
        ),
        migrations.CreateModel(
            name='CalculateItemModel',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('item_type', models.CharField(choices=[('Delivery', 'Delivery Fee'), ('Handle', 'Handle Fee')], default='Delivery', max_length=10, verbose_name='Item Type')),
                ('item', models.CharField(default='', max_length=50, verbose_name='Item')),
                ('item_desc', models.CharField(default='', max_length=100, null=True, verbose_name='Item_desc')),
                ('express_company', models.CharField(default='', max_length=10, verbose_name='express company Code')),
                ('zone', models.CharField(default='ZONE1', max_length=10, null=True, verbose_name='Zone Area')),
                ('max_qty', models.IntegerField(default=0, verbose_name='max qty')),
                ('min_weight', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='min weight')),
                ('max_weight', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='min weight')),
                ('unit_price', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Unit Price')),
                ('remark', models.CharField(default='', max_length=100, null=True, verbose_name='Item_remark')),
                ('order_by', models.IntegerField(default=0, verbose_name='order by')),
                ('is_used', models.BooleanField(default=True, verbose_name='is Used')),
                ('op_datetime', models.DateTimeField(auto_now=True, verbose_name='Operate Datetime')),
                ('op_user', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='op_calc_item', to=settings.AUTH_USER_MODEL, verbose_name='Operator')),
            ],
            options={
                'verbose_name': 'calc_item',
                'db_table': 'x_calc_item',
                'ordering': ['express_company', 'item_type', 'order_by'],
            },
        ),
        migrations.CreateModel(
            name='UpsMainBillModel',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('bill_date', models.DateField(blank=True, default=django.utils.timezone.now, verbose_name='Bill Date')),
                ('ups_bill_no', models.CharField(blank=True, default='', max_length=10, unique=True, verbose_name='ups bill no')),
                ('record_num', models.IntegerField(default=0, verbose_name='record num.')),
                ('total_amount', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=12, verbose_name='total_amount')),
                ('op_datetime', models.DateTimeField(auto_now=True, verbose_name='Operate Datetime')),
                ('op_user', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='ups_manage_bill_op', to=settings.AUTH_USER_MODEL, verbose_name='Operator')),
            ],
            options={
                'verbose_name': 'ups_bill_main',
                'db_table': 'x_ups_bill_main',
                'ordering': ['bill_date', 'ups_bill_no'],
                'unique_together': {('ups_bill_no',)},
            },
        ),
        migrations.CreateModel(
            name='RentalBillModel',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('bill_year', models.IntegerField(default=0, verbose_name='bill_year')),
                ('bill_month', models.IntegerField(default=0, verbose_name='bill_year')),
                ('record_num', models.IntegerField(default=0, verbose_name='record num.')),
                ('fee_unit', models.DecimalField(blank=True, decimal_places=4, default=0, max_digits=10, verbose_name='fee_unit')),
                ('fee_total', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, verbose_name='fee_total')),
                ('op_datetime', models.DateTimeField(auto_now=True, verbose_name='Operate Datetime')),
                ('op_user', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='dpd_rental_bill_op', to=settings.AUTH_USER_MODEL, verbose_name='Operator')),
            ],
            options={
                'verbose_name': 'x_rental_main',
                'db_table': 'x_rental_main',
                'ordering': ['bill_year', 'bill_month'],
                'unique_together': {('bill_year', 'bill_month')},
            },
        ),
        migrations.CreateModel(
            name='RentalBillDetailModel',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('bill_date', models.DateField(blank=True, default=django.utils.timezone.now, verbose_name='Bill Date')),
                ('sku', models.CharField(blank=True, default='', max_length=10, verbose_name='sku')),
                ('goods_id', models.CharField(blank=True, default='', max_length=10, verbose_name='goods id')),
                ('unit_volume', models.DecimalField(blank=True, decimal_places=6, default=0, max_digits=9, verbose_name='unit_volume')),
                ('qty', models.IntegerField(blank=True, default=0, verbose_name='qty')),
                ('pallet_qty', models.IntegerField(blank=True, default=0, verbose_name='unit_volume')),
                ('total_volume', models.DecimalField(blank=True, decimal_places=4, default=0, max_digits=9, verbose_name='unit_volume')),
                ('fee_unit', models.DecimalField(blank=True, decimal_places=4, default=0, max_digits=10, verbose_name='fee_unit')),
                ('fee_total', models.DecimalField(blank=True, decimal_places=4, default=0, max_digits=10, verbose_name='fee_total')),
                ('op_datetime', models.DateTimeField(auto_now=True, verbose_name='Operate Datetime')),
                ('op_user', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='op_rental_detail_op', to=settings.AUTH_USER_MODEL, verbose_name='Operator')),
            ],
            options={
                'verbose_name': 'x_rental_detail',
                'db_table': 'x_rental_detail',
                'ordering': ['bill_date', 'sku'],
                'unique_together': {('bill_date', 'sku')},
            },
        ),
        migrations.CreateModel(
            name='PostcodeModel',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('postcode_begin', models.CharField(default='', max_length=6, verbose_name='Postcode_begin')),
                ('postcode_end', models.CharField(default='', max_length=6, verbose_name='Postcode_end')),
                ('express_company', models.CharField(default='', max_length=10, verbose_name='express company Code')),
                ('op_datetime', models.DateTimeField(auto_now=True, verbose_name='Operate Datetime')),
                ('op_user', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='op_mi_postcode', to=settings.AUTH_USER_MODEL, verbose_name='Operator')),
            ],
            options={
                'verbose_name': 'mi_postcode',
                'db_table': 'x_mi_postcode',
                'unique_together': {('postcode_begin', 'express_company')},
            },
        ),
        migrations.CreateModel(
            name='MiAccountBillMainModel',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('bill_year', models.IntegerField(default=2021, verbose_name='Bill Year')),
                ('bill_month', models.IntegerField(default=1, verbose_name='Bill Month')),
                ('record_num', models.IntegerField(default=0, verbose_name='record num.')),
                ('is_used', models.BooleanField(default=False)),
                ('op_datetime', models.DateTimeField(auto_now=True, verbose_name='Operate Datetime')),
                ('op_user', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='op_mi_account_main', to=settings.AUTH_USER_MODEL, verbose_name='Operator')),
            ],
            options={
                'verbose_name': 'x_mi_bill_main',
                'db_table': 'x_mi_bill_main',
                'ordering': ['bill_year', 'bill_month'],
                'unique_together': {('bill_year', 'bill_month')},
            },
        ),
        migrations.CreateModel(
            name='MiAccountBillDetailModel',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('bill_year', models.IntegerField(default=2021, verbose_name='Bill Year')),
                ('bill_month', models.IntegerField(default=1, verbose_name='Bill Month')),
                ('mi_code', models.CharField(default='', max_length=50, unique=True, verbose_name='Mi Code')),
                ('express_company', models.CharField(default='', max_length=10, verbose_name='express company Code')),
                ('package_code', models.CharField(default='', max_length=21, null=True, verbose_name='package_code')),
                ('parcel_id', models.CharField(blank=True, default='', max_length=50, null=True, verbose_name='parcel id')),
                ('country', models.CharField(blank=True, default='', max_length=20, null=True, verbose_name='country')),
                ('county', models.CharField(blank=True, default='', max_length=50, null=True, verbose_name='county')),
                ('town', models.CharField(blank=True, default='', max_length=50, null=True, verbose_name='town')),
                ('postcode', models.CharField(blank=True, default='', max_length=10, null=True, verbose_name='postcode')),
                ('ready_datetime', models.DateTimeField(blank=True, null=True, verbose_name='ready_datetime')),
                ('goods_id', models.CharField(blank=True, default='', max_length=100, null=True, verbose_name='goods_id')),
                ('total_qty', models.IntegerField(default=1, verbose_name='Total Qty.')),
                ('weight', models.DecimalField(blank=True, decimal_places=5, default=0, max_digits=12, verbose_name='weight')),
                ('delivery_fee_checked', models.BooleanField(default=False)),
                ('update_bill_year', models.IntegerField(default=0, verbose_name='update_bill_year')),
                ('update_bill_month', models.IntegerField(default=0, verbose_name='update_bill_year')),
                ('op_datetime', models.DateTimeField(auto_now=True, verbose_name='Operate Datetime')),
                ('op_user', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='op_mi_account', to=settings.AUTH_USER_MODEL, verbose_name='Operator')),
            ],
            options={
                'verbose_name': 'x_mi_bill_detail',
                'db_table': 'x_mi_bill_detail',
                'ordering': ['bill_year', 'bill_month', 'mi_code', 'parcel_id'],
                'unique_together': {('mi_code',)},
            },
        ),
        migrations.CreateModel(
            name='FuelSurchargeModel',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('express_company', models.CharField(default='UPS', max_length=10, verbose_name='express company Code')),
                ('begin_date', models.DateField(blank=True, verbose_name='finished Datetime')),
                ('end_date', models.DateField(blank=True, verbose_name='finished Datetime')),
                ('fuel_surcharge', models.DecimalField(decimal_places=2, default=0, max_digits=6, verbose_name='Fuel Surcharge')),
                ('range', models.CharField(default='UK', max_length=10, verbose_name='within_range')),
                ('op_datetime', models.DateTimeField(auto_now=True, verbose_name='Operate Datetime')),
                ('op_user', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='op_fuel_surcharge', to=settings.AUTH_USER_MODEL, verbose_name='Operator')),
            ],
            options={
                'verbose_name': 'fuel_surcharge_detail',
                'db_table': 'x_fuel_surcharge',
                'ordering': ['-begin_date'],
                'unique_together': {('begin_date', 'express_company', 'range')},
            },
        ),
        migrations.CreateModel(
            name='DPDMainBillModel',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('bill_date', models.DateField(blank=True, default=django.utils.timezone.now, verbose_name='Bill Date')),
                ('dpd_account_no', models.CharField(blank=True, default='', max_length=10, verbose_name='dpd account no')),
                ('dpd_invoice_no', models.CharField(blank=True, default='', max_length=10, verbose_name='dpd invoice no')),
                ('record_num', models.IntegerField(default=0, verbose_name='record num.')),
                ('invoice_value', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Invoice Value')),
                ('vat', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='vat Value')),
                ('gross_invoice_value', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Invoice Value')),
                ('op_datetime', models.DateTimeField(auto_now=True, verbose_name='Operate Datetime')),
                ('op_user', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='dpd_bill_main_op', to=settings.AUTH_USER_MODEL, verbose_name='Operator')),
            ],
            options={
                'verbose_name': 'dpd_bill_main',
                'db_table': 'x_dpd_bill_main',
                'ordering': ['bill_date', 'dpd_account_no', 'dpd_invoice_no'],
                'unique_together': {('dpd_account_no', 'dpd_invoice_no')},
            },
        ),
        migrations.CreateModel(
            name='DPDCongestionPostcodeModel',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('postcode_begin', models.CharField(default='', max_length=6, verbose_name='Postcode_begin')),
                ('postcode_end', models.CharField(default='', max_length=6, verbose_name='Postcode_end')),
                ('express_company', models.CharField(default='', max_length=10, verbose_name='express company Code')),
                ('op_datetime', models.DateTimeField(auto_now=True, verbose_name='Operate Datetime')),
                ('op_user', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='op_dpd_congestion_postcode', to=settings.AUTH_USER_MODEL, verbose_name='Operator')),
            ],
            options={
                'verbose_name': 'dpd_congestion_postcode',
                'db_table': 'x_mi_dpd_congestion_postcode',
                'unique_together': {('postcode_begin', 'express_company')},
            },
        ),
        migrations.CreateModel(
            name='DPDBillDetailModel',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('bill_date', models.DateField(blank=True, default=django.utils.timezone.now, verbose_name='Bill Date')),
                ('dpd_account_no', models.CharField(blank=True, default='', max_length=10, verbose_name='dpd account no')),
                ('dpd_invoice_no', models.CharField(blank=True, default='', max_length=10, verbose_name='dpd invoice no')),
                ('parcel_id', models.CharField(blank=True, default='', max_length=50, verbose_name='parcel_id')),
                ('product_code', models.CharField(blank=True, default='', max_length=18, verbose_name='product_code')),
                ('product_description', models.CharField(blank=True, default='', max_length=18, verbose_name='product_description')),
                ('service_code', models.IntegerField(blank=True, default=0, verbose_name='service_code')),
                ('service_description', models.CharField(blank=True, default='', max_length=10, verbose_name='service_description')),
                ('mi_code', models.CharField(blank=True, default='', max_length=50, verbose_name='mi_code')),
                ('weight', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=7, verbose_name='weight')),
                ('qty', models.IntegerField(blank=True, default=0, verbose_name='qty')),
                ('revenue', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, verbose_name='revenue')),
                ('fuel_surcharge', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, verbose_name='fuel_surcharge')),
                ('third_party_collection', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, verbose_name='third_party_collection')),
                ('fourth_party_collection', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, verbose_name='fourth_party_collection')),
                ('congestion', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, verbose_name='congestion')),
                ('eu_clearance', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, verbose_name='eu_clearance')),
                ('return_charge', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, verbose_name='revenue')),
                ('failed_collection', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, verbose_name='failed_collection')),
                ('scottish_zone', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, verbose_name='scottish_zone')),
                ('tax_prepaid', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, verbose_name='tax_prepaid')),
                ('handling', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, verbose_name='revenue')),
                ('contractual_liability', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, verbose_name='contractual_liability')),
                ('oversize_exports', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, verbose_name='oversize_exports')),
                ('unsuccessful_eu_export', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, verbose_name='unsuccessful_eu_export')),
                ('eu_export_return', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, verbose_name='eu_export_return')),
                ('is_use', models.BooleanField(default=False)),
                ('used_bill_year', models.IntegerField(default=0, verbose_name='used_bill_year')),
                ('used_bill_month', models.IntegerField(default=0, verbose_name='used_bill_month')),
                ('op_datetime', models.DateTimeField(auto_now=True, verbose_name='Operate Datetime')),
                ('op_user', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='op_dpd_detail_op', to=settings.AUTH_USER_MODEL, verbose_name='Operator')),
            ],
            options={
                'verbose_name': 'dpd_bill_detail',
                'db_table': 'x_dpd_bill_detail',
                'ordering': ['bill_date', 'dpd_account_no', 'dpd_invoice_no', 'parcel_id'],
                'unique_together': {('dpd_account_no', 'dpd_invoice_no', 'parcel_id')},
            },
        ),
        migrations.CreateModel(
            name='DcgBillModel',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('bill_year', models.IntegerField(default=2021, verbose_name='Bill Year')),
                ('bill_month', models.IntegerField(default=1, verbose_name='Bill Month')),
                ('express_company', models.CharField(default='', max_length=10, verbose_name='express company Code')),
                ('company_bill_list', models.CharField(default='', max_length=400, verbose_name='Bill List')),
                ('last_month_record', models.IntegerField(default=1, verbose_name='last_month_record')),
                ('this_month_record', models.IntegerField(default=1, verbose_name='this_month_record')),
                ('total_record', models.IntegerField(default=1, verbose_name='Total Record')),
                ('total_amount', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=12, verbose_name='Total Amount')),
                ('nett_cost', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=12, verbose_name='nett_cost')),
                ('total_vat', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=12, verbose_name='total_vat')),
                ('total_cost', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=12, verbose_name='total_cost')),
                ('total_profit', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=12, verbose_name='total_profit')),
                ('op_datetime', models.DateTimeField(auto_now=True, verbose_name='Operate Datetime')),
                ('op_user', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='op_total_bill', to=settings.AUTH_USER_MODEL, verbose_name='Operator')),
            ],
            options={
                'verbose_name': 'dcg_bill_main',
                'db_table': 'x_dcg_bill_main',
                'ordering': ['bill_year', 'bill_month'],
                'unique_together': {('bill_year', 'bill_month', 'express_company')},
            },
        ),
        migrations.CreateModel(
            name='DcgBillDetailUPSModel',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('bill_year', models.IntegerField(default=2021, verbose_name='Bill Year')),
                ('bill_month', models.IntegerField(default=1, verbose_name='Bill Month')),
                ('mi_code', models.CharField(default='', max_length=50, verbose_name='Mi Code')),
                ('package_code', models.CharField(default='', max_length=21, null=True, verbose_name='package_code')),
                ('express_company', models.CharField(default='', max_length=10, verbose_name='express company Code')),
                ('parcel_id', models.CharField(blank=True, default='', max_length=50, null=True, verbose_name='ups parcel id')),
                ('postcode', models.CharField(blank=True, default='', max_length=10, null=True, verbose_name='postcode')),
                ('ready_datetime', models.DateTimeField(blank=True, null=True, verbose_name='ready_datetime')),
                ('goods_id', models.CharField(blank=True, default='', max_length=100, null=True, verbose_name='goods_id')),
                ('total_qty', models.IntegerField(default=1, verbose_name='Total Qty.')),
                ('weight', models.DecimalField(blank=True, decimal_places=5, default=0, max_digits=12, verbose_name='weight')),
                ('standard_delivery_fee', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=12, verbose_name='standard_delivery_fee')),
                ('residential', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=12, verbose_name='residential')),
                ('dom_standard_undeliverable_return', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=12, verbose_name='dom_standard_undeliverable_return')),
                ('extended_area_surcharge_destination', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=12, verbose_name='extended_area_surcharge_destination')),
                ('uk_border_fee', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=12, verbose_name='um_border_fee')),
                ('additional_handling', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=12, verbose_name='additional_handling')),
                ('peak_surcharge_additional_handling', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=12, verbose_name='peak_surcharge_additional_handling')),
                ('address_correction_dom_standard', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=12, verbose_name='address_correction_dom_standard')),
                ('fuel_surcharge_rate', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=12, verbose_name='fuel_surcharge_rate')),
                ('fuel_surcharge', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=12, verbose_name='fuel_surcharge')),
                ('total_amount', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=12, verbose_name='total_amount')),
                ('nett_cost', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=12, verbose_name='nett_cost')),
                ('total_vat', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=12, verbose_name='total_vat')),
                ('total_cost', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=12, verbose_name='total_cost')),
                ('total_profit', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=12, verbose_name='total_profit')),
                ('update_year', models.IntegerField(default=2021, verbose_name='Update Year')),
                ('update_month', models.IntegerField(default=1, verbose_name='Update Month')),
                ('ups_bill_no_list', models.CharField(blank=True, default='', max_length=100, null=True, verbose_name='ups_bill_no_list,')),
                ('op_datetime', models.DateTimeField(auto_now=True, verbose_name='Operate Datetime')),
                ('op_user', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='op_bill_detail_ups', to=settings.AUTH_USER_MODEL, verbose_name='Operator')),
            ],
            options={
                'verbose_name': 'dcg_bill_detail_ups',
                'db_table': 'x_detail_ups',
                'ordering': ['bill_year', 'bill_month'],
                'unique_together': {('mi_code', 'update_year', 'update_month')},
            },
        ),
        migrations.CreateModel(
            name='DcgBillDetailDPDModel',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('bill_year', models.IntegerField(default=2021, verbose_name='Bill Year')),
                ('bill_month', models.IntegerField(default=1, verbose_name='Bill Month')),
                ('mi_code', models.CharField(default='', max_length=50, verbose_name='Mi Code')),
                ('package_code', models.CharField(default='', max_length=21, null=True, verbose_name='package_code')),
                ('express_company', models.CharField(default='', max_length=10, verbose_name='express company Code')),
                ('parcel_id', models.CharField(blank=True, default='', max_length=50, verbose_name='parcel id')),
                ('postcode', models.CharField(blank=True, default='', max_length=10, null=True, verbose_name='postcode')),
                ('ready_datetime', models.DateTimeField(blank=True, null=True, verbose_name='ready_datetime')),
                ('goods_id', models.CharField(blank=True, default='', max_length=100, null=True, verbose_name='goods_id')),
                ('total_qty', models.IntegerField(default=1, verbose_name='Total Qty.')),
                ('weight', models.DecimalField(blank=True, decimal_places=5, default=0, max_digits=12, verbose_name='weight')),
                ('standard_delivery_fee', models.DecimalField(blank=True, decimal_places=5, default=0, max_digits=12, verbose_name='standard_delivery_fee')),
                ('additional_fee', models.DecimalField(blank=True, decimal_places=5, default=0, max_digits=12, verbose_name='additional_fee')),
                ('fuel_surcharge_rate', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=12, verbose_name='fuel_surcharge_rate')),
                ('fuel_surcharge', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=12, verbose_name='fuel_surcharge')),
                ('total_amount', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=12, verbose_name='total_amount')),
                ('nett_cost', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=12, verbose_name='nett_cost')),
                ('total_vat', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=12, verbose_name='total_vat')),
                ('total_cost', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=12, verbose_name='total_cost')),
                ('total_profit', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=12, verbose_name='total_profit')),
                ('update_year', models.IntegerField(default=2021, verbose_name='Update Year')),
                ('update_month', models.IntegerField(default=1, verbose_name='Update Month')),
                ('dpd_bill_no_list', models.CharField(blank=True, default='', max_length=100, null=True, verbose_name='ups_bill_no_list,')),
                ('op_datetime', models.DateTimeField(auto_now=True, verbose_name='Operate Datetime')),
                ('op_user', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='op_bill_detail_dpd', to=settings.AUTH_USER_MODEL, verbose_name='Operator')),
            ],
            options={
                'verbose_name': 'dcg_bill_detail_dpd',
                'db_table': 'x_detail_dpd',
                'ordering': ['bill_year', 'bill_month'],
                'unique_together': {('mi_code', 'update_year', 'update_month')},
            },
        ),
    ]
