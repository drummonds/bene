import datetime as dt
from functools import wraps
from numpy import isnan
import pandas as pd
from unipath import Path
import uuid
import yaml

from django.db import connection, IntegrityError


# from luca import p

# ***************************
# Utilities
# ***************************


def read_in(file_name):
    """Reads in a YML file which is extracted from Xero and converts it into a dataframe.  Note often
    the fields contain nested master slave relationships."""
    with open(file_name, "r") as f:
        result = yaml.safe_load(f.read())
    return pd.DataFrame(result)


def truncate_data():
    """Currently have to truncate all data in order to upload new variants."""
    with connection.cursor() as cursor:
        # Data is interconnected with foreign keys so have to get rid of it all
        cursor.execute(
            "TRUNCATE xeroapp_ContactGroup, xeroapp_Contact, xeroapp_Invoice, xeroapp_LineItem, xeroapp_Item"
        )


# Wrapper for SQL execute that has error handling


class SQLExecute:
    def __init__(self, num_failures_to_report=3):
        self.cursor = connection.cursor()
        self.first_failures = num_failures_to_report

    def __enter__(self):
        self.cursor.__enter__()
        return self

    def __exit__(self, *exc_info):
        self.cursor.__exit__(*exc_info)

    def execute(self, sql, params=None):
        try:
            if params:
                self.cursor.execute(sql, params)
            else:
                self.cursor.execute(sql)
        except Exception as e:
            if self.first_failures > 0:
                print("# ~~~ Loading invoices failed")
                print(f"sql = {sql}")
                if params:
                    print(f"params = {params}")
                else:
                    print("No params")
                print(e)
                self.first_failures -= 1


# ***************************
# Contact groups
# ***************************


def contact_groups(cg):
    for row in cg.iterrows():
        yield row[1]["Name"], row[1]["ContactGroupID"]


def load_contact_group(df):
    with SQLExecute() as cursor:
        cursor.execute("TRUNCATE xeroapp_ContactGroup")
        i = 0
        for n, id in contact_groups(df):
            sql = f"""INSERT INTO xeroapp_ContactGroup ("xerodb_id", name) VALUES('{id}', '{n}')"""
            cursor.execute(sql)
            i += 1


# ***************************
# Contacts
# ***************************


def contacts_all(c):
    for row in c.iterrows():
        first_name = default_get(row, None, "FirstName")
        last_name = default_get(row, None, "LastName")
        email_address = default_get(row, None, "EmailAddress")
        yield row[1]["ContactID"], row[1]["Name"], row[1][
            "AccountNumber"
        ], first_name, last_name, email_address


def load_contacts(df):
    with SQLExecute() as cursor:
        i = 0
        for id, name, number, first_name, last_name, email_address in contacts_all(df):
            try:
                if isnan(number):
                    number = ""
            except:
                pass
            sql = f"""
INSERT INTO xeroapp_Contact 
("xerodb_id", name, number,
first_name, last_name, email_address 
) 
VALUES(%(id)s, %(name)s, %(number)s,
%(first_name)s, %(last_name)s, %(email_address)s
)"""
            params = {
                "id": id,
                "name": name,
                "number": number,
                "first_name": first_name,
                "last_name": last_name,
                "email_address": email_address,
            }
            cursor.execute(sql, params)
            i += 1


# ***************************
# Inventory items
# ***************************


def items_all(df):
    for row in df.iterrows():
        try:
            cost_price = row[1]["PurchaseDetails"]["UnitPrice"]
        except:  # eg if missing
            cost_price = 0.0
        try:
            sales_price = row[1]["SalesDetails"]["UnitPrice"]
        except:  # eg if missing
            sales_price = 0.0
        yield row[1]["ItemID"], row[1]["Code"], row[1][
            "Description"
        ], cost_price, sales_price


def load_items(df):
    with SQLExecute() as cursor:
        i = 0
        num = len(df)
        marked_complete = 0
        for id, code, name, cost_price, sales_price in items_all(df):
            sql = f"""INSERT INTO xeroapp_Item ("xerodb_id",code, name, cost_price, sales_price)
            VALUES(%(id)s, %(code)s, %(name)s, %(cost_price)s, %(sales_price)s)"""
            params = {
                "id": id,
                "code": code,
                "name": name,
                "cost_price": cost_price,
                "sales_price": sales_price,
            }
            cursor.execute(sql, params)
            i += 1
            pc = int(10.0 * (i / num))  # percent complete
            if pc > marked_complete:
                print(f"Load items {pc*10}% complete")
                # print('.'*(pc-marked_complete), end='', flush=True)
                marked_complete = pc


# ***************************
# Generic invoices covers both invoices and credit notes
# ***************************


def default_get(row, default, index_str, index_str2=""):
    if index_str2:
        try:
            result = row[1][index_str][index_str2]
        except:  # eg if missing
            result = default
    else:
        try:
            result = row[1][index_str]
        except:  # eg if missing
            result = default
    try:
        if f"{result}" == "NaT":
            result = default
    except:
        result = default
    return result


def invoices_all(df):
    "Iterate all invoice fields in dataframe"
    for row in df.iterrows():
        contact_id = default_get(row, 0.0, "Contact", "ContactID")
        due_date = default_get(row, None, "DueDate")
        payment_date = default_get(row, None, "ExpectedPaymentDate")
        planned_payment_date = default_get(row, None, "PlannedPaymentDate")
        yield (
            row[1]["InvoiceID"],
            contact_id,
            row[1]["CurrencyCode"],
            row[1]["CurrencyRate"],
            row[1]["Date"],
            row[1]["SubTotal"],
            row[1]["Total"],
            row[1]["TotalTax"],
            row[1]["Status"],
            row[1]["Type"],
            row[1]["UpdatedDateUTC"],
            row[1]["InvoiceNumber"],
            due_date,
            payment_date,
            planned_payment_date,
        )


