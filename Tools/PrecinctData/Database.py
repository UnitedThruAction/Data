"""Initialize CouchDB for this project.

See https://pythonhosted.org/CouchDB/
"""

from enum import Enum

from couchdb.client import Server
from couchdb.design import ViewDefinition

class Database(object):
    """Handle connections to the CouchDB database.

    TODO: Create views from fields in QueryType enum: https://docs.python.org/3/library/enum.html
    """

    def __init__(self):
        self.host = "localhost"
        self.port = "5984"
        self.server = Server("http://{}:{}".format(self.host, self.port))

        # Load or create database
        if 'precinct_db' not in self.server:
            self.db = self.server.create('precinct_db')
        else:
            self.db = self.server['precinct_db']

        # Load or create views.  See https://markhaa.se/couchdb-views-in-python.html
        vtd_by_census_logrecno = ViewDefinition("db_views", "vtd_by_census_logrecno",
                                                "function(doc) "
                                                "{if(doc.doctype == 'VTD') "
                                                "{emit(doc.census_LOGRECNO, "
                                                "doc._id)}}")
        vtd_by_census_logrecno.sync(self.db)
        vtd_by_census_county_cousub_vtd = ViewDefinition("db_views", "vtd_by_census_county_vtd",
                                                         "function(doc) "
                                                         "{if(doc.doctype =='VTD') "
                                                         "{emit([doc.census_COUNTY, "
                                                         "doc.census_COUSUB, doc.census_VTD], doc._id)}}")
        vtd_by_census_county_cousub_vtd.sync(self.db)

    def get_db(self):
        """Return CouchDB database object."""
        return self.db

class QueryType(Enum):
    """Query types, for use loading objects from the DB."""

    VTD_BY_CENSUS_LOGRECNO = "db_views/vtd_by_census_logrecno"
    VTD_BY_CENSUS_COUNTY_COUSUB_VTD = "db_views/vtd_by_census_county_vtd"

if __name__ == "__main__":
    print("Reinitializing database.")
    _DATABASE = Database()
