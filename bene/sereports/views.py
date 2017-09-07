import datetime as dt
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.core.urlresolvers import reverse_lazy
from django.views.generic import TemplateView, ListView, FormView
import hashlib
import urllib.request
import json
import requests

import django_tables2 as tables
from explorer.models import Query
from explorer.exporters import JSONExporter


from .forms import FilebabyForm, RemittanceForm
from .models import Report, Company
from .models import FilebabyFile, RemittanceFile
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
            last_update = inv.updated_date_utc.strftime('%Y-%m-%d %H:%M')
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


class RemittanceView(LoginRequiredMixin, FormView):
    form_class = RemittanceForm
    success_url = reverse_lazy('home')
    template_name = 'sereports/remittance.html'
    redirect_field_name = ''
    model = Report

    def get_context_data(self, **kwargs):
        context = super(RemittanceView, self).get_context_data(**kwargs)
        context.update({'company': company_name, 'version': settings.VERSION, 'last_update': last_update})
        return context

    def form_valid(self, form):
        form.save(commit=True)
        messages.success(self.request, 'Remmitance file uploaded!', fail_silently=True)
        return super(RemittanceView, self).form_valid(form)



# /uploadering/filebaby/views.py

class FileListView(ListView):

    model = FilebabyFile
    queryset = FilebabyFile.objects.order_by('-id')
    context_object_name = "files"
    template_name = "sereports/file_index.html"
    paginate_by = 5


class FileAddView(FormView):
    form_class = FilebabyForm
    success_url = reverse_lazy('home')
    template_name = "sereports/add.html"

    def form_valid(self, form):
        form.save(commit=True)
        messages.success(self.request, 'File uploaded!', fail_silently=True)
        return super(FileAddView, self).form_valid(form)


class FileAddHashedView(FormView):
    """This view hashes the file contents using md5"""

    form_class = FilebabyForm
    success_url = reverse_lazy('home')
    template_name = "sereports/add.html"

    def form_valid(self, form):
        print('Validating file upload form')
        hash_value = hashlib.md5(form.files.get('f').read()).hexdigest()
        # form.save returns a new FilebabyFile as instance
        instance = form.save(commit=False)
        instance.md5 = hash_value
        instance.save()
        messages.success(
            self.request, 'File hashed and uploaded!', fail_silently=True)
        print('Completed form')
        return super(FileAddHashedView, self).form_valid(form)

counter = 0

def generate(li_dict):
    #unique classname.
    global counter
    counter += 1
    table_classname = "MyTableClass%s" % (counter)

    class Meta:
        #ahhh... Bootstrap
        attrs = {"class": "table table-striped"}

    #generate a class dynamically
    cls = type(table_classname,(tables.Table,),dict(Meta=Meta))

    #grab the first dict's keys
    try:
        li = li_dict[0].keys()
    except IndexError:
        li = ['No Data']

    for colname in li:
        column = tables.Column(orderable=False)
        cls.base_columns[colname] = column

    return cls

class QueryView(LoginRequiredMixin, TemplateView):
    template_name = "sereports/query.html"

    def get_context_data(self, **kwargs):
        context = super(QueryView, self).get_context_data(**kwargs)
        try:
            report_name = self.kwargs['query_id']  # Indexed by name of report
            report = Report.objects.filter(name=report_name).first() # get the details of the report
            try:
                query_id = report.report_number
                query = Query.objects.get(pk=query_id)
                res = query.execute()
                header = res.header_strings
                data = [dict(zip(header, row)) for row in res.data]
            except:
                query = Query.objects.none()
                header = data = []
        except:
            report_name = 'Failed to get query_id'
        table_cls = generate(data)
        context.update({'report': report, 'report_name': report_name, 'query': table_cls(data), 'header': header})
        return context
