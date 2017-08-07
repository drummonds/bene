import datetime as dt
from functools import wraps
from numpy import isnan
import pandas as pd
import psycopg2
from psycopg2 import InterfaceError, IntegrityError
from unipath import Path
import yaml


from luca import p

#***************************
# Database connection
#***************************

# bene_prod
def postgres_production():
    return psycopg2.connect(
        dbname='d9fjtam9q6qofp',
        user='lcrhvbsiyzokef',
        host='ec2-54-247-177-33.eu-west-1.compute.amazonaws.com',
        password='7313adb5e6c9dae86f3ab4b4519b0f066fed91aa4cb02add5b489576727b206e',
        sslmode='require'
        )

# Local
def postgres_local():
    return psycopg2.connect(
        dbname='bene',
        host='localhost',
        )

DATABASE_CONNECTION = 'production' 

def database_conn():
    if DATABASE_CONNECTION == 'production':
        return postgres_production()
    else:
        return postgres_local()

#***************************
# Utilties
#***************************

def test_database_conn():
    try:
        conn = database_conn()
        print ("** Connected to the database")
        cur = conn.cursor()
        cur.execute("""SELECT * from django_site""")
        rows = cur.fetchall()
        for row in rows:
            print (f"{row}")
        print ("** closing database")
        conn.close()
    except:
        print ("I am unable to connect to the database")


def read_in(file_name):
    """Reads in a YML file which is extracted from Xero and converts it into a dataframe.  Note often
    the fields contain nested master slave relationships."""
    with open(file_name, 'r') as f:
        result = yaml.safe_load(f.read())
    return pd.DataFrame(result)

def db_command(func):
    """opens up the database and closes it for the function.  Makes available a live cursor cur"""
    @wraps(func)
    def db_access_wrapper(*args, **kwargs):       
        try:
            conn = database_conn()
            conn.autocommit = True
            cur = conn.cursor()
            print (f"** Connected to the database for {func.__name__}")
            func(conn, cur, *args, **kwargs)
            print ("** closing database")
            conn.close()
        except InterfaceError as err:
            print (f"I am unable to connect to the database: {err}")
    return db_access_wrapper

@db_command
def truncate_data(conn, cur):
    """Currently have to truncate all data in order to upload new variants."""
    # Data is interconnected with foreign keys so have to get rid of it all
    cur.execute('TRUNCATE xero_ContactGroup, xero_Contact, xero_Invoice, xero_LineItem, xero_Item')


#***************************
# Contact groups
#***************************

def contact_groups(cg):
    for row in cg.iterrows():
        yield row[1]['Name'], row[1]['ContactGroupID']

@db_command
def load_contact_group(conn, cur, df):
    cur.execute('TRUNCATE xero_ContactGroup')
    i = 0
    for n, id in contact_groups(df):
        sql = f"""INSERT INTO xero_ContactGroup ("xerodb_id", name) VALUES('{id}', '{n}')"""
        cur.execute(sql)
        i += 1

#***************************
# Contacts
#***************************

def contacts_all(c):
    for row in c.iterrows():
        yield row[1]['ContactID'], row[1]['Name'], row[1]['AccountNumber']


@db_command
def load_contacts(conn, cur, df):
    i = 0
    for id, name, number in contacts_all(df):
        try:
            if isnan(number):
                number = ''
        except:
            pass
        sql = f"""INSERT INTO xero_Contact ("xerodb_id", name, number ) VALUES(%(id)s, %(name)s, %(number)s)"""
        params = {'id': id, 'name': name, 'number': number}
        cur.execute(sql, params)
        i+=1


#***************************
# Inventory items
#***************************

def items_all(df):
    for row in df.iterrows():
        try:
            cost_price = row[1]['PurchaseDetails']['UnitPrice']
        except:  # eg if missing
            cost_price = 0.0
        try:
            sales_price = row[1]['SalesDetails']['UnitPrice']
        except:  # eg if missing
            sales_price = 0.0
        yield row[1]['ItemID'], row[1]['Code'], row[1]['Description'], cost_price, sales_price

@db_command
def load_items(conn, cur, df):
    i = 0
    num = len(df)
    marked_complete = 0
    for id, code, name, cost_price, sales_price in items_all(df):
        sql = f"""INSERT INTO xero_Item ("xerodb_id",code, name, cost_price, sales_price)
        VALUES(%(id)s, %(code)s, %(name)s, %(cost_price)s, %(sales_price)s)"""
        params = {'id': id, 'code': code, 'name': name, 'cost_price': cost_price, 'sales_price':sales_price}
        cur.execute(sql, params)
        i+=1
        pc = int(100.0 * (i / num))  # percent complete
        if pc > marked_complete:
            print('.'*(pc-marked_complete), end='', flush=True)
            marked_complete = pc
    print('')


#***************************
# Generic invoices covers both invoices and credit notes
#***************************

