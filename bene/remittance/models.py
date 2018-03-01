import os

from django.core.exceptions import ValidationError
from django.core.files import File
from django.core.files.storage import default_storage as storage
from django.db import models
from django.utils import timezone

from .utils import date_to_path
from .pdf_to_txt import pdf_to_text

def remittance_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/
    return f'remittances/{date_to_path(instance.uploaded_at)}/{filename}'


# Create your models here.
class RemittanceItem(models.Model):
    state = models.CharField(verbose_name='Remittance State',
                             max_length=15, default='Start')
    orig_name = models.CharField(max_length=255, default='')
    source_doc = models.FilePathField(verbose_name='Source Doc', max_length=255, null=True)
    yaml_doc = models.CharField(verbose_name='Yaml Doc', max_length=255, default='')
    orig_file = models.FileField(upload_to=remittance_directory_path, null=True)  # Upload to should be set
    uploaded_at = models.DateTimeField(default=timezone.now)

    def file_count(self, file_name):
        path_name = self.orig_file.name
        try:
            self.orig_name = os.path.split(path_name)[1]
        except IndexError:
            self.orig_name = 'Not parseable'
        return RemittanceItem.objects.filter(orig_name = self.orig_name).count()

    def clean(self):
        if self.file_count(self.orig_file.name) > 0:
            raise ValidationError('File has already been added.')

    def save(self, *args, **kwargs):
        if self.file_count(self.orig_file.name) == 0:
            path_name = self.orig_file.name
            try:
                self.orig_name = os.path.split(path_name)[1]
            except IndexError:
                self.orig_name = 'Not parseable'
            super().save(*args, **kwargs)  # Call the "real" save() method.
        else:
            raise ValidationError('File has already been added.')
        # do_something_else()
        # copy to text file
        self.trial_copy()
        new_file = self.orig_file
        new_path, file_name = os.path.split(new_file.name)
        pdf_to_text(new_path, file_name)


    def trial_copy(self):
        new_file = self.orig_file
        new_path = os.path.split(new_file.name)[0]
        with storage.open(new_path + '/hello_world.txt', 'w') as f:
            myfile = File(f)
            myfile.write('Hello World')
