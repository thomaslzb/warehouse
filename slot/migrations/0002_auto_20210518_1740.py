# Generated by Django 3.1.11 on 2021-05-18 16:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('slot', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='haulier',
            name='code',
            field=models.CharField(default='', max_length=6, unique=True, verbose_name='Code'),
        ),
    ]
