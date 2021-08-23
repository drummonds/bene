from django.conf.urls import url

from . import views

app_name = "sereports"
urlpatterns = [
    url(regex=r"^$", view=views.HomeView.as_view(), name="home"),
    url(regex=r"^customer$", view=views.CustomerView.as_view(), name="customers"),
    url(
        regex=r"^monthly-sales$",
        view=views.monthly_sales_graph,
        name="monthly_sales_graph",
    ),
    url(
        regex=r"^monthly-sales.svg$",
        view=views.monthly_sales_graph,
        name="monthly_sales_svg",
    ),
    url(regex=r"^remittance$", view=views.RemittanceView.as_view(), name="remittance"),
    url(regex=r"^add$", view=views.FileAddView.as_view(), name="filebaby-add"),
    # Special cases
    url(
        r"^query/Sales\sAnalysis\sby\sCustomer/$",
        views.SalesAnalysisByCustomerView.as_view(),
        {"report_name": "Sales Analysis by Customer"},
        name="sales_analysis_by_customer",
    ),
    # Generic cases
    url(
        regex=r"^query/(?P<report_name>.+)/$",
        view=views.QueryView.as_view(),
        name="query",
    ),
    #    # uploadering/urls.py
    #    url(r'^add$', views.FileAddView.as_view(), name='filebaby-add'),
]
