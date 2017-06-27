"""Computes and outputs district summaries."""

import sys
from collections import Counter, defaultdict
import pdb

import pandas as pd

from Database import Database, QueryType
from ElectionDistrict import ElectionDistrict
from ElectionResult import ElectionResult
from FIPS import NY_STATE_COUNTIES
from VTD import VTD


class Summary(object):
    """Calculate summaries for a given range of EDs."""

    DATABASE = Database().get_db()

    def __init__(self, district_type, district_num, countyname):

        querytype, key = None, None
        self.ed_list, self.counties = [], {}

        if district_type and district_num:
            print("Generating summary for district type {},"
                  " district num {}".format(district_type, district_num))

            # Load election districts, with voter registration numbers etc.
            if district_type.upper() == "STATESENATE":
                querytype = QueryType.ED_BY_SD.value
            elif district_type.upper() == "STATEASSEMBLY":
                querytype = QueryType.ED_BY_AD.value
            else:
                raise ValueError("Provide valid district_type")
            key = int(district_num)
        elif countyname:
            print("Generating summary for {}".format(countyname))
            querytype = QueryType.ED_BY_COUNTYNAME.value
            key = countyname

        print("Database QueryType {}".format(querytype))
        ed_uuids = [doc.value for doc in Summary.DATABASE.view(querytype)[key]]
        for uuid in ed_uuids:
            doc = ElectionDistrict.load(Summary.DATABASE, uuid)
            self.ed_list.append(doc)
            self.counties[doc.vf_countyname] = True

        print("Found {} Election Districts in {} counties"
              .format(len(self.ed_list), list(self.counties.keys())))

    def generate(self):
        # Load VTDs, map to EDs and load add results
        fips_code_lookup = {v: k for k, v in NY_STATE_COUNTIES.items()}
        county_codes = [fips_code_lookup[county_name]
                        for county_name in self.counties.keys()]
        querytype = QueryType.VTD_BY_CENSUS_COUNTY  # not value
        vtds = []
        for county_code in county_codes:
            vtds.extend(VTD.load_vtds_from_db(querytype, county_code))

        print("Found {} VTDs for review".format(len(vtds)))
        er_cache = defaultdict(list)
        stats_output_cache = {}
        results_output_cache = {}
        vtds_failed = 0
        print("Caching Election Results: ", end='')
        er_doc_view = ElectionResult.DATABASE.view(
            QueryType.ER_DOC_BY_COUNTY_PRECINCT.value)
        for row in er_doc_view:
            er_cache[str(row.key)].append(row.value)

        print(
            "{} taking {:<.2f} kbytes".format(
                len(er_cache),
                sys.getsizeof(er_cache) /
                1024))
        print("Stepping through VTDs", end='')
        for i, vtd in enumerate(vtds):
            if i % 10 == 0:
                print(".", end='')

            in_district = False
            vtd_stats = Counter()
            vtd_election_results = Counter()
            try:
                test = "{}{}{}".format(
                    vtd.census_STATE, vtd.census_COUNTY, vtd.census_VTD)
            except AttributeError:
                vtds_failed += 1
                continue

            geoid10_key = "{:02.0f}{:03.0f}{:.0f}".format(vtd.census_STATE,
                                                          vtd.census_COUNTY,
                                                          vtd.census_VTD)
            for vtd_ed in vtd.boe_eds:
                for ed in self.ed_list:
                    if (vtd.census_COUNTY_NAME == ed.vf_countyname)\
                        and (vtd_ed == ed.vf_ed_code):
                        print("Matched {},{} and {},{} for VTD {}".format(
                            vtd.census_county_name,
                            ed.vf_countyname,
                            vtd_ed,
                            ed.vf_ed_code,
                            vtd.census_LOGRECNO))
                        in_district = True
                        vtd_stats += Counter(ed.to_dict())

                    # Sum Election Results for all EDs in this VTD
                    key = str([ed.vf_countyname, ed.vf_ed_code])
                    for doc in er_cache[key]:
                        election_key = "{} {} {}: {}".format(
                            doc['oe_election_date'],
                            doc['oe_office'],
                            doc['oe_district'],
                            doc['oe_candidate'])
                        line_dict = {election_key: doc['oe_votes']}
                        vtd_election_results += Counter(line_dict)

            if in_district:
                vtd_stats += Counter(vtd.to_dict())
                stats_output_cache[geoid10_key] = dict(vtd_stats)
                results_output_cache[geoid10_key] = dict(vtd_election_results)

        print("\nGenerated stats for {} and result summaries for {} Election "
              "Districts.".format(len(stats_output_cache), len(results_output_cache)))
        print("{} VTDs failed.".format(vtds_failed))

        pdb.set_trace()

        # Print Results
        print("Writing output")
        stats = pd.DataFrame(vtd_stats)
        stats.to_csv("~/Downloads/stats.csv")
        results = pd.DataFrame(vtd_election_results)
        results.to_csv("~/Downloads/results.csv")


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
    if len(sys.argv) == 3:
        s = Summary(
            district_type=sys.argv[1],
            district_num=sys.argv[2],
            countyname=None)
        s.generate()
    elif len(sys.argv) == 2:
        s = Summary(
            district_type=None,
            district_num=None,
            countyname=sys.argv[1])
        s.generate()
    else:
        raise ValueError(
            'python Summary.py {STATESENATE|STATEASSEMBLY} {DISTRICT_NUM} or\n'
            'python Summary.py {COUNTYNAME}')
