from django.forms import ModelForm

from .models import RemittanceItem

class RemittanceFileForm(ModelForm):
    """Upload files with this form"""
    class Meta:
        model = RemittanceItem
        exclude = ('md5',)


