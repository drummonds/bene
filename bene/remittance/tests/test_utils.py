import datetime as dt
import unittest

from bene.remittance.utils import date_to_path

class TestUtil(unittest.TestCase):

    def test_date_to_file_path(self):
        self.assertEqual(date_to_path(dt.datetime(2018,1,20)), '2018/2018-01/2018-01-20_00-00')
        self.assertEqual(date_to_path(dt.datetime(2018,1,20,10,42)), '2018/2018-01/2018-01-20_10-42')
