from django.conf.urls import url

from . import views


app_name = 'remittance_doc'
urlpatterns = [
    url(
        regex=r'^$',
        view=views.HomeView.as_view(),
        name='home'
    ),
    url(
        regex=r'^add$',
        view=views.FileAddView.as_view(),
        name='remittance-file-add'
    ),
]
