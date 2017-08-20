"""A utility for fuzzy-matching people between the NY State Voter File and
other data sources, e.g. Campaign Finance records or call records.

Uses [fuzzywuzzy](https://github.com/seatgeek/fuzzywuzzy) to fuzzy-match
name strings, with a bit of added interpersonal intelligence.

@author n.o.franklin@gmail.com
"""
import re
from sys import stderr

from fuzzywuzzy.process import extractOne

def try_int(number):
    """Gracefully try and strip decimal places from integers."""
    try:
        return "{:0.0f}".format(float(number))
    except ValueError:
        return ""

def parse_fuzzy_string(string):
    """Parse fuzzy string."""
    match = re.match(r'(\w+),(\w+),(\d+) ([^,]+) , (Apt ([^, ]+))? ([^,]+) NY ,'
                     r'(\d+),(\d+)\/(\w)\/(\w),(\d+).*',
                     string)
    if match:
        return dict(zip(['FIRSTNAME',
                         'LASTNAME',
                         'RADDNUMBER',
                         'RSTREETNAM',
                         'UNUSED1',
                         'RAPARTMENT',
                         'TOWNCITY',
                         'RZIP5',
                         'AGE',
                         'GENDER',
                         'ENROLLMENT',
                         'VANID'], match.groups()))

def build_fuzzy_string(row):
    """Build string for fuzzy-matching in VAN "Extra Data" format, e.g.
    Laurence,Bromberg,185 West End Ave , Apt 18L New York NY ,10023,48/M/D,2726268,null
    """
    return  ",".join([row['FIRSTNAME'].title() if 'FIRSTNAME' in row else "",
                      row['LASTNAME'].title() if 'LASTNAME' in row else "",
                      "{} {} , {} {} NY ".format(row['RADDNUMBER'] if 'RADDNUMBER' in row else "",
                                                 row['RSTREETNAM'].title() if "RSTREETNAM" in row else "",
                                                 "Apt {}".format(row['RAPARTMENT']) if 'RAPARTMENT' in row else "",
                                                 row['TOWNCITY'].title() if 'TOWNCITY' in row else ""),
                      try_int(row['RZIP5'] if 'RZIP5' in row else ""),
                      "{}/{}/{}".format(try_int(row['AGE']) if 'AGE' in row else "",
                                        row['GENDER'] if 'GENDER' in row else "",
                                        row['ENROLLMENT'][0] if 'ENROLLMENT' in row else ""),
                      "0000000",
                      "null"])

def fuzzy_match(person, universe):
    """Find the best person match in the universe.

    person (dict)                   features we know
    universe (pandas.DataFrame)     all people in the voter universe

    If you're running this repeatedly on the same universe, avoid recalculation
    using df['fuzzy_string'] = df.apply(FuzzyMatch.build_fuzzy_string, axis=1).

    NB We don't do much type-checking here, to allow Python/Pandas to duck-type
    if required.  But this might lead to surprising results, e.g.
    int("19350101") != datetime(1935, 1, 1).

    Returns completed dict."""

    # Precise lookup by unique ID.  Avoid the copy operation.  Only return
    # if only one row exists; otherwise continue to rest of logic.
    if 'SBOEID' in person:
        results = universe.loc[universe['SBOEID'] == person['SBOEID']]\
            .to_dict(orient='records')
        if len(results) == 1:
            return results[0], 100

    if 'COUNTYVRNU' in person:
        results = universe.loc[universe['COUNTYVRNU'] == person['COUNTYVRNU']]\
            .to_dict(orient='records')
        if len(results) == 1:
            return results[0], 100

    # Else, narrow universe using fields which must match exactly:
    # DOB, GENDER, LASTNAME and AGE
    remaining = universe.copy(deep=True)

    if 'DOB' in person:
        remaining = remaining.loc[remaining['DOB'] == person['DOB']]
        print("Matched DOB: {} remaining".format(remaining.shape[0]), file=stderr)

    if 'GENDER' in person:
        remaining = remaining.loc[remaining['GENDER'] == person['GENDER'].upper()]
        print("Matched GENDER: {} remaining".format(remaining.shape[0]), file=stderr)

    if 'LASTNAME' in person:
        remaining = remaining.loc[remaining['LASTNAME'] == person['LASTNAME'].upper()]
        print("Matched LASTNAME: {} remaining".format(remaining.shape[0]), file=stderr)

    if 'AGE' in person:
        remaining = remaining.loc[remaining['AGE'] == person['AGE']]
        print("Matched AGE: {} remaining".format(remaining.shape[0]), file=stderr)

    # Find best match from remaining data, handling abbreviations of firstname,
    # change of address, missing data, etc.
    # Use the column if it already exists, don't rebuild.
    if 'fuzzy_string' not in remaining.columns:
        print("Avoid recalculation using df['fuzzy_string'] = "
              "df.apply(FuzzyMatch.build_fuzzy_string, axis=1).", file=stderr)
        remaining['fuzzy_string'] = remaining.apply(build_fuzzy_string, axis=1)

    match, confidence, _ = extractOne(build_fuzzy_string(person), remaining['fuzzy_string'])
    result = remaining.loc[remaining['fuzzy_string'] == match]
    return result.to_dict(orient='records')[0], confidence
