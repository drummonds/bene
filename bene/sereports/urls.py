from django.conf.urls import url

from . import views

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
        regex=r'^remittance$',
        view=views.RemittanceView.as_view(),
        name='remittance'
    ),
    url(
        regex=r'^add$',
        view=views.FileAddView.as_view(),
        name='filebaby-add'
    ),
#    # uploadering/urls.py
#    url(r'^add$', views.FileAddView.as_view(), name='filebaby-add'),
]
