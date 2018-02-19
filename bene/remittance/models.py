from django.db import models


# Create your models here.
class RemittanceItem(models.Model):
    state = models.CharField(verbose_name='Remittance State', max_length=15, default='Start')
    orig_name = models.CharField(max_length=255)
    source_doc = models.FilePathField(verbose_name='Source Doc', max_length=255)
    yaml_doc = models.CharField(verbose_name='Yaml Doc', max_length=255)
    orig_file = models.FileField(upload_to='error')  # Upload to should be set
