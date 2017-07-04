from django.db import models

class Company(models.Model):
    name = models.CharField('Name of Company', blank=True, max_length=255)

    def __str__(self):
        return self.name


class Report(models.Model):
    name = models.CharField('Name of Report', blank=True, max_length=255)
    button_name = models.CharField('Button report name', blank=True, max_length=255)
    report_number = models.IntegerField('Report number')
    parameters = models.CharField('URL Parameters', blank=True, max_length=255)

    def __str__(self):
        return self.name

