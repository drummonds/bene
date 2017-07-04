from django.shortcuts import render

from django.core.urlresolvers import reverse
from django.views.generic import DetailView, ListView, RedirectView, UpdateView, TemplateView

from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Report, Company
#from ..xero.models import Item# Company,

class HomeView(ListView):
    template_name = 'sereports/reports_list.html'
    model = Report

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        c = Company.objects.first()
        try:
            company_name = c.name
        except:
            company_name = 'No company set up yet'
        context.update({'company': company_name})
        return context
