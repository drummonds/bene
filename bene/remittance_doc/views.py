from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.storage import default_storage
from django.urls import reverse_lazy
from django.views.generic import ListView, FormView

import django_tables2 as tables

# Create your views here.
from .models import RemittanceItem
from .forms import RemittanceFileForm

class ListTable(tables.Table):
    """Format for a single column table to be used for converting lists to html tables"""
    name = tables.Column()


class HomeView(LoginRequiredMixin, ListView):
    template_name = 'remittance/remittance_home.html'
    model = RemittanceItem

    def get_queryset(self):
        results = ['List of items from storage']
        results.append(f" Storage exists = {default_storage.exists('storage_test')}")
        dirs, files = default_storage.listdir('')
        results = results + ['**Dirs**'] + dirs  + ['**Files**'] + files
        return ListTable([{'name': x} for x in results])  # Convert list to a dictionary

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)

        context.update({'test': 'Hi from accruals',
                        'bucket_name': settings.AWS_STORAGE_BUCKET_NAME,
                        'AWS_ID': settings.AWS_ACCESS_KEY_ID,
                        'remittances': RemittanceItem.objects.all(),
                        })
        return context


class FileAddView(FormView):
    form_class = RemittanceFileForm
    success_url = reverse_lazy('remittance_doc:home')
    template_name = "remittance/remittance_add.html"

    def post(self, request, *args, **kwargs):
        return super(FileAddView, self).post(request, *args, **kwargs)

    def form_invalid(self, form, **kwargs):
        return super(FileAddView, self).form_invalid(form, **kwargs)

    def form_valid(self, form):
        form.save(commit=True)
        messages.success(self.request, 'File uploaded!', fail_silently=True)
        return super(FileAddView, self).form_valid(form)
