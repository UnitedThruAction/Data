"""Local CouchDB cache of data from the NY Senate API.
"""

from requests import get
import couchdb
from uuid import uuid4
import sys


class Cache(object):

    def __init__(self, key):
        self.key = key
        self.server = couchdb.Server()
        self.db = self.server['united-thru-action']

    def populate(self, year="2016"):
        """Populate bills for a given year for analysis."""
        bills = self.get_bills_year(year)
        count = 0
        print("\nGetting bill details.")
        for bill in bills:
            doc = self.get_bill_detail(year, bill['printNo'])
            doc_id = uuid4().hex
            self.db[doc_id] = doc
            count += 1
            if count % 100 == 0:
                print(".", end="")

    def get_bills_year(self, year):
        offset = 1
        more = True
        total = None
        bills = []
        print("Getting bill list.")
        while more:
            payload = {
                'key': self.key,
                'view': 'info',
                'limit': 100,
                'offset': offset}
            r = get(
                'http://legislation.nysenate.gov/api/3/bills/' +
                year,
                params=payload)
            r.raise_for_status()
            total = r.json()['total']
            for bill in r.json()['result']['items']:
                bills.append(bill)
            offset += r.json()['result']['size']
            more = False if offset >= total else True
            print(".", end="")
        return bills

    def get_bill_detail(self, year, printNo):
        payload = {'key': self.key, 'view': 'default'}
        r = get("http://legislation.nysenate.gov/api/3/bills/{}/{}".format(year,
                                                                               printNo), params=payload)
        r.raise_for_status()
        doc = r.json()['result']
        doc['year'] = year
        return doc

    def reconcile(self, year="2016"):
        bills = self.get_bills_year(year)
        count = 0
        print("\nGetting bill details.")
        for bill in bills:
            db_vers = self.db.view('db-views/by_year_printNo')[[year,bill['printNo']]]
            if len(db_vers) == 0: # not in cache
                doc = self.get_bill_detail(year, bill['printNo'])
                doc_id = uuid4().hex
                self.db[doc_id] = doc
            if len(db_vers) > 1: # >1 in cache
                to_delete = db_vers[1:]
                for doc in to_delete:
                    del self.db[doc.id]
            count += 1
            if count % 100 == 0:
                print(".", end="")


class Unbuffered(object):
   def __init__(self, stream):
       self.stream = stream
   def write(self, data):
       self.stream.write(data)
       self.stream.flush()
   def __getattr__(self, attr):
       return getattr(self.stream, attr)

if __name__ == "__main__":
    sys.stdout = Unbuffered(sys.stdout)
    c = Cache(sys.argv[1])
    c.populate(sys.argv[2])
