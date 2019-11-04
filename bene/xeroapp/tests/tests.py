import datetime as dt
import json
import uuid

from django.test import TestCase

from bene.xeroapp.models import Item
from bene.xeroapp.xero_db_load import load_item
from bene.xeroapp.update_models_from_xero import get_all

demo_items = """{
  "Items": [
    {
      "ItemID": "9a59ea90-942e-484d-9b71-d00ab607e03b",
      "Code": "Merino-2011-LG",
      "Description": "2011 Merino Sweater - LARGE",
      "UpdatedDateUTC": "\/Date(1488338552390+0000)\/",
      "PurchaseDetails": {
        "UnitPrice": 149.0000,
        "AccountCode": "300"
      },
      "SalesDetails": {
        "UnitPrice": 299.0000,
        "AccountCode": "200"
      }
    },
      {
          "ItemID": "19b79d12-0ae1-496e-9649-cbd04b15c7c5",
          "Code": "UnTrackedThing",
          "Description": "I sell this untracked thing",
          "PurchaseDescription": "I buy this untracked thing",
          "UpdatedDateUTC": "\/Date(1488338552390+0000)\/",
          "PurchaseDetails": {
              "UnitPrice": 20.0000,
              "AccountCode": "400",
              "TaxType": "NONE"
          },
          "SalesDetails": {
              "UnitPrice": 40.0000,
              "AccountCode": "200",
              "TaxType": "OUTPUT2"
          },
          "Name": "An Untracked Item",
          "IsTrackedAsInventory": false,
          "IsSold": true,
          "IsPurchased": true
      },
      {
          "ItemID": "90a72d44-43e4-410d-a68b-1139ef0c0c07",
          "Code": "TrackedThing",
          "Description": "I sell this tracked thing",
          "PurchaseDescription": "I purchase this tracked thing",
          "UpdatedDateUTC": "\/Date(1488338552390+0000)\/",
          "PurchaseDetails": {
              "UnitPrice": 20.0000,
              "COGSAccountCode": "430",
              "TaxType": "NONE"
          },
          "SalesDetails": {
              "UnitPrice": 40.0000,
              "AccountCode": "200",
              "TaxType": "OUTPUT2"
          },
          "Name": "Tracked Thing",
          "IsTrackedAsInventory": true,
          "InventoryAssetAccountCode": "630",
          "TotalCostPool": 200.00,
          "QuantityOnHand": 10.0000,
          "IsSold": true,
          "IsPurchased": true
      }
  ]
}
"""


def dummy_get_items(paged=False):
    return json.loads(demo_items)["Items"]


class ItemTestCase(TestCase):
    def setUp(self):
        Item.objects.create(
            xerodb_id=str(uuid.uuid4()),
            code="DPC456",
            name="Some damp proof course",
            cost_price=24.45,
            sales_price=36.34,
        )
        Item.objects.create(
            xerodb_id=str(uuid.uuid4()),
            code="A111",
            name="Another item",
            cost_price=0.0,
            sales_price=0.0,
        )

    def test_Items_can_be_created(self):
        """Items that can speak are correctly identified"""
        first_item = Item.objects.get(code="DPC456")
        second_item = Item.objects.get(name="Another item")
        self.assertEqual("Some damp proof course", str(first_item))
        self.assertEqual("Another item", str(second_item))

    def test_parsing_items(self):
        records = json.loads(demo_items)["Items"]
        print(f"{records}")
        self.assertEqual(3, len(records))

    def test_get_items(self):
        dir_root = dt.datetime.now().strftime(f"TEST_get_items_%Y-%m-%dT%H-%M-%S")
        for i, item in enumerate(get_all(dummy_get_items, "Xero_Items", dir_root, paged=False)):
            load_item(item)
        self.assertEquals(3, len(Item.objects.all()))
