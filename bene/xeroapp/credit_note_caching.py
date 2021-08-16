import datetime as dt
import pandas as pd
import sys
from time import sleep
from unipath import Path
import yaml


def read_in(file_root="Xero_data"):
    file_name = Path(".").child(
        file_root + dt.datetime.now().strftime(" %Y-%m-%d") + ".yml"
    )
    with open(file_name, "r") as f:
        result = yaml.safe_load(f.read())
    return pd.DataFrame(result)


# going to convert this to a function that will iterate through all credit notes giving an id and last modified date.
def all_credit_notes(credit_notes):
    for row in credit_notes.iterrows():
        # print(row[1])
        yield row[1]["CreditNoteID"], row[1]["UpdatedDateUTC"]


MAX_API_CALLS = 12  # Per 15 second period


class CreditNoteCache:
    def test_credit_note(self, xero, id, last_updated):
        """Does the id exist in cache if not get it?
        Else if cache updates dates not equal then update."""
        try:
            cached_credit_note = self.cache[id]
            last_update = cached_credit_note["UpdatedDateUTC"]
            if last_updated != cached_credit_note["UpdatedDateUTC"]:
                self.cache[id] = xero.creditnotes.get(id)[0]  # Overwrite old version
                self.api_counter -= 1
                print("U", end="", flush=True)
            else:
                print(".", end="", flush=True)
        except KeyError:
            self.cache[id] = xero.creditnotes.get(id)[0]
            self.api_counter -= 1
            print("N", end="", flush=True)

    @property
    def cache_file_name(self):
        return Path(".").child("Credit Note Cache.yml")

    def read_cache(self):
        if self.cache_file_name.exists():
            with open(self.cache_file_name.absolute(), "r") as f:
                self.cache_variables, self.cache = yaml.safe_load(f.read())
        else:
            self.cache_variables = {}
            self.cache = {}

    def write_cache(self):
        with open(self.cache_file_name.absolute(), "w") as f:
            f.write(yaml.dump([self.cache_variables, self.cache]))

    def update_cache(self, xero, yaml_file_name):
        """yaml_file_name is the abreviated file name"""
        print("Updating credit notes cache")
        self.read_cache()
        # Read in abbreviated file
        self.api_counter = MAX_API_CALLS
        self.cn_counter = 100
        start_time = dt.datetime.now()
        df_credit_notes = read_in("Xero_CreditNotes")  # no line entries.
        print(
            "There are {} credit notes in the abreviated file".format(
                len(df_credit_notes)
            )
        )
        for id, last_update in all_credit_notes(df_credit_notes):
            self.test_credit_note(xero, id, last_update)
            self.cn_counter -= 1
            if self.api_counter <= 0:  # Max limit is 60 per minute
                self.api_counter = MAX_API_CALLS
                while (dt.datetime.now() - start_time).seconds < 15:
                    self.write_cache()  # save current state of cache in case of crash
                    test = dt.datetime.now()
                    print("w", end="", flush=True)
                    sleep(5)
                start_time = dt.datetime.now()
                self.cn_counter = 100
                print("R")
            if self.cn_counter <= 0:
                self.cn_counter = 100
                print("r")
        self.write_cache()

    def test_update_cache(self, xero, yaml_file_name):
        """yaml_file_name is the abreviate file name"""
        print("Updating cached credit notes")
        result = xero.creditnotes.get("d919a95c-aaf7-4f46-aa4d-97fec75d263b")
        file_name = Path(".").child(
            "Test" + dt.datetime.now().strftime(" %Y-%m-%d") + ".yml"
        )
        with open(file_name, "w") as f:
            f.write(yaml.dump(result))
