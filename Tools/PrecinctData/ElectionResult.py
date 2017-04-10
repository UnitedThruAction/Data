"""Load precinct-level election results from the OpenElections Project
(http://www.openelections.net), the first free, comprehensive, standardized,
linked set of election data for the United States, including federal and
statewide offices.

Download New York files into DIRNAME from
https://github.com/openelections/openelections-data-ny
"""

from couchdb.mapping import Document, TextField, IntegerField, DateField

from Database import Database, QueryType


class ElectionResult(Document):
    """Precinct-level election result form OpenElections."""

    DIRNAME = "/Users/nick/Dev/Git/openelections-data-ny"
    DATABASE = Database().get_db()

    doctype = TextField()

    oe_election_date = DateField()
    oe_state = TextField()
    oe_county_name = TextField()
    oe_county_fips = IntegerField()

    oe_precinct = TextField()
    oe_office = TextField()
    oe_district = TextField()
    oe_party = TextField()
    oe_candidate = TextField()
    oe_votes = IntegerField()
    oe_public_counter_votes = IntegerField()
    oe_emergency_votes = IntegerField()
    oe_absentee_military_votes = IntegerField()
    oe_federal_votes = IntegerField()
    oe_affidavit_votes = IntegerField()
    oe_manually_counted_emergency = IntegerField()
    oe_special_presidential = IntegerField()
