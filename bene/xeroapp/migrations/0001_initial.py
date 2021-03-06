# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-08-11 11:35
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('xerodb_id', models.CharField(blank=True, max_length=255, primary_key=True, serialize=False, verbose_name='Xero ID')),
                ('name', models.CharField(blank=True, max_length=255, verbose_name='Name of Contact')),
                ('number', models.CharField(blank=True, max_length=50, verbose_name='Account number')),
            ],
        ),
        migrations.CreateModel(
            name='ContactGroup',
            fields=[
                ('xerodb_id', models.CharField(blank=True, max_length=255, primary_key=True, serialize=False, verbose_name='Xero ID')),
                ('name', models.CharField(blank=True, max_length=255, verbose_name='Name of ContactGroup')),
            ],
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('xerodb_id', models.CharField(blank=True, max_length=255, primary_key=True, serialize=False, verbose_name='Xero ID')),
                ('currency_code', models.CharField(blank=True, max_length=3, verbose_name='Currency Code')),
                ('currency_rate', models.DecimalField(blank=True, decimal_places=8, default=0, max_digits=16, verbose_name='CurrencyRate')),
                ('inv_number', models.CharField(blank=True, default='', max_length=50, verbose_name='Status')),
                ('inv_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Date')),
                ('nett', models.DecimalField(decimal_places=2, default=0, max_digits=16, verbose_name='Nett')),
                ('gross', models.DecimalField(decimal_places=2, default=0, max_digits=16, verbose_name='Gross')),
                ('tax', models.DecimalField(decimal_places=2, default=0, max_digits=16, verbose_name='Tax')),
                ('status', models.CharField(blank=True, default='', max_length=255, verbose_name='Status')),
                ('invoice_type', models.CharField(blank=True, default='', max_length=255, verbose_name='Invoice Type')),
                ('updated_date_utc', models.DateTimeField(default=django.utils.timezone.now, verbose_name='UpdatedDateUTC')),
                ('contact_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='xeroapp.Contact')),
            ],
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('xerodb_id', models.CharField(blank=True, max_length=255, primary_key=True, serialize=False, verbose_name='Xero ID')),
                ('code', models.CharField(blank=True, max_length=255, verbose_name='Item Code')),
                ('name', models.CharField(blank=True, max_length=255, verbose_name='Item Name')),
                ('cost_price', models.DecimalField(decimal_places=4, max_digits=16, verbose_name='Cost Price')),
                ('sales_price', models.DecimalField(decimal_places=4, max_digits=16, verbose_name='Sales Price')),
            ],
        ),
        migrations.CreateModel(
            name='LineItem',
            fields=[
                ('id', models.UUIDField(primary_key=True, serialize=False)),
                ('quantity', models.DecimalField(decimal_places=4, max_digits=16, verbose_name='Qty')),
                ('price', models.DecimalField(decimal_places=4, max_digits=16, verbose_name='Price')),
                ('invoice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='xeroapp.Invoice')),
                ('item', models.ForeignKey(on_delete=models.CASCADE,
                                        blank=True, null=True, to='xeroapp.Item')),
            ],
        ),
    ]
