import os
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


def hashed_uploads_dirs(instance, filename):
    """Returns path with md5 hash as directory"""
    return os.path.join(instance.md5, filename)


class FilebabyFile(models.Model):
    """This holds a single user uploaded file"""
    f = models.FileField(upload_to='.')
    #f = models.FileField(upload_to='%Y/%m/%d')  # Date-based directories
    #f = models.FileField(upload_to=hashed_uploads_dirs)  # Callback defined
    md5 = models.CharField(max_length=32)
