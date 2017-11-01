import datetime as dt
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.urls import reverse
from django.core.urlresolvers import reverse_lazy
from django.views.generic import TemplateView, ListView, FormView
import hashlib
import urllib.request
import json
import requests
import pygal

import django_tables2 as tables
from explorer.models import Query
from explorer.exporters import JSONExporter


from .forms import FilebabyForm, RemittanceForm
from .models import Report, Company
from .models import FilebabyFile, RemittanceFile
from utils.table_formatters import generate
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
        try:
            query = Query.objects.get(pk=24) # Todo need to add paremeters
            # query.params = report.dict_parameters
            res = query.execute()
            header = res.header_strings
            data = [dict(zip(header, row)) for row in res.data]
        except:
            query = Query.objects.none()
            header = data = []
        table_cls = generate(data)
        # Generate graph
        file_name = '/tmp/customer/graph.svg'
        try:
            bar_chart = pygal.Bar()  # Then create a bar graph object
            bar_chart.add('Sales', [row[1] for row in res.data])  # Add some values
            bar_chart.render_to_file(file_name)
        except:
            pass
        context.update({'version': settings.VERSION, 'query': table_cls(data), 'header': header})
        return context


def customer_graph(request):
    # do whatever you have to do with your view
    # customize and prepare your chart
    bar_chart = pygal.Bar()  # Then create a bar graph object
    # bar_chart.add('Fibonacci', [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55])  # Add some values
    query = Query.objects.get(pk=24)  # Todo need to add paremeters
    # query.params = report.dict_parameters
    res = query.execute()
    bar_chart.add('Sales', [row[1] for row in res.data])  # Add some values
    # bar_chart.render_to_file('bar_chart.svg')
    return bar_chart.render_django_response()

    # # Generate graph
    # file_name = '/tmp/customer/graph.svg'
    # try:
    #     bar_chart = pygal.Bar()  # Then create a bar graph object
    #     bar_chart.add('Sales', [row[1] for row in res.data])  # Add some values
    #     bar_chart.render_to_file(file_name)
    # except:
    #     pass


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


class QueryView(LoginRequiredMixin, TemplateView):
    template_name = "sereports/query.html"

    def get_context_data(self, **kwargs):
        context = super(QueryView, self).get_context_data(**kwargs)
        try:
            report_name = self.kwargs['query_id']  # Indexed by name of report
            report = Report.objects.filter(name=report_name).first() # get the details of the report
            try:
                query_id = report.report_number
                query = Query.objects.get(pk=query_id) # Todo need to add paremeters
                query.params = report.dict_parameters
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
