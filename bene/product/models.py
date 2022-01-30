from django.db import models


class Product(models.Model):
    descriptive_content = models.CharField(max_length=200)
    factory_description = models.CharField(max_length=200, blank=True)
    sage_description = models.CharField(max_length=200, blank=True)
    sage_category = models.IntegerField(null=True)
    material = models.CharField(max_length=100, blank=True)
    ebay_material = models.CharField(max_length=100, blank=True)
    ebay_features = models.CharField(max_length=255, blank=True)
    ebay_type = models.CharField(max_length=100, blank=True)
    keywords = models.CharField(
        max_length=100, default="matress;matrass;mattrass", blank=True
    )
    bullet_point_1 = models.CharField(max_length=135, blank=True, default="Point 1")
    bullet_point_2 = models.CharField(max_length=135, blank=True, default="Point 1")
    bullet_point_3 = models.CharField(max_length=135, blank=True, default="Point 1")
    bullet_point_4 = models.CharField(max_length=135, blank=True, default="Point 1")
    bullet_point_5 = models.CharField(max_length=135, blank=True, default="Point 1")
    manufacturer_description = models.TextField(
        max_length=2000, blank=True, default="Manuf desc"
    )
    in_the_box = models.CharField(max_length=135, blank=True, default="1 Single")
    url = models.URLField(blank=True, default="")
    TOPPER = "TPR"
    MATTRESS_PROTECTOR = "MP"
    PRODUCT_CHOICES = (
        (TOPPER, "Topper"),
        (MATTRESS_PROTECTOR, "Mattress Protector"),
    )
    product_type = models.CharField(
        max_length=3, choices=PRODUCT_CHOICES, default=MATTRESS_PROTECTOR
    )
    product_code_root = models.CharField(max_length=16, blank=True, default="")


class Size(models.Model):
    variant = models.CharField(max_length=3, primary_key=True)
    sage_size = models.CharField(max_length=4)
    bed_size = models.CharField(max_length=100)
    imperial_width = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Width of product in inches",
    )
    imperial_length = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Length of product in inches",
    )
    metric_width = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Width of product in cm",
    )
    metric_length = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Length of product in cm",
    )
    amazon = models.CharField(max_length=100, blank=True)
    ebay = models.CharField(max_length=100, blank=True)
    description_long = models.CharField(max_length=100)
    comment = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.description_long


class Material(models.Model):
    description = models.CharField(max_length=250, blank=True)
    material = models.CharField(max_length=135, blank=True)
    thread_count = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, help_text="thread count per inch"
    )
    weight = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, help_text="grams per square meter"
    )
    coating = models.CharField(
        max_length=135, blank=True, help_text="Description of any coating applied"
    )

    def __str__(self):
        return self.description


class Sku(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(Size, on_delete=models.SET_DEFAULT, default="UNK")
    colour = models.CharField(max_length=30, blank=True)
    factory_sku_description = models.CharField(max_length=200, blank=True)
    url = models.URLField(blank=True)
    vendor_product_id = models.CharField(max_length=30, blank=True)
    barcode = models.CharField(max_length=100, unique=True, blank=True)
    asin = models.CharField(max_length=100, blank=True)
    slf_cost_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    rrp = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    length = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    width = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    height = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    weight = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    qty_per_box = models.IntegerField(
        null=True,
        blank=True,
        help_text="This is the number in a standard shipping container box at the factory",
    )
    keywords = models.CharField(max_length=100, blank=True)
    launch_date = models.DateField(blank=True)
    release_date = models.DateField(blank=True)
    bullet_point_1 = models.CharField(max_length=135, blank=True)
    bullet_point_2 = models.CharField(max_length=135, blank=True)
    bullet_point_3 = models.CharField(max_length=135, blank=True)
    bullet_point_4 = models.CharField(max_length=135, blank=True)
    bullet_point_5 = models.CharField(max_length=135, blank=True)
    in_the_box = models.CharField(max_length=135, blank=True)


class Spec(models.Model):
    UNKNOWN_QUILTING_PATTERN = "UNKNOWN"
    DIAMOND_3_INCH = 'DIA 3"'
    SQUARE_2_INCH = 'SQU 2"'
    STRIGHT_6_INCH = 'STR 6"'
    QUILTING_PATTERN = (
        (
            UNKNOWN_QUILTING_PATTERN,
            "Unkown",
        ),
        (
            DIAMOND_3_INCH,
            '3" Diamond',
        ),
        (
            SQUARE_2_INCH,
            '2" Square',
        ),
        (
            STRIGHT_6_INCH,
            '6" Straight',
        ),
    )
    quilting_pattern = models.CharField(
        max_length=10, choices=QUILTING_PATTERN, default=UNKNOWN_QUILTING_PATTERN
    )
    ELASTIC_STRAP = "ELASTIC"
    SKIRT = "SKIRT"
    FIXING_CHOICES = (
        (ELASTIC_STRAP, "Elastic strip"),
        (
            SKIRT,
            "Elasticed skirt",
        ),
    )
    fixing = models.CharField(
        max_length=10, choices=FIXING_CHOICES, default=ELASTIC_STRAP
    )
    POLYCOTTON = "PolyCotton"
    EGYPTIAN_COTTON = "Egyptian Cotton"
    TEXTILE_MATERIAL = (
        (
            UNKNOWN_QUILTING_PATTERN,
            "Unkown",
        ),
        (
            DIAMOND_3_INCH,
            '3" Diamond',
        ),
        (
            SQUARE_2_INCH,
            '2" Square',
        ),
        (
            STRIGHT_6_INCH,
            '6" Straight',
        ),
    )
    top = models.ForeignKey(Material, on_delete=models.CASCADE, related_name="top")
    bottom = models.ForeignKey(
        Material, on_delete=models.CASCADE, related_name="bottom"
    )
    filling = models.CharField(
        max_length=135, blank=True, help_text="Type of filling , hollow fibre"
    )
    filling_weight = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, help_text="grams per square meter"
    )
