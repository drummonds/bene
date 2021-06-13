import uuid

from django.db import connection, IntegrityError


# ***************************
# Utilities
# ***************************


def truncate_data():
    """Currently have to truncate all data in order to upload new variants."""
    with connection.cursor() as cursor:
        # Data is interconnected with foreign keys so have to get rid of it all
        cursor.execute(
            "TRUNCATE xeroapp_ContactGroup, xeroapp_Contact, xeroapp_Invoice, xeroapp_LineItem, xeroapp_Item"
        )


def default_get(record, default, index_str, index_str2=""):
    """Like get from dictionary but gets 1 or 2 levels"""
    if index_str2:
        try:
            result = record[index_str][index_str2]
        except KeyError:  # eg if missing
            result = default
    else:
        try:
            result = record[index_str]
        except KeyError:  # eg if missing
            result = default
    try:
        if f"{result}" == "NaT":
            result = default
    except:
        result = default
    return result


class SQLExecute:
    """Wrapper for SQL execute that has error handling, eg when data is missing or incomplete."""

    def __init__(self, num_failures_to_report=10):
        self.cursor = connection.cursor()
        self.first_failures = num_failures_to_report

    def __enter__(self):
        self.cursor.__enter__()
        return self

    def __exit__(self, *exc_info):
        self.cursor.__exit__(*exc_info)

    def handle_failure(self, e, sql, params):
        if self.first_failures > 0:
            print("# ~~~ Loading data into database failed")
            print(f"sql = {sql}")
            if params:
                print(f"params = {params}")
            else:
                print("No params")
            print(e)
            self.first_failures -= 1

    def execute(self, sql, params=None):
        try:
            if params:
                self.cursor.execute(sql, params)
            else:
                self.cursor.execute(sql)
        except Exception as e:
            self.handle_failure(e, sql, params)


# ***************************
# Contact groups
# ***************************


def load_contact_group(record):
    """Given a dictionary for a single row will load the data into SQL"""
    with SQLExecute() as cursor:
        sql = f"""INSERT INTO xeroapp_ContactGroup ("xerodb_id", name) 
        VALUES('{record["ContactGroupID"]}', '{record.get("Name","No name in Xero")}')"""
        cursor.execute(sql)


# ***************************
# Contacts
# ***************************


def insert_contact(
    cursor,
    id,
    name="No name",
    number=0,
    first_name="No First Name",
    last_name="No Last Name",
    email_address="none@none.com",
):
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
    with SQLExecute() as cursor:
        cursor.execute(sql, params)


def load_contact(record):
    with SQLExecute() as cursor:
        insert_contact(
            cursor,
            record["ContactID"],
            name=record.get("Name", "No Xero Name"),
            number=record.get("AccountNumber",""),
            first_name=default_get(record, "No First Name", "FirstName"),
            last_name=default_get(record, "No Last Name", "LastName"),
            email_address=default_get(record, "none@none.com", "EmailAddress"),
        )


# ***************************
# Inventory items or product catalogue
# ***************************


def load_item(record):
    with SQLExecute() as cursor:
        try:
            cost_price = record["PurchaseDetails"]["UnitPrice"]
        except:  # eg if missing
            cost_price = 0.0
        try:
            sales_price = record["SalesDetails"]["UnitPrice"]
        except:  # eg if missing
            sales_price = 0.0
        sql = f"""INSERT INTO xeroapp_Item ("xerodb_id",code, name, cost_price, sales_price)
        VALUES(%(id)s, %(code)s, %(name)s, %(cost_price)s, %(sales_price)s)"""
        params = {
            "id": record["ItemID"],
            "code": record.get("Code", "No Xero code"),
            "name": record.get("Description", "No Xero Description"),
            "cost_price": cost_price,
            "sales_price": sales_price,
        }
        cursor.execute(sql, params)


# ***************************
# Generic invoices covers both invoices and credit notes
# ***************************


