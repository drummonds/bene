from django.db import models


class ContactGroup(models.Model):

    # First Name and Last Name do not cover name patterns
    # around the globe.
    xero_id = models.CharField('', blank=True, max_length=255)  # store the guid
    name = models.CharField('Name of ContactGroup', blank=True, max_length=255)

    def __str__(self):
        return self.name

    #def get_absolute_url(self):
    #    return reverse('users:detail', kwargs={'username': self.username})

class Contact(models.Model):

    # First Name and Last Name do not cover name patterns
    # around the globe.
    xero_id = models.CharField('', blank=True, max_length=255)  # store the guid
    name = models.CharField('Name of Contact', blank=True, max_length=255)
    number = models.CharField('Account number', blank=True, max_length=50)

    def __str__(self):
        return self.name


class Inventory(models.Model):

    # First Name and Last Name do not cover name patterns
    # around the globe.
    xero_id = models.CharField('', blank=True, max_length=255)  # store the guid
    code = models.CharField('Item Code', blank=True, max_length=255)
    name = models.CharField('Item Name', blank=True, max_length=255)
    cost_price = models.DecimalField('Cost Price', max_digits=16, decimal_places=4)  # Could be part price
    sales_price = models.DecimalField('Cost Price', max_digits=16, decimal_places=4)  # Could be part price

    def __str__(self):
        return self.name

    #def get_absolute_url(self):
    #    return reverse('users:detail', kwargs={'username': self.username})


class Invoice(models.Model):

    # First Name and Last Name do not cover name patterns
    # around the globe.
    xero_id = models.CharField('', blank=True, max_length=255)  # store the guid
    code = models.CharField('Item Code', blank=True, max_length=255)
    name = models.CharField('Item Name', blank=True, max_length=255)
    cost_price = models.DecimalField('Cost Price', max_digits=16, decimal_places=4)  # Could be part price
    sales_price = models.DecimalField('Cost Price', max_digits=16, decimal_places=4)  # Could be part price

    def __str__(self):
        return self.name

