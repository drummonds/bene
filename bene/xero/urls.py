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
        name='authorize'
    ),
    url(
        regex=r'^$',
        view=views.OAuthView.as_view(),
        name='oauth'
    ),
    url(
        regex=r'^$',
        view=views.XeroView.as_view(),
        name='xero'
    ),
]

