import json
import unittest

from bene.utils.json_parameters import json_to_params


class TestJSONParameter(unittest.TestCase):

    def test_basic(self):
        # URL param string
        a = '?params=startdate%3A2017-06-01%7Cenddate%3A2017-06-30'
        b = '{"startdate":[2017, 6, 1], "enddate":[2017, 6, 30]}'
        c = json.loads(b)
        d = json_to_params(c)
        self.assertEqual(a, d)
