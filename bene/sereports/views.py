import datetime as dt
from django.conf import settings
from django.views.generic import DetailView, ListView, RedirectView, UpdateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Report, Company
from xeroapp.models import Invoice

view = views.CustomerView.as_view(),


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
            last_update = inv.updated_date_utc.strftime('%Y-%m-$d')
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
