import datetime as dt
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import DatabaseError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

try:
    from django.urls import reverse, reverse_lazy
except ImportError:
    from django.core.urlresolvers import reverse, reverse_lazy
from django.views.generic import TemplateView, ListView, FormView, View
import hashlib
import json
import requests
import pygal
import urllib.request

import django_tables2 as tables
from explorer.models import Query
from explorer.exporters import JSONExporter


from .forms import FilebabyForm, RemittanceForm, QueryReportForm
from .models import Report, Company
from .models import FilebabyFile, RemittanceFile
from utils.table_formatters import generate
from xeroapp.models import Invoice


class HomeView(LoginRequiredMixin, ListView):
    template_name = "sereports/reports_list.html"
    redirect_field_name = ""
    model = Report

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        c = Company.objects.first()
        try:
            company_name = c.name
        except:
            company_name = "No company set up yet"
        try:
            inv = Invoice.objects.latest("updated_date_utc")
            last_update = inv.updated_date_utc.strftime("%Y-%m-%d %H:%M")
        except Invoice.DoesNotExist:
            last_update = "No data so no DB update"
        context.update(
            {
                "company": company_name,
                "version": settings.VERSION,
                "last_update": last_update,
            }
        )
        return context


class CustomerView(LoginRequiredMixin, ListView):
    template_name = "sereports/customers.html"
    redirect_field_name = ""
    model = Report

    def get_context_data(self, **kwargs):
        context = super(CustomerView, self).get_context_data(**kwargs)
        try:
            query = Query.objects.get(pk=24)  # Todo need to add paremeters
            # query.params = report.dict_parameters
            res = query.execute()
            header = res.header_strings
            data = [dict(zip(header, row)) for row in res.data]
        except:
            query = Query.objects.none()
            header = data = []
        table_cls = generate(data)
        # Generate graph
        file_name = "/tmp/customer/graph.svg"
        try:
            bar_chart = pygal.StackedBar()  # Then create a bar graph object
            bar_chart.add("Sales", [row[1] for row in res.data])  # Add some values
            bar_chart.add("O/S", [row[1] * 0.2 for row in res.data])  # Add some values
            bar_chart.render_to_file(file_name)
        except:
            pass
        context.update(
            {"version": settings.VERSION, "query": table_cls(data), "header": header}
        )
        return context


def monthly_sales_graph(request):
    # do whatever you have to do with your view
    # customize and prepare your chart
    bar_chart = pygal.StackedBar(
        show_legend=False,
        human_readable=True,
        # x_label_rotation=20,
        y_title="Sales (£,000)",
        height=200,
        width=800,
    )  # Then create a bar graph object
    query = Query.objects.get(pk=24)  # Todo need to add parameters
    # query.params = report.dict_parameters
    res = query.execute()  # Returns ?
    bar_chart.title = "Monthly Sales"
    months = "JFMAMJJASOND"
    bar_chart.x_labels = [months[int(row[0][-2:]) - 1] for row in res.data]
    bar_chart.add(
        "Sales 15",
        [row[1] / 1000 if row[0].find("2015") != -1 else 0 for row in res.data],
    )  # Add some values
    bar_chart.add(
        "Sales 16",
        [row[1] / 1000 if row[0].find("2016") != -1 else 0 for row in res.data],
    )  # Add some values
    bar_chart.add(
        "Sales 17",
        [row[1] / 1000 if row[0].find("2017") != -1 else 0 for row in res.data],
    )  # Add some values
    bar_chart.add(
        "Sales 18",
        [row[1] / 1000 if row[0].find("2018") != -1 else 0 for row in res.data],
    )  # Add some values
    bar_chart.add(
        "Sales 19",
        [row[1] / 1000 if row[0].find("2019") != -1 else 0 for row in res.data],
    )  # Add some values
    return bar_chart.render_django_response()