def load_invoices(df=None, all=None):
    with SQLExecute() as cursor:
        i = 0
        num = len(df)
        marked_complete = 0
        for (
            id,
            contact_id,
            currency_code,
            currency_rate,
            date,
            nett,
            gross,
            tax,
            status,
            invoice_type,
            updated_date_utc,
            invoice_number,
            due_date,
            expected_payment_date,
            planned_payment_date,
        ) in all(df):
            sql = f"""
INSERT INTO xeroapp_Invoice 
(    xerodb_id, contact_id_id, currency_code, 
     currency_rate, inv_date, nett, 
     gross, tax, status, 
     invoice_type, updated_date_utc, inv_number,
     due_date, expected_payment_date, planned_payment_date
     )
VALUES
(    %s, %s, %s, 
     %s, %s, %s, 
     %s, %s, %s, 
     %s, %s, %s, 
     %s, %s, %s)"""
            params = (
                id,
                contact_id,
                currency_code,
                currency_rate,
                date,
                nett,
                gross,
                tax,
                status,
                invoice_type,
                updated_date_utc,
                invoice_number,
                due_date,
                expected_payment_date,
                planned_payment_date,
            )
            cursor.execute(sql, params)
            i += 1
            pc = int(10.0 * (i / num))  # percent complete
            if pc > marked_complete:
                print(f"Load invoices {pc*10}% complete")
                # print('.'*(pc-marked_complete), end='', flush=True)
                marked_complete = pc


def credit_notes_all(df):
    """Generator for all credit notes"""
    for row in df.iterrows():
        contact_id = default_get(row, 0.0, "Contact", "ContactID")
        due_date = default_get(row, None, "DueDate")
        payment_date = default_get(row, None, "ExpectedPaymentDate")
        planned_payment_date = default_get(row, None, "PlannedPaymentDate")
        yield (
            row[1]["CreditNoteID"],
            contact_id,
            row[1]["CurrencyCode"],
            row[1]["CurrencyRate"],
            row[1]["Date"],
            -row[1]["SubTotal"],
            -row[1]["Total"],
            -row[1]["TotalTax"],
            row[1]["Status"],
            row[1]["Type"],
            row[1]["UpdatedDateUTC"],
            row[1]["CreditNoteNumber"],
            due_date,
            payment_date,
            planned_payment_date,
        )


# ***************************
# Generic invoice line items
# ***************************


unknown_list = []
unknown_description_list = []
unknown_code_list = []


class ItemError(Exception):
    pass


def get_item(line, items):
    """Aims to convert a line item into an item code in the items database.  Not all products use a consistent key.
    Returns an id into the items database. Or none if it cannot be found."""
    try:
        code = line["ItemCode"]
        # There is a valid code, now just need to find matching product item entry
        try:
            found = items[items["Code"] == code]
            if len(found) == 1:
                item_id = found.iloc[0]["ItemID"]
            else:
                item_id = None
        except KeyError:
            unknown_code_list.append(code)
            raise KeyError
    except KeyError:  # Try matching on description as couldn't find an itemcode
        #  Old invoices that were entered didn't match up to invoice.
        try:
            description = line["Description"]
            try:
                found = items[items["Description"] == description]
                if len(found) == 1:
                    item_id = found.iloc[0]["ItemID"]
                else:
                    item_id = None
            except KeyError:
                unknown_description_list.append(description)
                raise KeyError  # problem
        except:
            unknown_list.append(line)
            # raise ItemError('Not found (no id or description)', line)
            item_id = None
    return item_id


def abstract_lineitems_all(df, items, id_name, number_name):
    for row in df.iterrows():
        invoice_id = row[1][id_name]
        inv_number = row[1][number_name]
        for line in row[1]["LineItems"]:
            try:
                id = line["LineItemID"]
            except KeyError:  # there is no line item ID
                # but must have unique key so generate one here
                # Maybe there is a better solution
                id = str(uuid.uuid4())
            item_id = get_item(line, items)
            yield (id, invoice_id, item_id, line["Quantity"], line["UnitAmount"])


def invoice_lineitems_all(df, items):
    yield from abstract_lineitems_all(df, items, "InvoiceID", "InvoiceNumber")


def credit_note_lineitems_all(df, items):
    yield from abstract_lineitems_all(df, items, "CreditNoteID", "CreditNoteNumber")


def load_invoice_items(df=None, all=None, items=None):
    with SQLExecute() as cursor:
        i = 0
        num = len(df)
        marked_complete = 0
        old_invoice_id = ""
        for (id, invoice_id, item_id, qty, price) in all(df, items):
            sql = f"""INSERT INTO xeroapp_LineItem (id, invoice_id, item_id, quantity, 
                price)
                VALUES(%s, %s, %s, %s, %s)"""
            params = (id, invoice_id, item_id, qty, price)
            cursor.execute(sql, params)
            if old_invoice_id != invoice_id:
                old_invoice_id = invoice_id
                i += 1
            pc = int(10.0 * (i / num))  # percent complete
            if pc > marked_complete:
                print(f"Load invoice items {pc*10}% complete")
                # print('.'*(pc-marked_complete), end='', flush=True)
                marked_complete = pc
        print("")
