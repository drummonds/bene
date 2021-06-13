import datetime as dt
import json
import pandas as pd
from pathlib import Path
from time import sleep

from django.conf import settings
from django.core.files.storage import default_storage

from xero import Xero as PyXero
from xero.auth import PublicCredentials
from xero.exceptions import XeroException, XeroBadRequest

from .xero_db_load import truncate_data, load_contact_group, load_contact, load_item
from .xero_db_load import load_invoice, load_invoice_items
from .xero_db_load import (
    invoice_lineitems_all,
    credit_note_transform,
    credit_note_lineitems_all,
)  # Functions/iterators

MAX_API_CALLS = 12  # Per 15 second period


def get_all(get_method, file_root, dir_root, paged=True):
    """ Gets all the data from one endpoint with a rate limit to make sure the XERO
    API rate limit is not exceeded.
    The exact method of how you get records is passed in as a parameter so that the code is easy to test
    when you don't have an API
    get_method: Is a function that returns a list of records.
     It should have a named parameter page which gets paged data
    file_root:  This is passed in for debugging purposes."""
    print(f"Starting to get pages for {file_root}")
    for x in ["AWS_ACCESS_KEY_ID", "AWS_STORAGE_BUCKET_NAME", "MEDIA_ROOT", "MEDIA_URL"]:
        try:
            value = getattr(settings, x)
            print(f'{x:20} = {value}')
        except AttributeError:
            print(f'{x:20} Doesn''t exist')
    i = 1
    api_counter = MAX_API_CALLS
    start_time = dt.datetime.now()
    get_data = True
    while get_data:
        if ((i - 1) % 5) == 0:
            print("")  # End of line
        records_page = get_method.filter(page=i)
        if True:  #Write records to file in media_url
            filename = dt.datetime.now().strftime(f"XERO_DEBUG_%Y-%m-%dT%H-%M-%S_{file_root}_page_{i}.json")
            print(filename)
            extended_filename = Path(settings.MEDIA_ROOT) / filename
            try:
                with default_storage.open(f'{dir_root}/{filename}', 'w') as f:
                    f.write(records_page)
            except:
                print('Failed to write file to S3')
                print(f'Records_page = {records_page}')
        if paged:
            get_data = len(records_page) == 100
        else:
            get_data = False  # If not paged all data is returned in one go eg items or contactgroups
        print(f"Page {i} {file_root} with {len(records_page)} records", end="")
        for k, record in enumerate(records_page):
            if file_root == "Xero_Contacts" and ((i == 1) and (k < 5)):
                print(f" Record = {record}")
            yield (record)
        i += 1
        # Rate limiter functionality
        api_counter -= 1
        if api_counter <= 0:  # Max limit is 60 per minute
            api_counter = MAX_API_CALLS
            while (dt.datetime.now() - start_time).seconds < 15:
                sleep(5)
            start_time = dt.datetime.now()


def reload_data(xero_values):
    """Reloads all the data by downloading from Xero and updating the local copy database.
    This is done by iterating through each type of record."""
    # First convert stored xero values to credentials
    credentials = PublicCredentials(**xero_values)
    try:
        xero = PyXero(credentials)
    except XeroException as e:
        print(f"real_data failed to convert values to credentials: {xero_values}")
        print(f"TestXeroView Error {e.__class__}: {e.message}")
        return
    # Get rid of old data
    truncate_data()
    # Get a directory to store all the data
    dir_root =  dt.datetime.now().strftime(f"XERO_Get_All_%Y-%m-%dT%H-%M-%S")
    # Contact Groups
    print(f"RD update contact groups from Xero")
    for group in get_all(xero.contactgroups, "Xero_ContactGroups", dir_root, paged=False):
        load_contact_group(group)
    # Contacts
    print(f"RD update contacts from Xero")
    for contact in get_all(xero.contacts, "Xero_Contacts", dir_root):
        load_contact(contact)
    # Items / product catalogue
    # Store product catalogue as a cache item for entering line items
    print(f"RD update items from Xero (product catalogue)")
    item_catalogue = {}
    item_catalogue["Code"] = {}
    item_catalogue["Description"] = {}
    for i, item in enumerate(get_all(xero.items, "Xero_Items", dir_root, paged=False)):
        load_item(item)
        try:
            item_catalogue["Code"][item["Code"]] = item["ItemID"]
        except KeyError:
            pass  # Doesn't have a code
        try:
            item_catalogue["Description"][item["Description"]] = item["ItemID"]
        except KeyError:
            pass  # Doesn't have a description
    # Invoices
    print(f'Product catalogue = {item_catalogue}')
    print(f"RD update invoices from Xero")
    for i, invoice in enumerate(get_all(xero.invoices, "Xero_Invoices", dir_root)):
        if i < 3:
            print(f" invoice {i} = {invoice}")
        load_invoice(invoice, transform=None)
        if i < 3:
            print(f" invoice items start {i}")
        # The invoice includes all the invoice items
        load_invoice_items(
            invoice,
            invoice_transform=None,
            get_items=invoice_lineitems_all,
            item_catalogue=item_catalogue,
        )
    # Credit notes (overview)
    print(f"RD update credit notes from Xero")
    for credit_note in get_all(xero.creditnotes, "Xero_CreditNotes", dir_root):
        load_invoice(credit_note, transform=credit_note_transform)
        load_invoice_items(
            credit_note,
            invoice_transform=credit_note_transform,
            get_items=credit_note_lineitems_all,
            item_catalogue=item_catalogue,
        )
    print(f"RD ******** completed database update")
