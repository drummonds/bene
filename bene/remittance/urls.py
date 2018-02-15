from django.conf.urls import url

from . import views


app_name = 'remittance'
urlpatterns = [
    url(
        regex=r'^$',
        view=views.HomeView.as_view(),
        name='home'
    ),
]
