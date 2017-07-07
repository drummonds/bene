from django.shortcuts import render

from django.core.urlresolvers import reverse
from django.views.generic import TemplateView

from django.contrib.auth.mixins import LoginRequiredMixin

class SyncView(TemplateView, LoginRequiredMixin):
    template_name = 'xero/sync.html'
