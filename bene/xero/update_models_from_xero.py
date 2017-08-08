from django.db import models
from django.utils import timezone

from .credit_note_caching import CreditNoteCache
from .xero_db_load import truncate_data, read_in, load_contact_group, load_contacts, load_items, load_invoices
from .xero_db_load import load_invoice_items
from .xero_db_load import invoices_all, invoice_lineitems_all, credit_notes_all  # Functions/iterators

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


