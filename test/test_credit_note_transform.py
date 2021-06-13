from copy import deepcopy
import datetime
import unittest

DUMMY_CREDIT_NOTE = {
    "CreditNoteID": "0b00935b-4297-4c73-b694-b2b45147dc1e",
    "CreditNoteNumber": "C14",
    "Payments": [],
    "ID": "0b00935b-4297-4c73-b694-b2b45147dc1e",
    "HasErrors": False,
    "CurrencyRate": 1.0,
    "Type": "ACCPAYCREDIT",
    "Reference": "C14",
    "RemainingCredit": 0.0,
    "Allocations": [
        {
            "Amount": 0.67,
            "Date": datetime.datetime(2015, 9, 2, 0, 0),
            "Invoice": {
                "InvoiceID": "222e74e7-cd60-47d8-9797-7cea7430dabb",
                "InvoiceNumber": "None",
                "Payments": [],
                "CreditNotes": [],
                "Prepayments": [],
                "Overpayments": [],
                "IsDiscounted": False,
                "HasErrors": False,
                "LineItems": [],
            },
        }
    ],
    "HasAttachments": False,
    "Contact": {
        "ContactID": "5e76175e-0732-408e-b48d-6e05872beb9a",
        "ContactNumber": "72555bcd-bbc1-4929-97b3-7cb9175e85d0",
        "Name": "BRITISH TELECOM PLC",
        "Addresses": [],
        "Phones": [],
        "ContactGroups": [],
        "ContactPersons": [],
        "HasValidationErrors": False,
    },
    "DateString": datetime.date(2015, 4, 8),
    "Date": datetime.datetime(2015, 4, 8, 0, 0),
    "DueDateString": datetime.date(2015, 4, 8),
    "DueDate": datetime.datetime(2015, 4, 8, 0, 0),
    "Status": "PAID",
    "LineAmountTypes": "Exclusive",
    "LineItems": [
        {
            "Description": "Mob rental chge",
            "UnitAmount": 0.56,
            "TaxType": "INPUT2",
            "TaxAmount": 0.11,
            "LineAmount": 0.56,
            "AccountCode": "2109",
            "Tracking": [],
            "Quantity": 1.0,
        }
    ],
    "SubTotal": 0.56,
    "TotalTax": 0.11,
    "Total": 0.67,
    "UpdatedDateUTC": datetime.datetime(2017, 2, 6, 18, 17, 43, 723000),
    "CurrencyCode": "GBP",
    "FullyPaidOnDate": datetime.datetime(2015, 9, 2, 0, 0),
}

from bene.xeroapp.xero_db_load import credit_note_transform


class TestJSONParameter(unittest.TestCase):

    def test_transform(self):
        test = deepcopy(DUMMY_CREDIT_NOTE)
        test = credit_note_transform(test)
        print(test)
        self.assertEqual(test['Total'],-0.67)
        self.assertEqual(test["InvoiceID"], "0b00935b-4297-4c73-b694-b2b45147dc1e")
        self.assertEqual(-0.56, test["SubTotal"])
        self.assertEqual(-0.11, test["TotalTax"])
        self.assertEqual('C14', test["InvoiceNumber"])