class RemittanceView(LoginRequiredMixin, FormView):
    form_class = RemittanceForm
    success_url = reverse_lazy("home")
    template_name = "sereports/remittance.html"
    redirect_field_name = ""
    model = Report

    def get_context_data(self, **kwargs):
        context = super(RemittanceView, self).get_context_data(**kwargs)
        context.update(
            {
                "company": company_name,
                "version": settings.VERSION,
                "last_update": last_update,
            }
        )
        return context

    def form_valid(self, form):
        form.save(commit=True)
        messages.success(self.request, "Remmitance file uploaded!", fail_silently=True)
        return super(RemittanceView, self).form_valid(form)


# /uploadering/filebaby/views.py


class FileListView(ListView):

    model = FilebabyFile
    queryset = FilebabyFile.objects.order_by("-id")
    context_object_name = "files"
    template_name = "sereports/file_index.html"
    paginate_by = 5


class FileAddView(FormView):
    form_class = FilebabyForm
    success_url = reverse_lazy("home")
    template_name = "sereports/add.html"

    def form_valid(self, form):
        form.save(commit=True)
        messages.success(self.request, "File uploaded!", fail_silently=True)
        return super(FileAddView, self).form_valid(form)


class FileAddHashedView(FormView):
    """This view hashes the file contents using md5"""

    form_class = FilebabyForm
    success_url = reverse_lazy("home")
    template_name = "sereports/add.html"

    def form_valid(self, form):
        print("Validating file upload form")
        hash_value = hashlib.md5(form.files.get("f").read()).hexdigest()
        # form.save returns a new FilebabyFile as instance
        instance = form.save(commit=False)
        instance.md5 = hash_value
        instance.save()
        messages.success(self.request, "File hashed and uploaded!", fail_silently=True)
        print("Completed form")
        return super(FileAddHashedView, self).form_valid(form)


class QueryView(LoginRequiredMixin, TemplateView):
    template_name = "sereports/query.html"

    def get_context_data(self, **kwargs):
        context = super(QueryView, self).get_context_data(**kwargs)
        try:
            report_name = self.kwargs["report_name"]  # Indexed by name of report
            report = Report.objects.filter(
                name=report_name
            ).first()  # get the details of the report
            try:
                query_id = report.report_number
                query = Query.objects.get(pk=query_id)  # Todo need to add paremeters
                query.params = report.dict_parameters
                res = query.execute()
                header = res.header_strings
                data = [dict(zip(header, row)) for row in res.data]
            except:
                query = Query.objects.none()
                header = data = []
        except:
            report_name = "Failed to convert report_name to query_id"
        table_cls = generate(data)
        context.update(
            {
                "report": report,
                "report_name": report_name,
                "date_now": dt.datetime.now(),
                "query": table_cls(data),
                "header": header,
            }
        )
        return context


def get_params_from_request(request):
    val = request.GET.get("params", None)
    try:
        d = {}
        tuples = val.split("|")
        for t in tuples:
            res = t.split(":")
            d[res[0]] = res[1]
        return d
    except Exception:
        return None


from explorer.utils import (
    url_get_show,
    url_get_rows,
    url_get_fullscreen,
    url_get_params,
)


class ReportContextMixin(object):
    def gen_ctx(self):
        # Todo add flexible pemissions
        # return {'can_view': app_settings.EXPLORER_PERMISSION_VIEW(self.request.user),
        #        'can_change': app_settings.EXPLORER_PERMISSION_CHANGE(self.request.user)}
        #
        return {"can_view": True, "can_change": False}

    def get_context_data(self, **kwargs):
        ctx = super(ReportContextMixin, self).get_context_data(**kwargs)
        ctx.update(self.gen_ctx())
        return ctx

    def render_template(self, template, ctx):
        ctx.update(self.gen_ctx())
        return render(self.request, template, ctx)


