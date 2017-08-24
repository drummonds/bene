# /uploadering/filebaby/forms.py

from django import forms

from .models import FilebabyFile, RemittanceFile


class FilebabyForm(forms.ModelForm):
    """Upload files with this form"""
    class Meta:
        model = FilebabyFile
        exclude = ('md5',)


class RemittanceForm(forms.ModelForm):
    """Upload files with this form"""
    class Meta:
        model = RemittanceFile
        exclude = ('md5',)
