"""Computes and prints county summaries."""

class CountySummary(object):
    """Calculate summaries for a given county."""

    def __init__(self, county_fips):
        self.county_fips = county_fips

    def generate(self):
        """Generate summary."""

        # Get all ElectionResults for this county and collapse to one record per ED.


        # Parse ED precinct codes (using county-specific rule) to look up VTDs.


        # Summarize down further to one row per VTD.


        # Output.



    @staticmethod
    def main():
        pass

if __name__ == "__main__":
    CountySummary.main()
