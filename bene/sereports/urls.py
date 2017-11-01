from django.conf.urls import url

from . import views

app_name = 'reports'
urlpatterns = [
    url(
        regex=r'^$',
        view=views.HomeView.as_view(),
        name='home'
    ),
    url(
        regex=r'^customer$',
        view=views.CustomerView.as_view(),
        name='customers'
    ),
    url(
        regex=r'^customer-graph$',
        view=views.customer_graph,
        name='customers_graph'
    ),
    url(
        regex=r'^customer-graph.svg$',
        view=views.customer_graph,
        name='customers_graph'
    ),
    url(
        regex=r'^remittance$',
        view=views.RemittanceView.as_view(),
        name='remittance'
    ),
    url(
        regex=r'^add$',
        view=views.FileAddView.as_view(),
        name='filebaby-add'
    ),
    url(
        regex=r'^query/(?P<query_id>.+)/$',
        view=views.QueryView.as_view(),
        name='query'
    ),
    #    # uploadering/urls.py
#    url(r'^add$', views.FileAddView.as_view(), name='filebaby-add'),
]
