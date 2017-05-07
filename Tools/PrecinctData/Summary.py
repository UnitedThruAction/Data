"""Computes and prints county summaries."""

from collections import defaultdict

from Database import Database, QueryType
from ElectionResult import ElectionResult

class Summary(object):
    """Calculate summaries for a given range of EDs."""

    DATABASE = Database().get_db()

    def __init__(self):
        pass

    def generate(self):
        """Generate summary."""

        NestedDict = lambda: defaultdict(NestedDict)
        cache = NestedDict()

        # Get all ElectionResults for this county and collapse to one record per ED.
        # We deliberately want to collapse in time.
        querytype = QueryType.ER_BY_COUNTY_PRECINCT
        for doc in Summary.DATABASE.view(querytype.value):
            oe_county_name, oe_precinct = doc.key
            er = ElectionResult.load(Summary.DATABASE, doc.value)
            cache[oe_county_name][oe_precinct][er.oe_election_date][er.oe_office][er.oe_party] 
            # Need cache of shape county - precinct - date - office - party

        # Parse ED precinct codes (using county-specific rule) to look up VTDs.


        # Summarize down further to one row per VTD.


        # Output.



    @staticmethod
    def main():
        pass

if __name__ == "__main__":
    Summary.main()
