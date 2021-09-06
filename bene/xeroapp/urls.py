from django.conf.urls import url

from . import views

app_name = "xeroapp"
urlpatterns = [
    url(regex=r"^$", view=views.XHomeView.as_view(), name="index"),
    url(regex=r"^do-auth$", view=views.DoAuthView.as_view(), name="do_auth"),
    url(regex=r"^oauth$", view=views.OAuthView.as_view(), name="oauth"),
    url(regex=r"^xero$", view=views.TestXeroView.as_view(), name="xero"),
    url(regex=r"^db-update$", view=views.DBUpdateView.as_view(), name="dbupdate"),
]
