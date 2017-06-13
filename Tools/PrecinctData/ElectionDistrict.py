"""Represents an actual New York State Election District, roughly equivalent
to a precinct.  Calculated by parsing the Voter File from the Board of
Elections."""

import os
import csv
import sys
from collections import defaultdict
from couchdb.mapping import Document, TextField, IntegerField, DictField

from Database import Database, QueryType
from FIPS import VOTER_FILE_COUNTIES


class ElectionDistrict(Document):
    """New York State Election District."""

    DIRNAME = "/Users/nick/Dev/Data/NY State Voter List 2017-03-27"
    FILENAME = "AllNYSVoters.txt"
    DATABASE = Database().get_db()

    doctype = TextField()

    vf_countyname = TextField()
    vf_ed_number = IntegerField()
    vf_ld_number = IntegerField()
    vf_towncity_character = TextField()
    vf_ward_character = TextField()
    vf_cd_number = IntegerField()
    vf_sd_number = IntegerField()
    vf_ad_number = IntegerField()

    # Election District code
    vf_ed_code = TextField()

    # Number of current, active registered voters
    vf_registration = DictField()

    # Elections which current, active voters have participated in
    vf_participation = DictField()

    @staticmethod
    def get_ed_code(countyname, towncity, ward, ad, ed):
        """Generate county-specific ED code from parameters.

        *** HUGE FLASHING WARNING ***
        Each county uses its own specific format.
        The first time you use this to match for a particular county, you'll
        need to contribute additional clauses here to make it work.

        """
        if countyname in ['Albany']:
            # e.g. "0009 ALBANY W1 ED9"
            # NB doesn't work - requires seq_no from somewhere
            seq_no = 0
            return "{} {} W{} ED{}".format(seq_no, towncity.upper(), ward, ed)
        if countyname in ['Nassau']:
            # e.g. "OB  09  016"
            return "{}  {:02.0f}  {:03.0f}".format(towncity, ad, ed)
        if countyname in ['Bronx', 'New York', 'Kings', 'Queens', 'Richmond']:
            # e.g. "001/67"
            return "{:03.0f}/{:02.0f}".format(ed, ad)
        if countyname in ['Suffolk']:
            # e.g. "Babylon #:  01"
            return "{} #: {:>3}".format(towncity.title(), "{:02.0f}".format(ed))
        else:
            return "Not yet implemented"

    @staticmethod
    def load_whole_voter_file(overwrite=True):
        """Load the whole voter file into the DB.  ~17 million rows"""
        #NestedDict = lambda: defaultdict(NestedDict)
        #cache = NestedDict()
        #cache[county][ed_code] ->
        #    [ed_number] = 2
        #    [registration] = {'DEM':3, 'REP':16, ...}
        #    [participation] = ['general2016':3, ...]
        cache = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(int))))

        # Cache data from CSV
        print("Caching data from Voter File.")
        rows_processed, rows_errors, elections = 0, 0, {}
        fieldnames = ['LASTNAME', 'FIRSTNAME', 'MIDDLENAME', 'NAMESUFFIX',
                      'RADDNUMBER', 'RHALFCODE', 'RAPARTMENT', 'RPREDIRECTION',
                      'RSTREETNAME', 'RPOSTDIRECTION', 'RCITY', 'RZIP5', 'RZIP4',
                      'MAILADD1', 'MAILADD2', 'MAILADD3', 'MAILADD4', 'DOB',
                      'GENDER', 'ENROLLMENT', 'OTHERPARTY', 'COUNTYCODE', 'ED',
                      'LD', 'TOWNCITY', 'WARD', 'CD', 'SD', 'AD', 'LASTVOTEDATE',
                      'PREVYEARVOTED', 'PREVCOUNTY', 'PREVADDRESS', 'PREVNAME',
                      'COUNTYVRNUMBER', 'REGDATE', 'VRSOURCE', 'IDREQUIRED',
                      'IDMET', 'STATUS', 'REASONCODE', 'INACT_DATE',
                      'PURGE_DATE', 'SBOEID', 'VoterHistory']

        with open(os.path.join(ElectionDistrict.DIRNAME,
                               ElectionDistrict.FILENAME),
                  newline='', encoding="Latin-1") as csvfile:
            reader = csv.DictReader(csvfile, fieldnames=fieldnames)
            for row in reader:
                if rows_processed % 100000 == 0:
                    print(".", end='') # progress indicator

                countyname = VOTER_FILE_COUNTIES[int(row['COUNTYCODE'])]
                vf_ed_code = ElectionDistrict.get_ed_code(countyname,
                                                          row['TOWNCITY'],
                                                          row['WARD'],
                                                          int(row['AD']),
                                                          int(row['ED']))
                district = cache[countyname][vf_ed_code]
                district['vf_ed_number'] = int(row['ED']) if row['ED'] else 0
                district['vf_ld_number'] = int(row['LD']) if row['LD'] else 0
                district['vf_towncity_character'] = row['TOWNCITY']
                district['vf_ward_character'] = row['WARD']
                district['vf_cd_number'] = int(row['CD']) if row['CD'] else 0
                district['vf_sd_number'] = int(row['SD']) if row['SD'] else 0
                district['vf_ad_number'] = int(row['AD']) if row['AD'] else 0
                district['vf_registration'][row['ENROLLMENT']] += 1
                for election in row['VoterHistory'].split(';'):
                    district['vf_participation'][election] += 1
                    elections[election] = True

                    #rows_errors += 1
                rows_processed += 1

            print("\nCompleted caching voter file.  "
                  "{} rows processed, {} errors".format(rows_processed, rows_errors))
            print("List of elections: {}".format(elections.keys()))

        # Save to DB
        eds_complete = 0
        print("Saving to database.")
        for countyname in cache:
            for vf_ed_code in cache[countyname]:
                if eds_complete % 1000 == 0:
                    print(".", end='')
                district = cache[countyname][vf_ed_code]
                querytype = QueryType.ED_BY_COUNTY_EDCODE.value
                key = [countyname, vf_ed_code]
                docs = ElectionDistrict.DATABASE.view(querytype)[key]
                if not docs:
                    # Create new doc
                    electiondistrict = ElectionDistrict(doctype='ElectionDistrict',
                                                        vf_countyname=countyname,
                                                        vf_ed_number=district['vf_ed_number'],
                                                        vf_ld_number=district['vf_ld_number'],
                                                        vf_towncity_character=district['vf_towncity_character'],
                                                        vf_ward_character=district['vf_ward_character'],
                                                        vf_cd_number=district['vf_cd_number'],
                                                        vf_sd_number=district['vf_sd_number'],
                                                        vf_ad_number=district['vf_ad_number'],
                                                        vf_ed_code=vf_ed_code,
                                                        vf_registration=district['vf_registration'],
                                                        vf_participation=district['vf_participation'])
                    electiondistrict.store(ElectionDistrict.DATABASE)
                elif overwrite:
                    # One or more ED by this code already exists in DB
                    for doc in docs:
                        electiondistrict = ElectionDistrict.load(ElectionDistrict.DATABASE, doc.value)
                        electiondistrict.doctype = 'ElectionDistrict'
                        electiondistrict.vf_countyname = countyname
                        electiondistrict.vf_ed_number = district['vf_ed_number']
                        electiondistrict.vf_ld_number = district['vf_ld_number']
                        electiondistrict.vf_towncity_character = district['vf_towncity_character']
                        electiondistrict.vf_ward_character = district['vf_ward_character']
                        electiondistrict.vf_cd_number = district['vf_cd_number']
                        electiondistrict.vf_sd_number = district['vf_sd_number']
                        electiondistrict.vf_ad_number = district['vf_ad_number']
                        electiondistrict.vf_ed_code = vf_ed_code
                        electiondistrict.vf_registration = district['vf_registration']
                        electiondistrict.vf_participation = district['vf_participation']
                        electiondistrict.store(ElectionDistrict.DATABASE)

                eds_complete += 1

        print("\nComplete.")

    @staticmethod
    def main():
        print("Loading Election District files.")
        ElectionDistrict.load_whole_voter_file()

    def to_dict(self):
        """Export to dict."""
        temp_dict = {}
        temp_dict['vf_countyname'] = self.vf_countyname
        temp_dict['vf_ed_number'] = self.vf_ed_number
        temp_dict['vf_ld_number'] = self.vf_ld_number
        temp_dict['vf_towncity_character'] = self.vf_towncity_character
        temp_dict['vf_ward_character'] = self.vf_ward_character
        temp_dict['vf_cd_number'] = self.vf_cd_number
        temp_dict['vf_sd_number'] = self.vf_sd_number
        temp_dict['vf_ad_number'] = self.vf_ad_number
        temp_dict['vf_ed_code'] = self.vf_ed_code
        temp_dict['vf_registration'] = self.vf_registration
        temp_dict['vf_participation'] = self.vf_participation
        return temp_dict

class Unbuffered(object):
    """A wrapper for stdout to unbuffer output on command line."""
    def __init__(self, stream):
        self.stream = stream

    def write(self, data):
        self.stream.write(data)
        self.stream.flush()

    def __getattr__(self, attr):
        return getattr(self.stream, attr)

if __name__ == "__main__":
    sys.stdout = Unbuffered(sys.stdout)
    ElectionDistrict.main()
