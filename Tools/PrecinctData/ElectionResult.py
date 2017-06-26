"""Load precinct-level election results from the OpenElections Project
(http://www.openelections.net), the first free, comprehensive, standardized,
linked set of election data for the United States, including federal and
statewide offices.

Download New York files into DIRNAME from
https://github.com/openelections/openelections-data-ny

"""

import csv
import os
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
    oe_public_counter_votes = IntegerField()  # total in that precinct
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
        m = re.search(
            r"(\d{8})__(\w{2})__(.*)__(\w+)__precinct\.csv",
            filename)
        if m:
            oe_election_date = date(int(m.group(1)[0:4]),
                                    int(m.group(1)[4:6]),
                                    int(m.group(1)[6:8]))
            oe_state = m.group(2).upper()
            oe_election_name = m.group(3).replace("__", " ").title()
            oe_county_name = m.group(4).replace("_", " ").title()
        else:
            raise TypeError("Filename does not match precinct type.")

        # Read CSV
        with open(filename) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['county'] != oe_county_name:
                    raise ValueError(
                        "Mismatch of county name in file {}".format(filename))
                if 'Total' in row[
                        'precinct']:  # e.g. 'Total for Babylon' instead of 'Babylon #: 154'
                    continue
                oe_precinct = row['precinct'] if 'precinct' in row else ""
                oe_office = row['office'] if 'office' in row else ""
                oe_district = row['district'] if 'district' in row else ""
                oe_party = row['party'] if 'party' in row else ""
                oe_candidate = row['candidate'] if 'candidate' in row else ""
                oe_votes = ElectionResult.safeint(row, 'votes')
                oe_public_counter_votes = ElectionResult.safeint(
                    row, 'public_counter_votes')
                oe_emergency_votes = ElectionResult.safeint(
                    row, 'emergency_votes')
                oe_absentee_military_votes = ElectionResult.safeint(
                    row, 'absentee_military_votes')
                oe_federal_votes = ElectionResult.safeint(row, 'federal_votes')
                oe_affidavit_votes = ElectionResult.safeint(
                    row, 'affidavit_votes')
                oe_manually_counted_emergency = ElectionResult.safeint(
                    row, 'manually_counted_emergency')
                oe_special_presidential = ElectionResult.safeint(
                    row, 'special_presidential')

                # Get ID if already exists; then save if appropriate
                # TODO: Refactor this to use load_ers_from_db() method
                querytype = QueryType.ER_BY_DATE_STATE_ELECTION_COUNTY_PRECINCT_OFFICE_DISTRICT_PARTY_CANDIDATE.value
                key = [
                    str(oe_election_date),
                    oe_state,
                    oe_election_name,
                    oe_county_name,
                    oe_precinct,
                    oe_office,
                    oe_district,
                    oe_party,
                    oe_candidate]
                uuids = [doc.value for doc in ElectionResult.DATABASE.view(querytype)[
                    key]]
                if len(uuids) == 0:
                    # New doc
                    new_er = ElectionResult(
                        doctype="ElectionResult",
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

    @staticmethod
    def safeint(row, key):
        """Safely return an integer without tripping over KeyErrors."""
        if (key in row) and row[key]:
            return int(row[key])
        else:
            return 0

    @staticmethod
    def load_ers_from_db(query_type, key):
        """Get ERs from the DB via a query."""

        if not isinstance(query_type, QueryType):
            raise ValueError("Must provide a QueryType Enum")
        uuids = [
            doc.value for doc in ElectionResult.DATABASE.view(
                query_type.value)[key]]
        if len(uuids) == 0:
            raise ValueError("No docs returned: {}, key {}"
                             .format(query_type, key))
        return [
            ElectionResult.load(
                ElectionResult.DATABASE,
                uuid) for uuid in uuids]

    @staticmethod
    def load_files_by_regexp(regexp):
        """Load OE files based on regexp."""

        path = ElectionResult.DIRNAME
        for root, _dirs, files in os.walk(path):
            for filename in files:
                filepath = os.path.join(root, filename)
                if re.search(regexp, filepath):
                    ElectionResult.load_single_file(filepath)

    @staticmethod
    def main():
        print("Loading Election Result files.")
        # ElectionResult.load_files_by_regexp(".*2016.*(nassau|suffolk)__precinct.csv")
        ElectionResult.load_files_by_regexp(".*suffolk__precinct.csv")

    def to_dict(self):
        """Convert ER to dict for use with Pandas.
        TODO: Make this less horrible.  self.__dict__ doesn't work."""

        temp_dict = {}
        temp_dict['oe_election_date'] = self.oe_election_date
        temp_dict['oe_state'] = self.oe_state
        temp_dict['oe_election_name'] = self.oe_election_name
        temp_dict['oe_county_name'] = self.oe_county_name

        temp_dict['oe_precinct'] = self.oe_precinct
        temp_dict['oe_office'] = self.oe_office
        temp_dict['oe_district'] = self.oe_district
        temp_dict['oe_party'] = self.oe_party
        temp_dict['oe_candidate'] = self.oe_candidate
        temp_dict['oe_votes'] = self.oe_votes
        # total in that precinct
        temp_dict['oe_public_counter_votes'] = self.oe_public_counter_votes
        temp_dict['oe_emergency_votes'] = self.oe_emergency_votes
        temp_dict['oe_absentee_military_votes'] = self.oe_absentee_military_votes
        temp_dict['oe_federal_votes'] = self.oe_federal_votes
        temp_dict['oe_affidavit_votes'] = self.oe_affidavit_votes
        temp_dict[
            'oe_manually_counted_emergency'] = self.oe_manually_counted_emergency
        temp_dict['oe_special_presidential'] = self.oe_special_presidential

        return temp_dict

if __name__ == "__main__":
    ElectionResult.main()
