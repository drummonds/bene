from django.db import models

# Create your models here.
class AccrualsTable(models.Model):
    expense_nc = models.CharField(
        verbose_name="Expense NC", max_length=4, blank=True, default=""
    )
    accruals_nc = models.CharField(verbose_name="Accruals NC", max_length=4)
    comment = models.CharField(verbose_name="Comment", max_length=255)
