"""
convert a single text file to a YML remittance
"""
from django.core.files.storage import default_storage as storage

import datetime as dt
import yaml

from remittance import Remittance, RemittanceError, RemittanceDoc, RemittanceException, p
from remittance import Invoice, InvoiceReversal, DebitNote, CreditNote, DebitNoteReversal

class ParseFenwicksHeader():
    def __init__(self):
        self.intro = {
            0: 'FENWICK LIMITED  NORTHUMBERLAND STREET NEWCASTLE UPONTYNE NE99 1AR TELEPHONE 0191 232 5100',
            2: 'REMITTANCE ADVICE',
            12: 'DATE',
            14: 'REFERENCE',
            16: 'DESCRIPTION',
            18: 'AMOUNT',
            20: 'DISCOUNT',
            21: ''}

    def find_offset(self, doc):
        # Sometimes there are a couple of extra lines so see which line matches the
        result = -99
        key = self.intro[0]
        for i in range(5):
            if doc.page[i] == key:
                result = i
        if result == -99:
            raise (RemittanceError('Tried to find key but not found in first few lines'))
        return result

    def check(self, doc, remittance):
        all_ok = True
        offset = self.find_offset(doc)
        for key, value in self.intro.items():
            line_index = key
            line = doc.page[line_index + offset]
            if line != value:
                all_ok = False
                print("Problem with line number {}, = '{}' should be '{}'".format(key, line, value))
        doc.parse_lines_linenumber = 22 + offset
        remittance.supplier_reference = doc.page[9 + offset].split()[-1]
        if all_ok:
            remittance.supplier = 'Fenwick'
        return all_ok  # ?


def get_amount(s):
    sign = 1
    s1 = s.replace(',','')
    if s1[-2:].upper() == 'CR':
        sign = -1
        s2 = s1[0:-2]
    else:
        s2 = s1
    return sign * p(float(s2))

class ParseLineItems():
    """This parses the line items for Fenwicks.  The store information is ignored and is got from the invoice number.
    """

    def parse_line(self, item, word_count):
        item.number = self.words[3]
        item.remittance_item_date = dt.datetime.strptime('{}-{}-{}'.format(self.words[0],
                                                                              self.words[1],
                                                                              self.words[2]) , '%d-%b-%y')
        item.date = self.doc_date  # Date of invoice or transaction this is NOT the date it will be paid in
        item.gross_amount = abs(get_amount(self.words[4 + word_count]))  # Make sure gross amounts are positive even
        # if marked as CR eg for Debit notes
        # TODO it would be better if the default arrangement was dependent on the type of the line item so if
        # the sign was the wrong way around it would still be ok.
        item.discount = abs(get_amount(self.words[5 + word_count]))  # Make sure discounts are positive even if marked
        # as CR
        print(item)
        self.remittance.append(item)

    def find_doc_date(self):
        # need to find the last line which should have the date on it
        parsing = True
        self.line_index = self.doc.parse_lines_linenumber
        while parsing:
            self.line = self.doc.page[self.line_index]
            self.words = self.line.split()
            if self.line == '' and len(self.words) < 10:
                pass
            elif self.words[0] == 'AMOUNT' and self.words[1] == 'TO' and self.words[2] == 'BE':
                self.doc_date = dt.datetime.strptime(self.words[9], '%d/%m/%y')
                parsing = False
            self.line_index += 1
            if self.line_index > len(self.doc.page):
                raise RemittanceException("Didn't find line AMOUNT TO BE PAID .. so as to get Date")

    def check(self, doc, remittance):
        self.doc = doc
        self.remittance = remittance
        self.find_doc_date()
        parsing = True
        self.line_index = self.doc.parse_lines_linenumber
        while parsing:
            self.line = self.doc.page[self.line_index]
            self.words = self.line.split()
            if self.line == '':
                parsing = False
            elif self.words[0] == 'CONTACT':
                self.store = self.words[1]
                # Introducing new store  We ignore this information at the moment
                # A Fenwicks store might be multiple Sage Customers who have different delivery addresses.
            elif self.words[4] == 'INVOICE' and self.words[5] == 'REVERS.':
                self.parse_line(InvoiceReversal(), 2)
            elif self.words[4] == 'INVOICE':
                self.parse_line(Invoice(), 1)
            elif self.words[4] == 'DEBIT' and self.words[5] == 'NOTE':
                self.parse_line(DebitNote(), 2)
            elif self.words[4] == 'ADJUST' and self.words[5] == 'DEBIT':
                # This should be our credit note
                self.parse_line(CreditNote(), 2)
            elif self.words[4] == 'DEBIT' and self.words[5] == 'REVERSAL':
                self.parse_line(DebitNoteReversal(), 2)
            else:
                raise RemittanceException("Unrecognised line in line {} = |{}|".format(self.line_index, self.line))
            self.line_index += 1
        self.doc.parse_end_linenumber = self.line_index


class ParseFenwicksFooter():
    def __init__(self):
        pass

    def check(self, doc, remittance):
        all_ok = True
        # Get total
        line_index = doc.parse_end_linenumber
        line = doc.page[line_index]
        if line.split()[0] == 'TOTAL:':
            remittance.total = get_amount(line.split()[1])
        else:
            raise RemittanceException("Unrecognised line in lines = ''".format(line))
        # Get date paid in (date of remittance)
        line_index += 1
        line = doc.page[line_index]
        if line.split()[0] == 'AMOUNT' and line.split()[1] == 'TO' and line.split()[8] == 'ON':
            d = line.split()[9]
            remittance.payment_date = statement_date = dt.datetime.strptime(d, '%d/%m/%y')
        else:
            raise RemittanceException("Unrecognised line in lines = ''".format(line))
        return all_ok  # ?


def text_to_yaml(path_name, file_name):
    text_file_name = file_name[:-4]+'.txt'
    yml_file_name = file_name[:-4]+'.yml'
    with storage.open(path_name + '/' + text_file_name, 'r') as input_file:
        text = input_file.read()
    doc = RemittanceDoc()
    doc.append_page(text)
    ph = ParseFenwicksHeader()
    fenwicks = Remittance()
    pli = ParseLineItems()
    pli.check(doc, fenwicks)
    pf = ParseFenwicksFooter()
    fenwicks.doc_self_check()
    with storage.open(path_name + '/' + text_file_name, 'w') as f:
        f.write(yaml.dump((fenwicks)))
