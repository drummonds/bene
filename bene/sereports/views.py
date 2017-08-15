import datetime as dt
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse_lazy
from django.views.generic import ListView, FormView
import hashlib

from .forms import FilebabyForm
from .models import Report, Company
from .models import FilebabyFile
from xeroapp.models import Invoice


class HomeView(LoginRequiredMixin, ListView):
    template_name = 'sereports/reports_list.html'
    redirect_field_name = ''
    model = Report

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        c = Company.objects.first()
        try:
            company_name = c.name
        except:
            company_name = 'No company set up yet'
        try:
            inv = Invoice.objects.latest('updated_date_utc')
            last_update = inv.updated_date_utc.strftime('%Y-%m-%d')
        except Invoice.DoesNotExist:
            last_update = 'No data so no DB update'
        context.update({'company': company_name, 'version': settings.VERSION, 'last_update': last_update})
        return context


class CustomerView(LoginRequiredMixin, ListView):
    template_name = 'sereports/customers.html'
    redirect_field_name = ''
    model = Report

    def get_context_data(self, **kwargs):
        context = super(CustomerView, self).get_context_data(**kwargs)
        return context

class RemittanceView(LoginRequiredMixin, ListView):
    template_name = 'sereports/remittance.html'
    redirect_field_name = ''
    model = Report

    def get_context_data(self, **kwargs):
        context = super(RemittanceView, self).get_context_data(**kwargs)
        return context


# /uploadering/filebaby/views.py

class FileListView(ListView):

    model = FilebabyFile
    queryset = FilebabyFile.objects.order_by('-id')
    context_object_name = "files"
    template_name = "filebaby/index.html"
    paginate_by = 5


class FileAddView(FormView):

    form_class = FilebabyForm
    success_url = reverse_lazy('home')
    template_name = "filebaby/add.html"
    #template_name = "filebaby/add-boring.html"

    def form_valid(self, form):
        form.save(commit=True)
        messages.success(self.request, 'File uploaded!', fail_silently=True)
        return super(FileAddView, self).form_valid(form)


class FileAddHashedView(FormView):
    """This view hashes the file contents using md5"""

    form_class = FilebabyForm
    success_url = reverse_lazy('home')
    template_name = "filebaby/add.html"

    def form_valid(self, form):
        hash_value = hashlib.md5(form.files.get('f').read()).hexdigest()
        # form.save returns a new FilebabyFile as instance
        instance = form.save(commit=False)
        instance.md5 = hash_value
        instance.save()
        messages.success(
            self.request, 'File hashed and uploaded!', fail_silently=True)
        return super(FileAddHashedView, self).form_valid(form)
