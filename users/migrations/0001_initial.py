# Generated by Django 3.1 on 2020-10-07 08:41

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('menu', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailVerifyRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=20, verbose_name='Verify Code')),
                ('email', models.EmailField(max_length=50, verbose_name='Email')),
                ('send_type', models.CharField(choices=[('register', 'Register'), ('forget', 'Forget Password'), ('update_email', 'Modify Email')], max_length=30, verbose_name='Verify Type')),
                ('send_time', models.DateTimeField(default=datetime.datetime.now, verbose_name='Send Date')),
            ],
            options={
                'verbose_name': 'Email Verify',
                'verbose_name_plural': 'Email Verify',
            },
        ),
        migrations.CreateModel(
            name='SlotEmailGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=50, verbose_name='Email')),
                ('desc', models.CharField(max_length=20, verbose_name='Verify Code')),
            ],
            options={
                'verbose_name': 'Email Group',
            },
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('op_position', models.CharField(blank=True, default='UK', max_length=2, verbose_name='Op_position')),
                ('telephone', models.CharField(blank=True, max_length=100, verbose_name='Telephone')),
                ('mod_date', models.DateTimeField(auto_now=True, verbose_name='Last modified')),
                ('profit_percent', models.BooleanField(choices=[(0, 'By Fix Amount'), (1, 'By Percent')], default=0, verbose_name='Profit Mode')),
                ('staff_role', models.IntegerField(blank=True, choices=[(0, 'Custom'), (1, 'Staff-OP'), (2, 'Staff-Warehouse'), (3, 'Staff-Manager')], default=0, verbose_name='Staff_role')),
                ('email_group', models.ForeignKey(default='1', on_delete=django.db.models.deletion.CASCADE, related_name='to_email_group', to='users.slotemailgroup', verbose_name='Email Group')),
                ('role', models.ForeignKey(default='1', on_delete=django.db.models.deletion.CASCADE, related_name='user_role', to='menu.role', verbose_name='System Role')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'User Profile',
            },
        ),
    ]
