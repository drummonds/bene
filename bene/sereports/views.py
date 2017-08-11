import datetime as dt
from django.conf import settings
from django.views.generic import DetailView, ListView, RedirectView, UpdateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Report, Company
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
        inv = Invoice.objects.latest('updated_date_utc')
        try:
            last_update = inv.updated_date_utc.strftime('%Y-%m-$d')
        except:
            last_update = ' waiting to implement latest update feature.'#'No DB update'
        context.update({'company': company_name, 'version': settings.VERSION, 'last_update': last_update})
        return context
