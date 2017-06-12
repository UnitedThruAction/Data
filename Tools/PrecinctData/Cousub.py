"""Class to represent the COUSUB (COUnty SUBdivision) level of the Census,
used in the naming convention for Election Districts in some counties.

"""

from couchdb.mapping import Document, TextField, IntegerField

from Database import Database, QueryType

class Cousub(Document):
    """COUnty SUBdivisions from the 2010 Census."""

    DIRNAME = "/Users/nick/Downloads"
    DATABASE = Database().get_db()

    doctype = TextField()

    census_LOGRECNO = IntegerField()
    census_STATE = IntegerField()
    census_COUNTY = IntegerField()
    census_COUSUB = IntegerField()
    census_NAME = TextField()

    @staticmethod
    def load_cousubs_from_file(overwrite=True):
        """Load VTDs into database from NY BoE files.
        See https://www.census.gov/prod/cen2010/doc/pl94-171.pdf, p.2-22
        """

        filename = "".join([Cousub.DIRNAME, "/ny2010/nygeo2010.pl"])
        filehandle = open(filename, "r")
        for line in filehandle:
            # State-County-Voting District/Remainder-County Subdivision
            census_SUMLEV = int(line[8:11].rstrip().lstrip())
            if census_SUMLEV == 60: # COUSUB
                # Logical Record Number
                census_LOGRECNO = int(line[18:25].rstrip().lstrip())
                # FIPS State
                census_STATE = int(line[27:29].rstrip().lstrip())
                # FIPS County
                census_COUNTY = int(line[29:32].rstrip().lstrip())
                # FIPS County Subdivision
                census_COUSUB = int(line[36:41].rstrip().lstrip())
                # Area Name-Legal/Statistical Area Description (LSAD) Term-Part
                # Indicator
                census_NAME = line[226:316].rstrip().lstrip()

                try:
                    cousubs = Cousub.load_cousubs_from_db(QueryType.COUSUB_BY_CENSUS_LOGRECNO, census_LOGRECNO)
                    if overwrite:
                        for cousub in cousubs:
                            cousub.doctype = "Cousub"
                            cousub.census_LOGRECNO = census_LOGRECNO
                            cousub.census_STATE = census_STATE
                            cousub.census_COUNTY = census_COUNTY
                            cousub.census_COUSUB = census_COUSUB
                            cousub.census_NAME = census_NAME
                            cousub.store(Cousub.DATABASE)
                except ValueError:
                    new_cousub = Cousub(doctype="Cousub",
                                        census_LOGRECNO=census_LOGRECNO,
                                        census_STATE=census_STATE,
                                        census_COUNTY=census_COUNTY,
                                        census_COUSUB=census_COUSUB,
                                        census_NAME=census_NAME)
                    new_cousub.store(Cousub.DATABASE)

        filehandle.close()

    @staticmethod
    def load_cousubs_from_db(query_type, key):
        """Get a VTD from the DB via a query."""

        if not isinstance(query_type, QueryType):
            raise ValueError("Must provide a QueryType Enum")
        uuids = [doc.value for doc in Cousub.DATABASE.view(query_type.value)[key]]
        if len(uuids) == 0:
            raise ValueError("No docs returned: {}, key {}"
                             .format(query_type, key))
        return [Cousub.load(Cousub.DATABASE, uuid) for uuid in uuids]

    @staticmethod
    def get_cousub_name(county, cousub):
        cousubs = Cousub.load_cousubs_from_db(QueryType.COUSUB_BY_COUNTY_COUSUB,
                                              [county, cousub])
        if len(cousubs) > 1:
            raise ValueError("More than one COUSUB returned for county {},"
                             " cousub {}".format(county, cousub))
        else:
            cousub = cousubs[0]
            return cousub.census_NAME

    @staticmethod
    def main():
        print("Loading basic COUSUBs from files.")
        Cousub.load_cousubs_from_file()

    def to_dict(self):
        """Convert VTD to dict for use with Pandas.
        TODO: Make this less horrible.  self.__dict__ doesn't work."""

        temp_dict = {}
        temp_dict['census_LOGRECNO'] = self.census_LOGRECNO
        temp_dict['census_STATE'] = self.census_STATE
        temp_dict['census_COUNTY'] = self.census_COUNTY
        temp_dict['census_COUSUB'] = self.census_COUSUB
        temp_dict['census_NAME'] = self.census_NAME

        return temp_dict


if __name__ == "__main__":
    Cousub.main()
