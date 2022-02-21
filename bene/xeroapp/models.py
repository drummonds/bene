from django.db import models
from django.utils import timezone


class ContactGroup(models.Model):
    xerodb_id = models.CharField(
        "Xero ID", blank=True, max_length=255, primary_key=True
    )  # store the guid
    name = models.CharField("Name of ContactGroup", blank=True, max_length=255)

    def __str__(self):
        return self.name

    # def get_absolute_url(self):
    #    return reverse('users:detail', kwargs={'username': self.username})


class Contact(models.Model):
    xerodb_id = models.CharField(
        "Xero ID", blank=True, max_length=255, primary_key=True
    )  # store the guid
    name = models.CharField("Name of Contact", blank=True, max_length=255)
    number = models.CharField("Account number", blank=True, max_length=50)
    first_name = models.CharField("Account number", blank=True, max_length=255)
    last_name = models.CharField("Account number", blank=True, max_length=255)
    email_address = models.CharField("Account number", blank=True, max_length=255)

    def __str__(self):
        return self.name


class Item(models.Model):
    xerodb_id = models.CharField(
        "Xero ID", blank=True, max_length=255, primary_key=True
    )  # store the guid
    code = models.CharField("Item Code", blank=True, max_length=255)
    name = models.CharField("Item Name", blank=True, max_length=255)
    cost_price = models.DecimalField(
        "Cost Price", max_digits=16, decimal_places=4
    )  # Could be part price
    sales_price = models.DecimalField(
        "Sales Price", max_digits=16, decimal_places=4
    )  # Could be part price

    def __str__(self):
        return self.name


class Invoice(models.Model):
    xerodb_id = models.CharField(
        "Xero ID", blank=True, max_length=255, primary_key=True
    )  # store the guid
    contact_id = models.ForeignKey(
        "Contact", on_delete=models.CASCADE, blank=True, null=True
    )
    currency_code = models.CharField("Currency Code", blank=True, max_length=3)
    currency_rate = models.DecimalField(
        "CurrencyRate", blank=True, default=0, max_digits=16, decimal_places=8
    )
    inv_number = models.CharField("Status", blank=True, max_length=50, default="")
    inv_date = models.DateTimeField("Date", default=timezone.now)
    nett = models.DecimalField("Nett", max_digits=16, decimal_places=2, default=0)
    gross = models.DecimalField("Gross", max_digits=16, decimal_places=2, default=0)
    tax = models.DecimalField("Tax", max_digits=16, decimal_places=2, default=0)
    status = models.CharField("Status", blank=True, max_length=255, default="")
    invoice_type = models.CharField(
        "Invoice Type", blank=True, max_length=255, default=""
    )
    updated_date_utc = models.DateTimeField("UpdatedDateUTC", default=timezone.now)
    due_date = models.DateTimeField(
        "DueDate", default=timezone.now, blank=True, null=True
    )
    expected_payment_date = models.DateTimeField(
        "ExpectedPaymentDate", default=timezone.now, blank=True, null=True
    )
    planned_payment_date = models.DateTimeField(
        "PlannedPaymentDate", default=timezone.now, blank=True, null=True
    )
    fully_paid_on_date = models.DateTimeField(
        "FullyPaidOnDate", default=timezone.now, blank=True, null=True
    )
    amount_due = models.DecimalField(
        "AmountDue", max_digits=16, decimal_places=2, default=0, blank=True, null=True
    )
    amount_paid = models.DecimalField(
        "AmountPaid", max_digits=16, decimal_places=2, default=0, blank=True, null=True
    )
    amount_credited = models.DecimalField(
        "AmountCredited",
        max_digits=16,
        decimal_places=2,
        default=0,
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.name


class LineItem(models.Model):
    id = models.UUIDField(primary_key=True)
    invoice = models.ForeignKey("Invoice", on_delete=models.CASCADE)
    item = models.ForeignKey("Item", on_delete=models.CASCADE, blank=True, null=True)
    quantity = models.DecimalField(
        "Qty", max_digits=16, decimal_places=4
    )  # Could be part price
    price = models.DecimalField(
        "Price", max_digits=16, decimal_places=4
    )  # Could be part price

    def __str__(self):
        return f"{self.quantity} of {self.item.name} for {self.price}"
