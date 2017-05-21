"""A class to map OE precinct codes (e.g. Nassau GC  13  001) with VTDs."""

from VTD import VTD
from FIPS import NY_STATE_COUNTIES

class PrecinctCodeMap(object):

    def __init__(self):
        pass

    @staticmethod
    def county_precinct_from_vtd(vtd):
        if not isinstance(vtd, VTD):
            raise TypeError("Argument to er_code_from_vtd() must be VTD.")
        if vtd.census_COUNTY in [5, 47, 61, 81, 85, 59]:
            # Nassau County and 5 boroughs of NYC
            return ADBasedPrecinctCodeMap.county_precinct_from_vtd(vtd)
        else:
            return WardBasedPrecinctCodeMap.county_precinct_from_vtd(vtd)


class ADBasedPrecinctCodeMap(PrecinctCodeMap):
    """Used in Nassau county and 5 boroughs of NYC."""

    @staticmethod
    def county_precinct_from_vtd(vtd):
        county = NY_STATE_COUNTIES[vtd.census_COUNTY]




        return county, precinct

class WardBasedPrecinctCodeMap(PrecinctCodeMap):
    """Used in all other counties in NY."""

    @staticmethod
    def county_precinct_from_vtd(vtd):
        county = NY_STATE_COUNTIES[vtd.census_COUNTY]



        return county, precinct
