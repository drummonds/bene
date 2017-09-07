import os
from django.db import models

from bene.utils.json_parameters import json_to_params

class Company(models.Model):
    name = models.CharField('Name of Company', blank=True, max_length=255)

    def __str__(self):
        return self.name


class Report(models.Model):
    name = models.CharField('Name of Report', blank=True, max_length=255)
    button_name = models.CharField('Button report name', blank=True, max_length=255)
    report_number = models.IntegerField('Report number')
    parameters = models.CharField('URL Parameters', blank=True, max_length=255)  # Converting to JSON

    def __str__(self):
        return self.name

    @property
    def url_parameters(self):
        return json_to_params(self.parameters)

def hashed_uploads_dirs(instance, filename):
    """Returns path with md5 hash as directory"""
    return os.path.join(instance.md5, filename)


class FilebabyFile(models.Model):
    """This holds a single user uploaded file"""
    f = models.FileField(upload_to='.')
    # photo = models.FileField(upload_to='candidate-photos')
    #f = models.FileField(upload_to='%Y/%m/%d')  # Date-based directories
    #f = models.FileField(upload_to=hashed_uploads_dirs)  # Callback defined
    md5 = models.CharField(max_length=32)


class RemittanceFile(models.Model):
    """This holds a single user uploaded file"""
    f = models.FileField(upload_to='/Remittance/')
    # photo = models.FileField(upload_to='candidate-photos')
    #f = models.FileField(upload_to='%Y/%m/%d')  # Date-based directories
    #f = models.FileField(upload_to=hashed_uploads_dirs)  # Callback defined
    md5 = models.CharField(max_length=32)
