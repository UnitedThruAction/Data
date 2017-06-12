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

    @staticmethod
    def main():
        print("Reinitializing database objects.")
        _DATABASE = Database()

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

        doc_by_class = ViewDefinition("db_views", "doc_by_class",
                                      "function(doc) "
                                      "{emit(doc.doctype, doc._id)}")
        doc_by_class.sync(self.db)

        vtd_by_census_logrecno = ViewDefinition("db_views", "vtd_by_census_logrecno",
                                                "function(doc) "
                                                "{if(doc.doctype == 'VTD') "
                                                "{emit(doc.census_LOGRECNO, "
                                                "doc._id)}}")
        vtd_by_census_logrecno.sync(self.db)

        vtd_by_census_county = ViewDefinition("db_views", "vtd_by_census_county",
                                              "function(doc) "
                                              "{if(doc.doctype =='VTD') "
                                              "{emit(doc.census_COUNTY, doc._id)}}")
        vtd_by_census_county.sync(self.db)

        vtd_by_census_county_cousub_vtd = ViewDefinition("db_views", "vtd_by_census_county_cousub_vtd",
                                                         "function(doc) "
                                                         "{if(doc.doctype =='VTD') "
                                                         "{emit([doc.census_COUNTY, "
                                                         "doc.census_COUSUB, doc.census_VTD], doc._id)}}")
        vtd_by_census_county_cousub_vtd.sync(self.db)

        er_by_county_precinct = ViewDefinition("db_views", "er_by_county_precinct",
                                               "function(doc) "
                                               "{if(doc.doctype == 'ElectionResult') "
                                               "{emit([doc.oe_county_name, "
                                               "doc.oe_precinct], doc._id)}}")
        er_by_county_precinct.sync(self.db)

        er_by_date_office_district = ViewDefinition("db_views", "er_by_date_office_district",
                                                    "function(doc) "
                                                    "{if(doc.doctype == 'ElectionResult') "
                                                    "{emit([doc.oe_election_date, doc.oe_office, doc.oe_district], doc._id)}}")

        er_by_date_office_district.sync(self.db)


        er_by_date_state_election_county_precinct_office_district_party_candidate = ViewDefinition("db_views", "er_by_date_state_election_county_precinct_office_district_party_candidate",
                                                                                                   "function(doc) "
                                                                                                   "{if(doc.doctype == 'ElectionResult') "
                                                                                                   "{emit([doc.oe_election_date, doc.oe_state, doc.oe_election_name, "
                                                                                                   "doc.oe_county_name, doc.oe_precinct, doc.oe_office, doc.oe_district, doc.oe_party, doc.oe_candidate], doc._id)}}")
        er_by_date_state_election_county_precinct_office_district_party_candidate.sync(self.db)

        ed_by_county_edcode = ViewDefinition("db_views", "ed_by_county_edcode",
                                             "function(doc) "
                                             "{if(doc.doctype == 'ElectionDistrict') "
                                             "{emit([doc.vf_countyname, doc.vf_ed_code], doc._id)}}")
        ed_by_county_edcode.sync(self.db)

        ed_by_ad = ViewDefinition("db_views", "ed_by_ad",
                                  "function(doc) "
                                  "{if(doc.doctype == 'ElectionDistrict') "
                                  "{emit(doc.vf_ad_number, doc._id)}}")
        ed_by_ad.sync(self.db)

        ed_by_sd = ViewDefinition("db_views", "ed_by_sd",
                                  "function(doc) "
                                  "{if(doc.doctype == 'ElectionDistrict') "
                                  "{emit(doc.vf_sd_number, doc._id)}}")
        ed_by_sd.sync(self.db)

        cousub_by_census_logrecno = ViewDefinition("db_views", "cousub_by_census_logrecno",
                                                   "function(doc) "
                                                   "{if(doc.doctype == 'Cousub') "
                                                   "{emit(doc.census_LOGRECNO, doc._id)}}")
        cousub_by_census_logrecno.sync(self.db)

        cousub_by_county_cousub = ViewDefinition("db_views", "cousub_by_county_cousub",
                                                 "function(doc) "
                                                 "{if(doc.doctype == 'Cousub') "
                                                 "{emit([doc.census_COUNTY, doc.census_COUSUB], doc._id)}}")
        cousub_by_county_cousub.sync(self.db)

    def get_db(self):
        """Return CouchDB database object."""
        return self.db

    def delete_by_class(self, doctype):
        docs = self.db.view(QueryType.DOC_BY_CLASS.value)[doctype]
        for doc in docs:
            del self.db[doc]

class QueryType(Enum):
    """Query types, for use loading objects from the DB."""

    DOC_BY_CLASS = "db_views/doc_by_class"
    VTD_BY_CENSUS_LOGRECNO = "db_views/vtd_by_census_logrecno"
    VTD_BY_CENSUS_COUNTY = "db_views/vtd_by_census_county"
    VTD_BY_CENSUS_COUNTY_COUSUB_VTD = "db_views/vtd_by_census_county_cousub_vtd"
    ER_BY_COUNTY_PRECINCT = "db_views/er_by_county_precinct"
    ER_BY_DATE_OFFICE_DISTRICT = "db_views/er_by_date_office_district"
    ER_BY_DATE_STATE_ELECTION_COUNTY_PRECINCT_OFFICE_DISTRICT_PARTY_CANDIDATE = "db_views/er_by_date_state_election_county_precinct_office_district_party_candidate"
    ED_BY_COUNTY_EDCODE = "db_views/ed_by_county_edcode"
    ED_BY_AD = "db_views/ed_by_ad"
    ED_BY_SD = "db_views/ed_by_sd"
    COUSUB_BY_CENSUS_LOGRECNO = "db_views/cousub_by_census_logrecno"
    COUSUB_BY_COUNTY_COUSUB = "db_views/cousub_by_county_cousub"

if __name__ == "__main__":
    Database.main()