def invoices_all(df):
    for row in df.iterrows():
        try:
            contact_id = row[1]['Contact']['ContactID']
        except:  # eg if missing
            cost_price = 0.0
        yield (row[1]['InvoiceID'], contact_id, row[1]['CurrencyCode'], row[1]['CurrencyRate'],
               row[1]['Date'], row[1]['SubTotal'], row[1]['Total'],
               row[1]['TotalTax'], row[1]['Status'], row[1]['Type'],
               row[1]['UpdatedDateUTC'], row[1]['InvoiceNumber'])

@db_command
def load_invoices(conn, cur, df=None, all=None):
    i = 0
    num = len(df)
    marked_complete = 0
    for (id, contact_id, currency_code, currency_rate, 
         date, nett, gross, 
         tax, status, invoice_type, 
         updated_date_utc, invoice_number) in all(df):
        try:
            sql = f"""INSERT INTO xero_Invoice (xerodb_id, contact_id_id, currency_code, currency_rate, 
            inv_date, nett, gross, tax, status, invoice_type, updated_date_utc, inv_number)
            VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            params = (id, contact_id, currency_code, currency_rate, date, nett, gross, tax, status, invoice_type, 
                      updated_date_utc, invoice_number)
            cur.execute(sql, params)
        except IntegrityError:
            pass  # TODO but for the moment ignore things like
        """IntegrityError: insert or update on table "xero_invoice" violates foreign key constraint "xero_invoice_contact_id_id_833dbd1a_fk_xero_contact_xerodb_id"
DETAIL:  Key (contact_id_id)=(97ead41b-22cb-4f63-bf92-d8dbc9dc610a) is not present in table "xero_contact"."""
        i+=1
        pc = int(100.0 * (i / num))  # percent complete
        if pc > marked_complete:
            print('.'*(pc-marked_complete), end='', flush=True)
            marked_complete = pc
    print('')


def credit_notes_all(df):
    """Generator for all credit notes"""
    for row in df.iterrows():
        try:
            contact_id = row[1]['Contact']['ContactID']
        except:  # eg if missing
            cost_price = 0.0
        yield (row[1]['CreditNoteID'], contact_id, row[1]['CurrencyCode'], row[1]['CurrencyRate'], 
               row[1]['Date'], -row[1]['SubTotal'], -row[1]['Total'], 
               -row[1]['TotalTax'], row[1]['Status'], row[1]['Type'],
               row[1]['UpdatedDateUTC'], row[1]['CreditNoteNumber'])


#***************************
# Generic invoice line items
#***************************


unknown_list = []
unknown_description_list = []
unknown_code_list = []


class ItemError(Exception):
    pass


def get_item(line, items):
    """Aims to convert a line item into an item code in the items database.  Not all products use a consistent key.
    Returns an id into the items database. Or none if it cannot be found."""
    try:
        code = line['ItemCode']
        # There is a valid code, now just need to find matching product item entry
        try:
            found = items[items['Code'] == code]
            if len(found) == 1:
                item_id = found.iloc[0]['ItemID']
            else:
                item_id = None
        except KeyError:
            unknown_code_list.append(code)
            raise KeyError
    except KeyError:  # Try matching on description as couldn't find an itemcode
        #  Old invoices that were entered didn't match up to invoice.
        try:
            description = line['Description']
            try:
                found = items[items['Description'] == description]
                if len(found) == 1:
                    item_id = found.iloc[0]['ItemID']
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


def invoice_lineitems_all(df, items):
    for row in df.iterrows():
        invoice_id = row[1]['InvoiceID']
        inv_number = row[1]['InvoiceNumber']
        for line in row[1]['LineItems']:
            id = line['LineItemID']
            item_id = get_item(line, items)
            yield (id, invoice_id, item_id, line['Quantity'], line['UnitAmount'])


@db_command
def load_invoice_items(conn, cur, df=None, all=None, items=None):
    i = 0
    num = len(df)
    marked_complete = 0
    old_invoice_id = ''
    for (id, invoice_id, item_id, qty, price) in all(df, items):
        try:
            sql = f"""INSERT INTO xero_LineItem (id, invoice_id, item_id, quantity, 
            price)
            VALUES(%s, %s, %s, %s, %s)"""
            params = (id, invoice_id, item_id, qty, price)
            cur.execute(sql, params)
        except IntegrityError:
            if old_invoice_id == '':
                print(sql, params)
            pass  # TODO but for the moment ignore things like
        """IntegrityError: insert or update on table "xero_invoice" violates foreign key constraint "xero_invoice_contact_id_id_833dbd1a_fk_xero_contact_xerodb_id"
DETAIL:  Key (contact_id_id)=(97ead41b-22cb-4f63-bf92-d8dbc9dc610a) is not present in table "xero_contact"."""
        if old_invoice_id != invoice_id:
            old_invoice_id = invoice_id
            i+=1
        pc = int(100.0 * (i / num))  # percent complete
        if pc > marked_complete:
            print('.'*(pc-marked_complete), end='', flush=True)
            marked_complete = pc
    print('')
    