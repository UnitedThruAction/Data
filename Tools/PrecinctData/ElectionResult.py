"""Load precinct-level election results from the OpenElections Project
(http://www.openelections.net), the first free, comprehensive, standardized,
linked set of election data for the United States, including federal and
statewide offices.

Download New York files into DIRNAME from
https://github.com/openelections/openelections-data-ny

"""

import csv
import re
from datetime import date
from couchdb.mapping import Document, TextField, IntegerField, DateField

from Database import Database, QueryType


class ElectionResult(Document):
    """Precinct-level election result form OpenElections."""

    DIRNAME = "/Users/nick/Dev/Git/openelections-data-ny"
    DATABASE = Database().get_db()

    doctype = TextField()

    oe_election_date = DateField()
    oe_state = TextField()
    oe_election_name = TextField()
    oe_county_name = TextField()

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


    @staticmethod
    def load_single_file(filename, overwrite=False):
        """Load precinct data from a single file into DB without translation."""

        print("Loading file {}".format(filename))
        # Parse data from name
        m = re.search(r"(\d{8})__(\w{2})__(.*)__(\w+)__precinct\.csv", filename)
        if m:
            oe_election_date = date(int(m.group(1)[0:4]),
                                    int(m.group(1)[4:6]),
                                    int(m.group(1)[6:8]))
            oe_state = m.group(2).upper()
            oe_election_name = m.group(3).replace("__", " ").title()
            oe_county_name = m.group(4).title()
        else:
            raise TypeError("Filename does not match precinct type.")

        # Read CSV
        with open(filename) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['county'] != oe_county_name:
                    raise ValueError("Mismatch of county name in file {}".format(filename))
                oe_precinct = row['precinct'] if 'precinct' in row else ""
                oe_office = row['office'] if 'office' in row else ""
                oe_district = row['district'] if 'district' in row else ""
                oe_party = row['party'] if 'party' in row else ""
                oe_candidate = row['candidate'] if 'candidate' in row else ""
                oe_votes = int(row['votes']) if 'votes' in row else 0
                oe_public_counter_votes = int(row['public_counter_votes']) if 'public_counter_votes' in row else 0
                oe_emergency_votes = int(row['emergency_votes']) if 'emergency_votes' in row else 0
                oe_absentee_military_votes = int(row['absentee_military_votes']) if 'absentee_military_votes' in row else 0
                oe_federal_votes = int(row['federal_votes']) if 'federal_votes' in row else 0
                oe_affidavit_votes = int(row['affidavit_votes']) if 'affidavit_votes' in row else 0
                oe_manually_counted_emergency = int(row['manually_counted_emergency']) if 'manually_counted_emergency' in row else 0
                oe_special_presidential = int(row['special_presidential']) if 'special_presidential' in row else 0

                # Get ID if already exists; then save if appropriate
                querytype = QueryType.ER_BY_DATE_STATE_ELECTION_COUNTY_PRECINCT.value
                key = [str(oe_election_date), oe_state, oe_election_name, oe_county_name, oe_precinct]
                uuids = [doc.value for doc in ElectionResult.DATABASE.view(querytype)[key]]
                if len(uuids) == 0:
                    # New doc
                    new_er = ElectionResult(doctype="ElectionResult",
                                            oe_election_date=oe_election_date,
                                            oe_state=oe_state,
                                            oe_election_name=oe_election_name,
                                            oe_county_name=oe_county_name,
                                            oe_precinct=oe_precinct,
                                            oe_office=oe_office,
                                            oe_district=oe_district,
                                            oe_party=oe_party,
                                            oe_candidate=oe_candidate,
                                            oe_votes=oe_votes,
                                            oe_public_counter_votes=oe_public_counter_votes,
                                            oe_emergency_votes=oe_emergency_votes,
                                            oe_absentee_military_votes=oe_absentee_military_votes,
                                            oe_federal_votes=oe_federal_votes,
                                            oe_affidavit_votes=oe_affidavit_votes,
                                            oe_manually_counted_emergency=oe_manually_counted_emergency,
                                            oe_special_presidential=oe_special_presidential)
                    new_er.store(ElectionResult.DATABASE)
                elif overwrite:
                    for uuid in uuids:
                        er = ElectionResult.load(ElectionResult.DATABASE, uuid)
                        er.doctype = "ElectionResult"
                        er.oe_election_date = oe_election_date
                        er.oe_state = oe_state
                        er.oe_election_name = oe_election_name
                        er.oe_county_name = oe_county_name
                        er.oe_precinct = oe_precinct
                        er.oe_office = oe_office
                        er.oe_district = oe_district
                        er.oe_party = oe_party
                        er.oe_candidate = oe_candidate
                        er.oe_votes = oe_votes
                        er.oe_public_counter_votes = oe_public_counter_votes
                        er.oe_emergency_votes = oe_emergency_votes
                        er.oe_absentee_military_votes = oe_absentee_military_votes
                        er.oe_federal_votes = oe_federal_votes
                        er.oe_affidavit_votes = oe_affidavit_votes
                        er.oe_manually_counted_emergency = oe_manually_counted_emergency
                        er.oe_special_presidential = oe_special_presidential
                        er.store(ElectionResult.DATABASE)



if __name__ == "__main__":
    ElectionResult.load_single_file('/Users/nick/Dev/Git/openelections-data-ny/2016/20161108__ny__general__nassau__precinct.csv')
