from django.db import models


class ContactGroup(models.Model):
    xeroId = models.CharField('Xero ID', blank=True, max_length=255, primary_key=True)  # store the guid
    name = models.CharField('Name of ContactGroup', blank=True, max_length=255)

    def __str__(self):
        return self.name

    #def get_absolute_url(self):
    #    return reverse('users:detail', kwargs={'username': self.username})

class Contact(models.Model):
    xeroId = models.CharField('Xero ID', blank=True, max_length=255, primary_key=True)  # store the guid
    name = models.CharField('Name of Contact', blank=True, max_length=255)
    number = models.CharField('Account number', blank=True, max_length=50)

    def __str__(self):
        return self.name


class Item(models.Model):
    xeroId = models.CharField('Xero ID', blank=True, max_length=255, primary_key=True)  # store the guid
    code = models.CharField('Item Code', blank=True, max_length=255)
    name = models.CharField('Item Name', blank=True, max_length=255)
    cost_price = models.DecimalField('Cost Price', max_digits=16, decimal_places=4)  # Could be part price
    sales_price = models.DecimalField('Sales Price', max_digits=16, decimal_places=4)  # Could be part price

    def __str__(self):
        return self.name


class Invoice(models.Model):
    xeroId = models.CharField('Xero ID', blank=True, max_length=255, primary_key=True)  # store the guid
    contact_id = models.ForeignKey('Contact', on_delete=models.CASCADE)
    code = models.CharField('Item Code', blank=True, max_length=255)
    name = models.CharField('Item Name', blank=True, max_length=255)
    cost_price = models.DecimalField('Cost Price', max_digits=16, decimal_places=4)  # Could be part price
    sales_price = models.DecimalField('Cost Price', max_digits=16, decimal_places=4)  # Could be part price

    def __str__(self):
        return self.name

class LineItem(models.Model):
    id = models.UUIDField(primary_key=True)
    invoice = models.ForeignKey('Invoice', on_delete=models.CASCADE)
    item = models.ForeignKey('Item', on_delete=models.CASCADE)
    quantity  = models.DecimalField('Qty', max_digits=16, decimal_places=4)  # Could be part price
    price = models.DecimalField('Price', max_digits=16, decimal_places=4)  # Could be part price

    def __str__(self):
        return f'{self.quantity} of {self.item.name} for {self.price}'

