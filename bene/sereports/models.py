from django.db import models
from django.utils import timezone

class Company(models.Model):
    name = models.CharField('Name of Company', blank=True, max_length=255)

    def __str__(self):
        return self.name

class Reports(models.Model):
    name = models.CharField('Name of Report', blank=True, max_length=255)  # store the guid
    button_name = models.CharField('Button report name', blank=True, max_length=255)
    report_number = models.IntegerField('Account number')

    def __str__(self):
        return self.name


