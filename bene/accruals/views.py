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
from django.shortcuts import render
from django.views.generic import TemplateView, ListView, FormView, View
import hashlib
import json
import requests
import pygal
import urllib.request


# Create your views here.
class HomeView(LoginRequiredMixin, ListView):
    template_name = 'accruals/accruals_home.html'
    redirect_field_name = ''

    # model = Report TODO

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        accruals = [
            {'Expense NC': '--', 'Accrual NC': 2110, 'Comment': 'debit notes'},
            {'Expense NC': '--', 'Accrual NC': 2160, 'Comment': 'Matched debit notes'},
            {'Expense NC': '7100', 'Accrual NC': 2111, 'Comment': 'Gas and Electricity for Factory'},
        ]

        context.update({'test': 'Hi from accruals',
                        'accruals': accruals
                        })
        return context
