# Generated by Django 3.1.11 on 2021-05-18 15:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('code', models.CharField(default='', max_length=4, unique=True, verbose_name='Code')),
                ('name', models.CharField(default='', max_length=100, null=True, verbose_name='Company Name')),
                ('contact', models.CharField(blank=True, default='', max_length=100, null=True, verbose_name='Contact')),
                ('telephone', models.CharField(blank=True, default='', max_length=100, null=True, verbose_name='Telephone')),
                ('email', models.CharField(blank=True, default='', max_length=250, null=True, verbose_name='Email')),
                ('icon_lg', models.CharField(blank=True, default='', max_length=250, null=True, verbose_name='Icon URL(Big)')),
                ('icon_sm', models.CharField(blank=True, default='', max_length=250, null=True, verbose_name='Icon URL(Small)')),
                ('is_use', models.IntegerField(choices=[(1, 'Normal'), (0, 'Stop')], default=1, verbose_name='Is Normal')),
                ('op_last_update', models.DateTimeField(auto_now=True, verbose_name='Operate Datetime')),
                ('op_user', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Operator')),
            ],
            options={
                'verbose_name': 'Company',
                'db_table': 'q_company',
            },
        ),
        migrations.CreateModel(
            name='EuroCountry',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('country', models.CharField(default='', max_length=50, verbose_name='Country')),
                ('belong', models.CharField(choices=[('UK', 'UK'), ('EURO', 'EUROPEAN')], default='EURO', max_length=4, verbose_name='Belong')),
                ('op_last_update', models.DateTimeField(auto_now=True, verbose_name='Operate Datetime')),
                ('op_user', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Operator')),
            ],
            options={
                'verbose_name': 'Country',
                'db_table': 'q_euro_country',
                'unique_together': {('country', 'belong')},
            },
        ),
        migrations.CreateModel(
            name='ServiceType',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(default='', max_length=20, verbose_name='ServiceName')),
                ('description', models.CharField(blank=True, default='', max_length=200, verbose_name='description')),
                ('base_price', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=6, verbose_name='Base Price')),
                ('max_weight', models.DecimalField(blank=True, decimal_places=0, default=0, max_digits=4, verbose_name='Max Weight(kg)')),
                ('max_length', models.DecimalField(blank=True, decimal_places=0, default=0, max_digits=4, verbose_name='Max Length(cm)')),
                ('max_girth', models.DecimalField(blank=True, decimal_places=0, default=0, max_digits=4, verbose_name='Max Girth(cm)')),
                ('op_last_update', models.DateTimeField(auto_now=True, verbose_name='Operate Datetime')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quote.company', verbose_name='Belong Company')),
                ('op_user', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Operator')),
            ],
            options={
                'verbose_name': 'Service Type',
                'db_table': 'q_service_type',
                'unique_together': {('name', 'company')},
            },
        ),
        migrations.CreateModel(
            name='UKRange',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('area', models.CharField(default='', max_length=50, unique=True, verbose_name='Area')),
                ('example_postcode', models.CharField(default='', max_length=10, verbose_name='Example Postcode')),
                ('op_last_update', models.DateTimeField(auto_now=True, verbose_name='Operate Datetime')),
            ],
            options={
                'verbose_name': 'UK Area',
                'db_table': 'q_uk_range',
                'unique_together': {('area',)},
            },
        ),
        migrations.CreateModel(
            name='ZoneName',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('zone_name', models.CharField(default='', max_length=10, verbose_name='Zone')),
                ('description', models.CharField(blank=True, default='', max_length=100, verbose_name='description')),
                ('op_last_update', models.DateTimeField(auto_now=True, verbose_name='Operate Datetime')),
                ('belong', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='quote.ukrange', verbose_name='Belong UK Range')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quote.company', verbose_name='Belong Company')),
                ('op_user', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Operator')),
            ],
            options={
                'verbose_name': 'Zone',
                'db_table': 'q_zone',
                'unique_together': {('company', 'zone_name')},
            },
        ),
        migrations.CreateModel(
            name='ZoneSurcharge',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('minimum_price', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=8, verbose_name='Minimum Price')),
                ('percent', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=8, verbose_name='Percent(%)')),
                ('plus_price', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=8, verbose_name='plus_price')),
                ('description', models.CharField(blank=True, default='', max_length=300, verbose_name='description')),
                ('op_last_update', models.DateTimeField(auto_now=True, verbose_name='Operate Datetime')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quote.company', verbose_name='Belong Company')),
                ('op_user', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Operator')),
                ('service_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quote.servicetype', verbose_name='Service Type')),
                ('zone', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quote.zonename', verbose_name='Zone Name')),
            ],
            options={
                'verbose_name': 'Zone Surcharge',
                'db_table': 'q_zone_surcharge',
                'unique_together': {('company', 'service_type', 'zone')},
            },
        ),
        migrations.CreateModel(
            name='ZoneDetail',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('begin', models.CharField(default='', max_length=10, verbose_name='Begin')),
                ('end', models.CharField(default='', max_length=10, verbose_name='End')),
                ('op_last_update', models.DateTimeField(auto_now=True, verbose_name='Operate Datetime')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quote.company', verbose_name='Belong Company')),
                ('op_user', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Operator')),
                ('zone', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quote.zonename', verbose_name='Zone Name')),
            ],
            options={
                'verbose_name': 'Zone Detail',
                'db_table': 'q_zone_detail',
                'unique_together': {('company', 'zone', 'begin')},
            },
        ),
        migrations.CreateModel(
            name='UserSetupProfit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_uk', models.CharField(choices=[('UK', 'UK'), ('EURO', 'EUROPEAN')], default='UK', max_length=4, verbose_name='Belong')),
                ('fix_amount', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=8, verbose_name='Fix Amount')),
                ('percent', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=8, verbose_name='Percent')),
                ('op_last_update', models.DateTimeField(auto_now=True, verbose_name='Operate Datetime')),
                ('euro_area', models.ForeignKey(blank=True, default='', null=True, on_delete=django.db.models.deletion.CASCADE, to='quote.eurocountry', verbose_name='Euro Country')),
                ('uk_area', models.ForeignKey(blank=True, default='', null=True, on_delete=django.db.models.deletion.CASCADE, to='quote.ukrange', verbose_name='UK Area')),
                ('user', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Customer')),
            ],
            options={
                'verbose_name': 'Profit Setup',
                'db_table': 'q_user_setup_profit',
                'ordering': ('user', 'is_uk', 'uk_area', 'euro_area'),
                'unique_together': {('user', 'is_uk', 'uk_area', 'euro_area')},
            },
        ),
        migrations.CreateModel(
            name='UKPostcodeRange',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('postcode_begin', models.CharField(default='', max_length=10, verbose_name='Begin')),
                ('postcode_end', models.CharField(default='', max_length=10, verbose_name='End')),
                ('op_last_update', models.DateTimeField(auto_now=True, verbose_name='Operate Datetime')),
                ('area', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quote.ukrange', verbose_name='UK Area')),
            ],
            options={
                'verbose_name': 'UK Postcode Range',
                'db_table': 'q_uk_postcode',
                'unique_together': {('area', 'postcode_begin')},
            },
        ),
        migrations.CreateModel(
            name='Surcharge',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('surcharge_name', models.CharField(default='', max_length=20, verbose_name='Surcharge Name')),
                ('description', models.CharField(blank=True, default='', max_length=300, verbose_name='description')),
                ('price', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=8, verbose_name='Price')),
                ('percent', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=8, verbose_name='Percent(%)')),
                ('op_last_update', models.DateTimeField(auto_now=True, verbose_name='Operate Datetime')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quote.company', verbose_name='Belong Company')),
                ('op_user', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Operator')),
            ],
            options={
                'verbose_name': 'Surcharge',
                'db_table': 'q_surcharge',
                'unique_together': {('company', 'surcharge_name')},
            },
        ),
        migrations.CreateModel(
            name='EuroPrice',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('basic_price', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=8, verbose_name='Basic_Price')),
                ('over_weight_price', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=8, verbose_name='OverWeight Price')),
                ('clearance_charge', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=8, verbose_name='Clearance Charge')),
                ('minimum_charge', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=8, verbose_name='minimum_charge(PerItem)')),
                ('description', models.CharField(blank=True, default='', max_length=300, verbose_name='description')),
                ('op_last_update', models.DateTimeField(auto_now=True, verbose_name='Operate Datetime')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quote.company', verbose_name='Belong Company')),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quote.eurocountry', verbose_name='Country')),
                ('op_user', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Operator')),
            ],
            options={
                'verbose_name': 'Euro Price',
                'db_table': 'q_euro_price',
                'unique_together': {('company', 'country')},
            },
        ),
    ]