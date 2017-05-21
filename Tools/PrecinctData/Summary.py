"""Computes and prints county summaries."""

from collections import defaultdict

from Database import Database, QueryType
from ElectionResult import ElectionResult
from VTD import VTD
from PrecinctCodeMap import PrecinctCodeMap

class Summary(object):
    """Calculate summaries for a given range of EDs."""

    DATABASE = Database().get_db()

    def __init__(self):
        pass

    @staticmethod
    def generate(querytype, key):
        """Generate summary."""

        NestedDict = lambda: defaultdict(NestedDict)
        cache = NestedDict()

        vtds = VTD.load_vtds_from_db(querytype, key)
        # Nassau county for debugging only
        for vtd in vtds:
            county, precinct = PrecinctCodeMap.county_precinct_from_vtd(vtd)
            ers = ElectionResult.load_ers_from_db(QueryType.ER_BY_COUNTY_PRECINCT,
                                                  [county, precinct])




if __name__ == "__main__":
    Summary.generate(QueryType.VTD_BY_CENSUS_COUNTY, 59)
