from django.conf.urls import url

from . import views

urlpatterns = [
    url(
        regex=r'^$',
        view=views.HomeView.as_view(),
        name='index'
    ),
    url(
        regex=r'^do-auth$',
        view=views.DoAuthView.as_view(),
        name='do_auth'
    ),
    url(
        regex=r'^oauth$',
        view=views.OAuthView.as_view(),
        name='oauth'
    ),
    url(
        regex=r'^xero$',
        view=views.XeroView.as_view(),
        name='xero'
    ),
    # Rubbish below?
    url(
        regex=r'^authorize$',
        view=views.AuthorizationView.as_view(),
        name='authorize'
    ),
    url(
        regex=r'^ob_authorize$',
        view=views.OBAuthorizationView.as_view(),
        name='ob_authorize'
    ),
    url(
        regex=r'^ob_authorize$',
        view=views.OBAuthorizationView.as_view(),
        name='ob_authorize'
    ),
]

