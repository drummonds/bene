from django.db import models
from django.utils import timezone

from .credit_note_caching import CreditNoteCache
from .xero_db_load import truncate_data, read_in, load_contact_group, load_contacts, load_items, load_invoices
from .xero_db_load import load_invoice_items
from .xero_db_load import invoices_all, invoice_lineitems_all, credit_notes_all  # Functions/iterators


class ContactGroup(models.Model):
    xerodb_id = models.CharField('Xero ID', blank=True, max_length=255, primary_key=True)  # store the guid
    name = models.CharField('Name of ContactGroup', blank=True, max_length=255)

    def __str__(self):
        return self.name

    #def get_absolute_url(self):
    #    return reverse('users:detail', kwargs={'username': self.username})

class Contact(models.Model):
    xerodb_id = models.CharField('Xero ID', blank=True, max_length=255, primary_key=True)  # store the guid
    name = models.CharField('Name of Contact', blank=True, max_length=255)
    number = models.CharField('Account number', blank=True, max_length=50)

    def __str__(self):
        return self.name


class Item(models.Model):
    xerodb_id = models.CharField('Xero ID', blank=True, max_length=255, primary_key=True)  # store the guid
    code = models.CharField('Item Code', blank=True, max_length=255)
    name = models.CharField('Item Name', blank=True, max_length=255)
    cost_price = models.DecimalField('Cost Price', max_digits=16, decimal_places=4)  # Could be part price
    sales_price = models.DecimalField('Sales Price', max_digits=16, decimal_places=4)  # Could be part price

    def __str__(self):
        return self.name


class Invoice(models.Model):
    xerodb_id = models.CharField('Xero ID', blank=True, max_length=255, primary_key=True)  # store the guid
    contact_id = models.ForeignKey('Contact', on_delete=models.CASCADE, blank=True, null=True)
    currency_code = models.CharField('Currency Code', blank=True, max_length=3)
    currency_rate = models.DecimalField('CurrencyRate', blank=True, default=0, max_digits=16, decimal_places=8)
    inv_number = models.CharField('Status', blank=True, max_length=50, default='')
    inv_date = models.DateTimeField('Date', default=timezone.now)
    nett = models.DecimalField('Nett', max_digits=16, decimal_places=2, default=0)
    gross = models.DecimalField('Gross', max_digits=16, decimal_places=2, default=0)
    tax = models.DecimalField('Tax', max_digits=16, decimal_places=2, default=0)
    status = models.CharField('Status', blank=True, max_length=255, default='')
    invoice_type = models.CharField('Invoice Type', blank=True, max_length=255, default='')
    updated_date_utc = models.DateTimeField('UpdatedDateUTC', default=timezone.now)

    def __str__(self):
        return self.name

class LineItem(models.Model):
    id = models.UUIDField(primary_key=True)
    invoice = models.ForeignKey('Invoice', on_delete=models.CASCADE)
    item = models.ForeignKey('Item', on_delete=models.CASCADE, blank=True, null=True)
    quantity  = models.DecimalField('Qty', max_digits=16, decimal_places=4)  # Could be part price
    price = models.DecimalField('Price', max_digits=16, decimal_places=4)  # Could be part price

    def __str__(self):
        return f'{self.quantity} of {self.item.name} for {self.price}'


def to_yaml(my_list, file_root):
    file_name = Path('.').child(file_root + dt.datetime.now().strftime(' %Y-%m-%d') + '.yml')
    with open(file_name, 'w') as f:
        f.write(yaml.dump(my_list))
    return file_name


def get_all(xero_endpoint, file_root='Xero_data'):
    print('Starting to get pages for {}'.format(file_root))
    records = records_page = xero_endpoint.filter(page=1)
    i = 2
    print('Page 1 ', end='')
    while len(records_page) == 100:
        if ((i-1) % 5) == 0:
            print('')  # End of line
        print(' {}'.format(i), end='')
        records_page = xero_endpoint.filter(page=i)
        records += records_page
        i += 1
    print('\n   Now saving file.')
    file_name = to_yaml(records, file_root)
    return records, file_name


def reload_data(xero):
    """Reloads all the data by downloading from Xero and updating the local copy database"""
    truncate_data()
    # Contact Groups
    groups, cg_file_name = get_all(xero.contactgroups, 'Xero_ContactGroups') # Saves to YAML file
    cg = read_in(cg_file_name)  # Convert from list to dataframe
    load_contact_group(cg)
    # Contacts
    contacts, ct_file_name = get_all(xero.contacts, 'Xero_Contacts')
    ct = read_in(ct_file_name)
    load_contacts(ct)
    # Items
    items, it_file_name  = get_all(xero.items, 'Xero_Items')
    it = read_in(it_file_name)
    load_items(it)
    # Invoices
    invoices, inv_file_name = get_all(xero.invoices, 'Xero_Invoices')
    inv = read_in(inv_file_name)
    load_invoices(df=inv, all=invoices_all)
    load_invoice_items(df=inv, all=invoice_lineitems_all, items=it)
    # Credit notes (overview)
    credit_notes, cn_file_name = get_all(xero.creditnotes, 'Xero_CreditNotes')
    cn = read_in(cn_file_name)
    # Credit notes cache
    ## Todo can now junk cache as credit notes gets invoice
    ## cnc = CreditNoteCache()
    ## cnc.update_cache(xero, fn)
    load_invoices(df=cn, all=credit_notes_all)


    #


