"""A utility for fuzzy-matching people between the NY State Voter File and
other data sources, e.g. Campaign Finance records or call records.

Uses [fuzzywuzzy](https://github.com/seatgeek/fuzzywuzzy) to fuzzy-match
name strings, with a bit of added interpersonal intelligence.

@author n.o.franklin@gmail.com
"""
import re

from fuzzywuzzy.process import fuzz


def try_int(number):
    """Gracefully try and strip decimal places from integers."""
    try:
        return "{:0.0f}".format(float(number))
    except (ValueError, TypeError):
        return ""

def build_address_string(row):
    return "{} {} , {} {} NY ".format(row['RADDNUMBER'] if 'RADDNUMBER' in row else "",
        row['RSTREETNAM'].title() if "RSTREETNAM" in row else "",
        "Apt {}".format(row['RAPARTMENT']) if 'RAPARTMENT' in row else "",
        row['TOWNCITY'].title() if 'TOWNCITY' in row else "")

def parse_van_string(string):
    """Parse VAN 'Extra Data' string."""
    # Format 1: the most common VAN format
    match1 = re.match(
        r'([^,]+)?,([^,]+)?,(\d+)? ([^,]+), (Apt ([^, ]+) )?([^,]+)? NY ,'
        r'(\d+)?,(\d+)?\/(\w)?\/(\w)?,(\d+)?.*', string)
    if match1:
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
                         'VANID'], match1.groups()))

    # Format 2: alternate VAN format
    match2 = re.match(
        r'([^,]+)?,([^,]+)?,(\d+)? ([^,]+), (Apt ([^, ]+) )?([^,]+)? NY ,'
        r'(\d+)?,(\d+)?,(\w)?,(\d+)?.*', string)
    if match2:
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
                         'VANID'], match2.groups()))

def fuzzy_match(person, universe):
    """Find the best person match in the universe.

    person (dict)                   features we know
    universe (pandas.DataFrame)     all people in the voter universe

    NB We don't do much type-checking here, to allow Python/Pandas to duck-type
    if required.  But this might lead to surprising results, e.g.
    int("19350101") != datetime(1935, 1, 1).

    Returns completed dict and confidence."""

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

    # Narrow universe using fields which must match exactly:
    # DOB, GENDER, LASTNAME and AGE
    remaining = universe.copy()

    if 'DOB' in person and person['DOB'] is not None:
        remaining = remaining.loc[remaining['DOB'] == person['DOB']]

    if 'GENDER' in person and person['GENDER'] is not None:
        remaining = remaining.loc[
            remaining['GENDER'] == person['GENDER'].upper()]

    if 'LASTNAME' in person and person['LASTNAME'] is not None:
        remaining = remaining.loc[
            remaining['LASTNAME'] == person['LASTNAME'].upper()]

    if 'AGE' in person and person['AGE'] is not None:
        remaining = remaining.loc[remaining['AGE'] == person['AGE']]

    if remaining.shape[0] == 0:
        # Nobody in the universe matches the mandatory fields
        return dict(), 0

    # Else, fuzzy match on remaining fields:
    # same firstname different address, likely person moved;
    # different firstname same address, possible abbreviation, but less likely
    # both different: very unlikely to be same person
    # i.e. FIRSTNAME (80% weighting), ADDRESS (20% weighting)

    if 'FIRSTNAME' in person:
        remaining['firstname_ratio'] = remaining.apply(
            lambda row: fuzz.ratio(person['FIRSTNAME'], row['FIRSTNAME']), axis=1)
    else:
        remaining['firstname_ratio'] = remaining.apply(lambda row: 50, axis=1)

    # Build address strings and try and match
    person['ADDRESS'] = build_address_string(person)
    remaining['ADDRESS'] = remaining.apply(build_address_string, axis=1)
    remaining['address_ratio'] = remaining.apply(
        lambda row: fuzz.ratio(person['ADDRESS'], row['ADDRESS']), axis=1)

    remaining['overall_match'] = 0.8 * remaining['firstname_ratio'] \
        + 0.2 * remaining['address_ratio']

    # Threshold and return best match.
    # Level 20 picked from examination of output.
    match = remaining.sort_values('address_ratio', ascending=False)\
        .iloc[0].to_dict()

    if match['overall_match'] > 20:
        return match, match['overall_match']
    else:
        return dict(), 0
