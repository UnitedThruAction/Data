"""Computes and outputs district summaries."""

from collections import Counter

from Database import Database, QueryType
from ElectionDistrict import ElectionDistrict
from FIPS import NY_STATE_COUNTIES
from VTD import VTD

class Summary(object):
    """Calculate summaries for a given range of EDs."""

    DATABASE = Database().get_db()

    def __init__(self, district_type, district_num):
        print("Generating summary for district type {},"
              " district num {}".format(district_type, district_num))

        # Load election districts, with voter registration numbers etc.
        ed_list, counties = [], {}
        if district_type.upper() == "STATE SENATE":
            querytype = QueryType.ED_BY_SD.value
        elif district_type.upper() == "STATE ASSEMBLY":
            querytype = QueryType.ED_BY_AD.value
        else:
            raise ValueError("Provide valid district_type")
        key = district_num
        ed_uuids = [doc.value for doc in Summary.DATABASE.view(querytype)[key]]
        for uuid in ed_uuids:
            doc = ElectionDistrict.load(Summary.DATABASE, uuid)
            ed_list.append(doc.to_dict())
            counties[doc.vf_countyname] = True

        # Load VTDs and map to EDs
        fips_code_lookup = {v:k for k, v in NY_STATE_COUNTIES.values()}
        county_codes = [fips_code_lookup[county_name] for county_name in counties.keys()]
        querytype = QueryType.VTD_BY_CENSUS_COUNTY # not value
        vtds = []
        for county_code in county_codes:
            vtds.append(VTD.load_vtds_from_db(querytype, county_code))
        vtd_results = []
        for vtd in vtds:
            vtd_summary = Counter()
            for vtd_ed_sub in vtd.boe_eds:
                for ed in ed_list:
                    # HUGE FLASHING WARNING
                    #
                    # This only works for
                    if (NY_STATE_COUNTIES[vtd.census_COUNTY] == ed.vf_countyname) \
                        and (((vtd_ed_sub.ad == ed.vf_ad_number) and (vtd_ed_sub.ed == ed.vf_ed_number)) \
                        or ((vtd_ed_sub.ward == ed.vf_ward_character) and (vtd_ed_sub.ed == ed.vf_ed_number))):




                if precinct_code in denominator.index.get_level_values(1): # in Senate District 31
                    in_district = True
                    vtd_result += Counter(denominator.loc['New York', precinct_code].to_dict()) # add voter registration
                if precinct_code in primary.index.get_level_values(1):
                    vtd_result += Counter(primary.loc['New York', precinct_code].to_dict()) # add primary data
            if in_district:
                vtd_result = dict(vtd_result)
                vtd_result.update(vtd.to_dict()) # get Census data
                vtd_result['Geoid10'] = "{:02.0f}{:03.0f}{:.0f}".format(vtd_result['census_STATE'],
                                                                        vtd_result['census_COUNTY'],
                                                                        vtd_result['census_VTD'])
                vtd_result['boe_eds'] = ", ".join(["AD {} ED {}".format(dct['ad'], dct['ed']) for dct in vtd_result['boe_eds']])
                results.append(vtd_result)

        # Load relevant results
