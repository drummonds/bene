from django.contrib.auth.mixins import LoginRequiredMixin
import django_tables2 as tables

try:
    from django.urls import reverse, reverse_lazy
except ImportError:
    from django.core.urlresolvers import reverse, reverse_lazy
from django.views.generic import TemplateView

from .models import AccrualsTable


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "accruals/accruals_home.html"
    redirect_field_name = ""

    # model = Report TODO

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)

        context.update(
            {"test": "Hi from accruals", "accruals": AccrualsTable.objects.all()}
        )
        return context
