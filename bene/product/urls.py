from django.conf.urls import url

from . import views

app_name = 'product'
urlpatterns = [
    url(
        regex=r'^$',
        view=views.HomeView.as_view(),
        name='home'
    ),
    url(
        regex=r'^product$',
        view=views.ProductView.as_view(),
        name='products'
    ),
    url(
        regex=r'^product-sales$',
        view=views.product_sales_graph,
        name='product_sales'
    ),
    url(
        regex=r'^product-sales\.svg$',
        view=views.product_sales_graph,
        name='product_sales_svg'
    ),
]