def load_invoice(record, transform=None):
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
    if transform:
        record = transform(record)
    with SQLExecute() as cursor:
        contact_id = default_get(record, None, "Contact", "ContactID")
        due_date = default_get(record, None, "DueDate")
        payment_date = default_get(record, None, "ExpectedPaymentDate")
        planned_payment_date = default_get(record, None, "PlannedPaymentDate")
        # Todo Not sure I like the list of parameters without a dictionary look up.
        params = (
            record["InvoiceID"],
            contact_id,
            record.get("CurrencyCode", "GBP"),
            record.get("CurrencyRate", 1),
            record["Date"],
            record["SubTotal"],
            record["Total"],
            record["TotalTax"],
            record.get("Status", "No Xero status"),
            record["Type"],
            record["UpdatedDateUTC"],
            record.get("InvoiceNumber", "No Xero Invoice Number"),
            due_date,
            payment_date,
            planned_payment_date,
        )
        try:
            cursor.cursor.execute(sql, params)
        except Exception as e:
            print(f" Problem with SQL exception = {str(e)}")
            if "fk_xeroapp_contact_xerodb_id" in str(e):
                #  insert contact and retry
                insert_contact(
                    cursor, contact_id, name="This contact missing but in invoice"
                )
                cursor.execute(
                    sql, params
                )  # Use default error handling if another error occurs
            else:  # unknown error
                cursor.handle_failure(e, sql, params)


def credit_note_transform(record):
    """Transform a credit note so that it looks lke an invoice"""
    record["InvoiceID"] = record["CreditNoteID"]
    record["SubTotal"] = -record["SubTotal"]
    record["Total"] = -record["Total"]
    record["TotalTax"] = -record["TotalTax"]
    record["InvoiceNumber"] = record["CreditNoteNumber"]
    return record


# ***************************
# Generic invoice line items
# ***************************


unknown_list = []
unknown_description_list = []
unknown_code_list = []


def get_item(line, item_catalogue):
    """Aims to convert a line item into an item code in the items database.  Not all products use a consistent key.
    Returns an id into the items database. Or none if it cannot be found."""
    # TODO could convert this to a database query rather than using a cache
    try:
        code = line["ItemCode"]
        # Item does have a valid code, now just need to find matching product item entry
        try:
            item_id = item_catalogue["Code"][code]
        except KeyError:
            unknown_code_list.append(code)
            raise KeyError
    except KeyError:  # Try matching on description as couldn't find an itemcode
        #  Old invoices that were entered didn't match up to invoice.
        try:
            description = line["Description"]
            try:
                item_id = item_catalogue["Description"][code]
            except KeyError:
                unknown_description_list.append(description)
                raise KeyError  # problem
        except:
            unknown_list.append(line)
            # raise ItemError('Not found (no id or description)', line)
            item_id = None
    return item_id


def abstract_lineitems_all(invoice_record, items):
    """For a single invoice record extract all the lineitems"""
    invoice_id = invoice_record["InvoiceID"]
    try:
        for line in invoice_record["LineItems"]:
            id = line.get(
                "LineItemID", str(uuid.uuid4())
            )  # there is no ID for each line entry
            # but must have unique key so generate one here
            item_id = get_item(line, items)  # Need to convert item name to an ID
            try:
                quantity = line["Quantity"]
            except KeyError:  # There is no quantity
                quantity = 0
                print(f"Unusual no quantity in this row of line items from Xero: {line}")
            unit_amount = line.get("UnitAmount", 1)
            yield (id, invoice_id, item_id, quantity, unit_amount)
    except KeyError:
        pass  # There are no line items


def invoice_lineitems_all(invoice_record, item_catalogue):
    yield from abstract_lineitems_all(invoice_record, item_catalogue)


def credit_note_lineitems_all(invoice_record, item_catalogue):
    yield from abstract_lineitems_all(invoice_record, item_catalogue)


def load_invoice_items(
    invoice_record, invoice_transform=None, get_items=None, item_catalogue=None
):
    """For a single invoice in invoice_record, load all the items into the database"""
    if invoice_transform:
        invoice_record = invoice_transform(invoice_record)
    with SQLExecute() as cursor:
        for (id, invoice_id, item_id, qty, price) in get_items(
            invoice_record, item_catalogue
        ):
            sql = f"""INSERT INTO xeroapp_LineItem (id, invoice_id, item_id, quantity, 
                price)
                VALUES(%s, %s, %s, %s, %s)"""
            params = (id, invoice_id, item_id, qty, price)
            cursor.execute(sql, params)
