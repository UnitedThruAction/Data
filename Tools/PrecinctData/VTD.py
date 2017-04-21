"""Class to represent Voting Tabulation Districts (VTDs) from the 2010 Census,
Vote and Enrollment Data from the NY State Board of Elections website.

See http://www.latfor.state.ny.us/data/
Download files and extract into DIRNAME.

TODO:
    -

"""
import os
import re
from collections import defaultdict

from couchdb.mapping import Document, TextField, IntegerField, BooleanField, ListField

from Database import Database, QueryType


class VTD(Document):
    """VTD from the 2010 Census, Vote and Enrollment Data."""

    DIRNAME = "/Users/nick/Downloads"
    DATABASE = Database().get_db()

    doctype = TextField()

    census_LOGRECNO = IntegerField()
    census_STATE = IntegerField()
    census_COUNTY = IntegerField()
    census_COUSUB = IntegerField()
    census_CBSA = IntegerField()
    census_METDIV = IntegerField()
    census_CSA = IntegerField()
    census_SLDL = IntegerField()
    census_VTD = IntegerField()
    census_VTDI = TextField()
    census_NAME = TextField()
    census_INTPTLAT = TextField()
    census_INTPTLON = TextField()
    census_LSADC = TextField()

    boe_ward = IntegerField()
    boe_assembly_district = IntegerField()
    boe_election_district = IntegerField()
    boe_district_code = TextField()
    boe_part_district = BooleanField()

    census_P1_RACE = ListField(IntegerField())
    census_P2_HISPANIC = ListField(IntegerField())
    census_P3_RACE_18OVER = ListField(IntegerField())
    census_P4_HISPANIC_18OVER = ListField(IntegerField())
    census_H1_OCCUPANCY = ListField(IntegerField())

    @staticmethod
    def load_vtds_from_file():
        """Load VTDs into database from NY BoE files.
        See https://www.census.gov/prod/cen2010/doc/pl94-171.pdf, p.2-22

        TODO: Make this idempotent by using a CreateOrUpdate method.
        """

        filename = "".join([VTD.DIRNAME, "/ny2010/nygeo2010.pl"])
        filehandle = open(filename, "r")
        for line in filehandle:
            # State-County-Voting District/Remainder-County Subdivision
            census_SUMLEV = int(line[8:11].rstrip().lstrip())
            if census_SUMLEV == 710:
                # Logical Record Number
                census_LOGRECNO = int(line[18:25].rstrip().lstrip())

                # FIPS State
                census_STATE = int(line[27:29].rstrip().lstrip())
                # FIPS County
                census_COUNTY = int(line[29:32].rstrip().lstrip())
                # FIPS County Subdivision
                census_COUSUB = int(line[36:41].rstrip().lstrip())
                # Metropolitan Statistical Area/Micropolitan Statistical Area
                census_CBSA = int(line[112:117].rstrip().lstrip())
                # Metropolitan Division
                census_METDIV = int(line[119:124].rstrip().lstrip())
                # Combined Statistical Area
                census_CSA = int(line[124:127].rstrip().lstrip())

                # Voting District
                census_VTD = int(line[161:167].rstrip().lstrip())
                # Voting District Indicator
                census_VTDI = line[167:168].rstrip().lstrip()

                # Area Name-Legal/Statistical Area Description (LSAD) Term-Part
                # Indicator
                census_NAME = line[226:316].rstrip().lstrip()
                # Internal Point (Latitude)
                census_INTPTLAT = line[336:347].rstrip().lstrip()
                # Internal Point (Longitude)
                census_INTPTLON = line[347:359].rstrip().lstrip()
                # Legal/Statistical Area Description Code
                census_LSADC = line[359:361].rstrip().lstrip()

                new_vtd = VTD(doctype="VTD",
                              census_LOGRECNO=census_LOGRECNO,
                              census_STATE=census_STATE,
                              census_COUNTY=census_COUNTY,
                              census_COUSUB=census_COUSUB,
                              census_CBSA=census_CBSA,
                              census_METDIV=census_METDIV,
                              census_CSA=census_CSA,
                              census_VTD=census_VTD,
                              census_VTDI=census_VTDI,
                              census_NAME=census_NAME,
                              census_INTPTLAT=census_INTPTLAT,
                              census_INTPTLON=census_INTPTLON,
                              census_LSADC=census_LSADC)
                new_vtd.store(VTD.DATABASE)
        filehandle.close()

    @staticmethod
    def load_vtd_ed_equivalents():
        """Load VTD-ED equivalents.
        See http://www.latfor.state.ny.us/data/?sec=2010equiv.

        For each State/County, maps Census (COUSUB, VTD) ->
                Election Board (Ward or AD, ED)
        """

        path = "".join([VTD.DIRNAME, "/REDIST_EQUIV"])
        for root, _dirs, files in os.walk(path):
            for filename in files:
                if "csv" in filename:
                    filepath = os.path.join(root, filename)
                    filehandle = open(filepath, "r")
                    line_num = 0
                    file_type = None
                    for line in filehandle:
                        if line_num == 0:
                            # Header row
                            if "WARD" in line:
                                file_type = "WARD"
                            elif "AD" in line:
                                file_type = "AD"
                            else:
                                raise TypeError(
                                    "Unknown file type: {}".format(filepath))
                        else:
                            # Data row
                            line = re.sub("\"", "", line)
                            cols = line.split(",")
                            if len(cols) != 7:
                                raise ValueError(
                                    "File {} line {} has invalid number of columns {}" .format(
                                        filepath, line_num, len(cols)))
                            county, cousub, ward_ad, ed, vtd08 = cols[2:7]
                            try:
                                vtds = VTD.load_vtds_from_db(
                                    QueryType.VTD_BY_CENSUS_COUNTY_COUSUB_VTD, [
                                        int(county), int(cousub), int(vtd08)])
                                for vtd in vtds:
                                    if file_type == "WARD":
                                        vtd.boe_ward = int(ward_ad)
                                    elif file_type == "AD":
                                        vtd.boe_assembly_district = int(ward_ad)
                                    vtd.boe_election_district = int(ed)
                                    vtd.boe_part_district = bool(len(vtds) > 1)
                                    vtd.store(VTD.DATABASE)
                            except ValueError as err:
                                print("Non-fatal exception: {}".format(err))

                        line_num += 1
                    filehandle.close()

    @staticmethod
    def load_additional_census_data():
        """Load additional census data from Census 2010 files.  See p.6-21."""

        cache = defaultdict(dict)

        # Cache data from file 1
        filename = "".join([VTD.DIRNAME, "/ny2010/ny000012010.pl"])
        filehandle = open(filename, "r")
        for line in filehandle:
            cols = line.split(",")
            logrecno = int(cols[4])
            p1_race = [int(i) for i in cols[5:76]]
            p2_hispanic = [int(i) for i in cols[76:149]]
            cache[logrecno]["p1"] = p1_race
            cache[logrecno]["p2"] = p2_hispanic
        filehandle.close()

        # Cache data from file 2
        filename = "".join([VTD.DIRNAME, "/ny2010/ny000022010.pl"])
        filehandle = open(filename, "r")
        for line in filehandle:
            cols = line.split(",")
            logrecno = int(cols[4])
            p3_race18older = [int(i) for i in cols[5:76]]
            p4_hispanic18older = [int(i) for i in cols[76:149]]
            h1_occupancy = [int(i) for i in cols[149:152]]
            cache[logrecno]["p3"] = p3_race18older
            cache[logrecno]["p4"] = p4_hispanic18older
            cache[logrecno]["h1"] = h1_occupancy
        filehandle.close()

        # Store in DB
        for doc in VTD.DATABASE.view(QueryType.VTD_BY_CENSUS_LOGRECNO.value):
            vtd = VTD.load(VTD.DATABASE, doc.value)
            vtd.census_P1_RACE = cache[vtd.census_LOGRECNO]["p1"]
            vtd.census_P2_HISPANIC = cache[vtd.census_LOGRECNO]["p2"]
            vtd.census_P3_RACE_18OVER = cache[vtd.census_LOGRECNO]["p3"]
            vtd.census_P4_HISPANIC_18OVER = cache[vtd.census_LOGRECNO]["p4"]
            vtd.census_H1_OCCUPANCY = cache[vtd.census_LOGRECNO]["h1"]
            vtd.store(VTD.DATABASE)

        del cache

    @staticmethod
    def load_vtds_from_db(query_type, key):
        """Get a VTD from the DB via a query."""

        if not isinstance(query_type, QueryType):
            raise ValueError("Must provide a QueryType Enum")
        uuids = [doc.value for doc in VTD.DATABASE.view(query_type.value)[key]]
        if len(uuids) == 0:
            raise ValueError("No docs returned: {}, key {}"
                             .format(query_type, key))
        return [VTD.load(VTD.DATABASE, uuid) for uuid in uuids]

if __name__ == "__main__":
    print("Loading basic VTDs from files.")
    VTD.load_vtds_from_file()
    print("Loading VTD/ED equivalents.")
    VTD.load_vtd_ed_equivalents()
    print("Loading additional census data.")
    VTD.load_additional_census_data()