class SalesAnalysisByCustomerView(LoginRequiredMixin, ReportContextMixin, TemplateView):
    template_name = "sereports/sa_by_cust.html"
    form_class = QueryReportForm

    def get(self, request, report_name):
        query, form, query_id = SalesAnalysisByCustomerView.get_instance_and_form(
            request, report_name
        )
        query.save()  # updates the modified date
        show = url_get_show(request)
        vm = report_viewmodel(
            request.user,
            query,
            form=form,
            run_query=show,
            name=report_name,
            report_number=query_id,
        )
        fullscreen = url_get_fullscreen(request)
        return self.render_template(self.template_name, vm)

    def post(self, request, report_name):
        # todo Integrate permissions
        # if not app_settings.EXPLORER_PERMISSION_CHANGE(request.user):
        #    return HttpResponseRedirect(
        #        reverse_lazy('query_detail', kwargs={'query_id': query_id})
        #    )
        show = url_get_show(request)
        query, form, query_id = SalesAnalysisByCustomerView.get_instance_and_form(
            request, report_name
        )
        success = form.is_valid() and form.save()
        vm = report_viewmodel(
            request.user,
            query,
            form=form,
            run_query=show,
            message="Query saved." if success else None,
            name=report_name,
            report_number=query_id,
        )
        return self.render_template(self.template_name, vm)

    def get_context_data(self, **kwargs):
        context = super(SalesAnalysisByCustomerView, self).get_context_data(**kwargs)
        try:
            report_name = self.kwargs["query_id"]  # Indexed by name of report
            report = Report.objects.filter(
                name=report_name
            ).first()  # get the details of the report
            try:
                query_id = report.report_number
                query = Query.objects.get(pk=query_id)
                # default parameters
                query.params = (
                    report.dict_parameters
                )  # taking parameters from hard coded
                # TODO these should be the default parameters rather than the curent ones
                res = query.execute()
                header = res.header_strings
                data = [dict(zip(header, row)) for row in res.data]
            except:
                query = Query.objects.none()
                header = data = []
            params = {
                "StartDate": "2017-02-01",
                "EndDate": "2018-01-31",
            }  # Todo connect to actual parameters
        except:
            report_name = "Failed to get query_id"
        table_cls = generate(data)
        context.update(
            {
                "report": report,
                "report_name": report_name,
                "query": table_cls(data),
                "header": header,
                "params": params,
            }
        )
        return context

    @staticmethod
    def get_instance_and_form(request, report_name):
        report = Report.objects.filter(
            name=report_name
        ).first()  # get the details of the report
        try:
            query_id = report.report_number
            query = get_object_or_404(Query, pk=query_id)
            query.params = url_get_params(request)
            # query.params = report.dict_parameters TODO addd default parameters
            res = query.execute()
            header = res.header_strings
            data = [dict(zip(header, row)) for row in res.data]
        except:
            query = Query.objects.none()
            header = data = []
        query = get_object_or_404(Query, pk=query_id)
        query.params = get_params_from_request(request)
        form = QueryReportForm(
            request.POST if len(request.POST) else None, instance=query
        )
        return query, form, query_id


def report_viewmodel(
    user,
    query,
    title=None,
    form=None,
    message=None,
    run_query=True,
    error=None,
    name="This Report",
    report_number=0,
):
    """Report convert query to parameters for template"""
    try:
        res = query.execute()
        header = res.header_strings
        data = [dict(zip(header, row)) for row in res.data]
    except:
        header = data = []
    table_cls = generate(data)
    # SQL Explorer
    res = None
    ql = None
    if run_query:
        try:
            res, ql = query.execute_with_logging(user)
        except DatabaseError as e:
            error = str(e)
    has_valid_results = not error and res and run_query
    ret = {
        "params": query.available_params(),
        "title": title,
        "shared": query.shared,
        "query": query,
        "form": form,
        "message": message,
        "error": error,
        "headers": res.headers if has_valid_results else None,
        "total_rows": len(res.data) if has_valid_results else None,
        "duration": res.duration if has_valid_results else None,
        "has_stats": len([h for h in res.headers if h.summary])
        if has_valid_results
        else False,
        "snapshots": query.snapshots if query.snapshot else [],
        "ql_id": ql.id if ql else None,
        # Report specific monitoring
        "report_name": name,
        "report_number": report_number,
        "report_data": table_cls(data),
        "header": header,
    }
    return ret
