import django_tables2 as tables

from .models import Product


class ProductSummaryTable(tables.Table):
    class Meta:
        model = Product
        fields = ['id', 'product_code_root', 'descriptive_content']
