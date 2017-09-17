# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-09-17 20:32
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('xeroapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='amount_credited',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=16, verbose_name='AmountCredited'),
        ),
        migrations.AddField(
            model_name='invoice',
            name='amount_due',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=16, verbose_name='AmountDue'),
        ),
        migrations.AddField(
            model_name='invoice',
            name='amount_paid',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=16, verbose_name='AmountPaid'),
        ),
        migrations.AddField(
            model_name='invoice',
            name='due_date',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='DueDate'),
        ),
        migrations.AddField(
            model_name='invoice',
            name='expected_payment_date',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='ExpectedPaymentDate'),
        ),
        migrations.AddField(
            model_name='invoice',
            name='fully_paid_on_date',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='FullyPaidOnDate'),
        ),
        migrations.AddField(
            model_name='invoice',
            name='planned_payment_date',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='PlannedPaymentDate'),
        ),
    ]
