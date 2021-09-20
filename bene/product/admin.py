from django.contrib import admin
from django.forms import TextInput, Textarea
from django.db import models

# Register your models here.

from .models import Product, Sku, Size, Spec, Material


class SkuInline(admin.StackedInline):
    model = Sku
    extra = 1


class SizeAdmin(admin.ModelAdmin):
    list_display = [
        "variant",
        "sage_size",
        "bed_size",
        "imperial_width",
        "imperial_length",
        "metric_width",
        "metric_length",
        "amazon",
        "description_long",
    ]


class ProductAdmin(admin.ModelAdmin):
    list_display = [
        "descriptive_content",
        "id",
        "product_type",
        "product_code_root",
        "bullet_point_1",
        "bullet_point_2",
        "bullet_point_3",
    ]
    inlines = [SkuInline]
    formfield_overrides = {
        models.CharField: {"widget": TextInput(attrs={"size": "100"})},
        models.TextField: {"widget": Textarea(attrs={"rows": 4, "cols": 40})},
    }

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "descriptive_content",
                    "product_type",
                    "product_code_root",
                    "material",
                    "ebay_material",
                    "ebay_features",
                    "ebay_type",
                    "bullet_point_1",
                    "bullet_point_2",
                    "bullet_point_3",
                    "bullet_point_4",
                    "bullet_point_5",
                )
            },
        ),
        (
            "Advanced options",
            {
                "classes": (
                    "wide",
                    "collapse",
                ),
                "fields": (
                    "manufacturer_description",
                    "factory_description",
                    "sage_description",
                    "sage_category",
                    "in_the_box",
                    "keywords",
                ),
            },
        ),
    )


class SpecAdmin(admin.ModelAdmin):
    list_display = ["quilting_pattern", "fixing"]


class MaterialAdmin(admin.ModelAdmin):
    list_display = ["description", "material", "thread_count", "weight"]


admin.site.register(Product, ProductAdmin)
admin.site.register(Size, SizeAdmin)
admin.site.register(Spec, SpecAdmin)
admin.site.register(Material, MaterialAdmin)
