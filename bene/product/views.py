import datetime
import pygal

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin

try:
    from django.urls import reverse, reverse_lazy
except ImportError:
    from django.core.urlresolvers import reverse, reverse_lazy
from django.views.generic import ListView
from django.http import HttpResponse

from .models import Product
from .tables import ProductSummaryTable


def current_datetime(request):
    now = datetime.datetime.now()
    html = "<html><body>Slumberfleece Products view <br>It is now %s.</body></html>" % now
    return HttpResponse(html)


class ProductView(LoginRequiredMixin, ListView):
    template_name = 'product/products.html'
    redirect_field_name = ''
    model = Product

    def get_context_data(self, **kwargs):
        context = super(ProductView, self).get_context_data(**kwargs)
        table = ProductSummaryTable(Product.objects.all())
        context.update({'version': settings.VERSION, 'table': table})
        return context


class HomeView(ProductView):
    pass


def product_sales_graph(request):
    bar_chart = pygal.StackedBar(show_legend=False, human_readable=True,
                                 # x_label_rotation=20,
                                 y_title='Product Sales (£,000)', height=200,
                                 width=800)  # Then create a bar graph object
    bar_chart.add('Sales', [10, 14, 15, 15])  # Add some values
    bar_chart.title = 'Product Sales'
    # bar_chart.x_labels = [months[int(row[0][-2:])-1] for row in res.data]
    return bar_chart.render_django_response()
