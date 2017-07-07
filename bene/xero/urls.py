from django.conf.urls import url

from . import views

urlpatterns = [
    url(
        regex=r'^$',
        view=views.SyncView.as_view(),
        name='index'
    ),
    url(
        regex=r'^$',
        view=views.AuthorizationView.as_view(),
        name='xero_authorize'
    ),
    url(
        regex=r'^$',
        view=views.XeroView.as_view(),
        name='xero'
    ),
]

