"""Extracted from https://www.census.gov/prod/cen2010/doc/pl94-171.pdf,
Data Dictionary, TABLE (MATRIX) SECTION, p.6-21 et seq."""


P1_RACE_MATRIX = {
    0: "Total",
    1: "Population of one race",
    2: "White alone",
    3: "Black or African American alone",
    4: "American Indian and Alaska Native alone",
    5: "Asian alone",
    6: "Native Hawaiian and Other Pacific Islander alone",
    7: "Some Other Race alone",
    8: "Two or More Races",
    9: "Population of two races",
    10: "White; Black or African American",
    11: "White; American Indian and Alaska Native",
    12: "White; Asian",
    13: "White; Native Hawaiian and Other Pacific Islander",
    14: "White; Some Other Race",
    15: "Black or African American; American Indian and Alaska Native",
    16: "Black or African American; Asian",
    17: "Black or African American; Native Hawaiian and Other Pacific Islander",
    18: "Black or African American; Some Other Race",
    19: "American Indian and Alaska Native; Asian",
    20: "American Indian and Alaska Native; Native Hawaiian and Other Pacific "
        "Islander",
    21: "American Indian and Alaska Native; Some Other Race",
    22: "Asian; Native Hawaiian and Other Pacific Islander",
    23: "Asian; Some Other Race",
    24: "Native Hawaiian and Other Pacific Islander; Some Other Race",
    25: "Population of three races",
    26: "White; Black or African American; American Indian and Alaska Native",
    27: "White; Black or African American; Asian",
    28: "White; Black or African American; Native Hawaiian and Other Pacific "
        "Islander",
    29: "White; Black or African American; Some Other Race",
    30: "White; American Indian and Alaska Native; Asian",
    31: "White; American Indian and Alaska Native; Native Hawaiian and Other "
        "Pacific Islander",
    32: "White; American Indian and Alaska Native; Some Other Race",
    33: "White; Asian; Native Hawaiian and Other Pacific Islander",
    34: "White; Asian; Some Other Race",
    35: "White; Native Hawaiian and Other Pacific Islander; Some Other Race",
    36: "Black or African American; American Indian and Alaska Native; Asian",
    37: "Black or African American; American Indian and Alaska Native; Native "
        "Hawaiian and Other Pacific Islander",
    38: "Black or African American; American Indian and Alaska Native; Some "
        "Other Race",
    39: "Black or African American; Asian; Native Hawaiian and Other Pacific "
        "Islander",
    40: "Black or African American; Asian; Some Other Race",
    41: "Black or African American; Native Hawaiian and Other Pacific "
        "Islander; Some Other Race",
    42: "American Indian and Alaska Native; Asian; Native Hawaiian and Other "
        "Pacific Islander",
    43: "American Indian and Alaska Native; Asian; Some Other Race",
    44: "American Indian and Alaska Native; Native Hawaiian and Other Pacific "
        "Islander; Some Other Race",
    45: "Asian; Native Hawaiian and Other Pacific Islander; Some Other Race",
    46: "Population of four races",
    47: "White; Black or African American; American Indian and Alaska Native; "
        "Asian",
    48: "White; Black or African American; American Indian and Alaska Native; "
        "Native Hawaiian and Other Pacific Islander",
    49: "White; Black or African American; American Indian and Alaska Native; "
        "Some Other Race",
    50: "White; Black or African American; Asian; Native Hawaiian and Other "
        "Pacific Islander",
    51: "White; Black or African American; Asian; Some Other Race",
    52: "White; Black or African American; Native Hawaiian and Other Pacific "
        "Islander; Some Other Race",
    53: "White; American Indian and Alaska Native; Asian; Native Hawaiian and "
        "Other Pacific Islander",
    54: "White; American Indian and Alaska Native; Asian; Some Other Race",
    55: "White; American Indian and Alaska Native; Native Hawaiian and Other "
        "Pacific Islander; Some Other Race",
    56: "White; Asian; Native Hawaiian and Other Pacific Islander; Some Other "
        "Race",
    57: "Black or African American; American Indian and Alaska Native; Asian; "
        "Native Hawaiian and Other Pacific Islander",
    58: "Black or African American; American Indian and Alaska Native; Asian; "
        "Some Other Race",
    59: "Black or African American; American Indian and Alaska Native; Native "
        "Hawaiian and Other Pacific Islander; Some Other Race",
    60: "Black or African American; Asian; Native Hawaiian and Other Pacific "
        "Islander; Some Other Race",
    61: "American Indian and Alaska Native; Asian; Native Hawaiian and Other "
        "Pacific Islander; Some Other Race",
    62: "Population of five races",
    63: "White; Black or African American; American Indian and Alaska Native; "
        "Asian; Native Hawaiian and Other Pacific Islander",
    64: "White; Black or African American; American Indian and Alaska Native; "
        "Asian; Some Other Race",
    65: "White; Black or African American; American Indian and Alaska Native; "
        "Native Hawaiian and Other Pacific Islander; Some Other Race",
    66: "White; Black or African American; Asian; Native Hawaiian and Other "
        "Pacific Islander; Some Other Race",
    67: "White; American Indian and Alaska Native; Asian; Native Hawaiian and "
        "Other Pacific Islander; Some Other Race",
    68: "Black or African American; American Indian and Alaska Native; Asian; "
        "Native Hawaiian and Other Pacific Islander; Some Other Race",
    69: "Population of six races",
    70: "White; Black or African American; American Indian and Alaska Native; "
        "Asian; Native Hawaiian and Other Pacific Islander; Some Other Race"}

P2_HISPANIC_MATRIX = {
    0: "Total",
    1: "Hispanic or Latino",
    2: "Not Hispanic or Latino",
    3: "Not Hispanic or Latino; Population of one race",
    4: "Not Hispanic or Latino; White alone",
    5: "Not Hispanic or Latino; Black or African American alone",
    6: "Not Hispanic or Latino; American Indian and Alaska Native alone",
    7: "Not Hispanic or Latino; Asian alone",
    8: "Not Hispanic or Latino; Native Hawaiian and Other Pacific Islander "
       "alone",
    9: "Not Hispanic or Latino; Some Other Race alone",
    10: "Not Hispanic or Latino; Two or More Races",
    11: "Not Hispanic or Latino; Population of two races",
    12: "Not Hispanic or Latino; White; Black or African American",
    13: "Not Hispanic or Latino; White; American Indian and Alaska Native",
    14: "Not Hispanic or Latino; White; Asian",
    15: "Not Hispanic or Latino; White; Native Hawaiian and Other Pacific "
        "Islander",
    16: "Not Hispanic or Latino; White; Some Other Race",
    17: "Not Hispanic or Latino; Black or African American; American Indian "
        "and Alaska Native",
    18: "Not Hispanic or Latino; Black or African American; Asian",
    19: "Not Hispanic or Latino; Black or African American; Native Hawaiian "
        "and Other Pacific Islander",
    20: "Not Hispanic or Latino; Black or African American; Some Other Race",
    21: "Not Hispanic or Latino; American Indian and Alaska Native; Asian",
    22: "Not Hispanic or Latino; American Indian and Alaska Native; Native "
        "Hawaiian and Other Pacific Islander",
    23: "Not Hispanic or Latino; American Indian and Alaska Native; Some Other "
        "Race",
    24: "Not Hispanic or Latino; Asian; Native Hawaiian and Other Pacific "
        "Islander",
    25: "Not Hispanic or Latino; Asian; Some Other Race",
    26: "Not Hispanic or Latino; Native Hawaiian and Other Pacific Islander; "
        "Some Other Race",
    27: "Not Hispanic or Latino; Population of three races",
    28: "Not Hispanic or Latino; White; Black or African American; American "
        "Indian and Alaska Native",
    29: "Not Hispanic or Latino; White; Black or African American; Asian",
    30: "Not Hispanic or Latino; White; Black or African American; Native "
        "Hawaiian and Other Pacific Islander",
    31: "Not Hispanic or Latino; White; Black or African American; Some Other "
        "Race",
    32: "Not Hispanic or Latino; White; American Indian and Alaska Native; "
        "Asian",
    33: "Not Hispanic or Latino; White; American Indian and Alaska Native; "
        "Native Hawaiian and Other Pacific Islander",
    34: "Not Hispanic or Latino; White; American Indian and Alaska Native; "
        "Some Other Race",
    35: "Not Hispanic or Latino; White; Asian; Native Hawaiian and Other "
        "Pacific Islander",
    36: "Not Hispanic or Latino; White; Asian; Some Other Race",
    37: "Not Hispanic or Latino; White; Native Hawaiian and Other Pacific "
        "Islander; Some Other Race",
    38: "Not Hispanic or Latino; Black or African American; American Indian "
        "and Alaska Native; Asian",
    39: "Not Hispanic or Latino; Black or African American; American Indian "
        "and Alaska Native; Native Hawaiian and Other Pacific Islander",
    40: "Not Hispanic or Latino; Black or African American; American Indian "
        "and Alaska Native; Some Other Race",
    41: "Not Hispanic or Latino; Black or African American; Asian; Native "
        "Hawaiian and Other Pacific Islander",
    42: "Not Hispanic or Latino; Black or African American; Asian; Some Other "
        "Race",
    43: "Not Hispanic or Latino; Black or African American; Native Hawaiian "
        "and Other Pacific Islander; Some Other Race",
    44: "Not Hispanic or Latino; American Indian and Alaska Native; Asian; "
        "Native Hawaiian and Other Pacific Islander",
    45: "Not Hispanic or Latino; American Indian and Alaska Native; Asian; "
        "Some Other Race",
    46: "Not Hispanic or Latino; American Indian and Alaska Native; Native "
        "Hawaiian and Other Pacific Islander; Some Other Race",
    47: "Not Hispanic or Latino; Asian; Native Hawaiian and Other Pacific "
        "Islander; Some Other Race",
    48: "Not Hispanic or Latino; Population of four races",
    49: "Not Hispanic or Latino; White; Black or African American; American "
        "Indian and Alaska Native; Asian",
    50: "Not Hispanic or Latino; White; Black or African American; American "
        "Indian and Alaska Native; Native Hawaiian and Other Pacific Islander",
    51: "Not Hispanic or Latino; White; Black or African American; American "
        "Indian and Alaska Native; Some Other Race",
    52: "Not Hispanic or Latino; White; Black or African American; Asian; "
        "Native Hawaiian and Other Pacific Islander",
    53: "Not Hispanic or Latino; White; Black or African American; Asian; Some "
        "Other Race",
    54: "Not Hispanic or Latino; White; Black or African American; Native "
        "Hawaiian and Other Pacific Islander; Some Other Race",
    55: "Not Hispanic or Latino; White; American Indian and Alaska Native; "
        "Asian; Native Hawaiian and Other Pacific Islander",
    56: "Not Hispanic or Latino; White; American Indian and Alaska Native; "
        "Asian; Some Other Race",
    57: "Not Hispanic or Latino; White; American Indian and Alaska Native; "
        "Native Hawaiian and Other Pacific Islander; Some Other Race",
    58: "Not Hispanic or Latino; White; Asian; Native Hawaiian and Other "
        "Pacific Islander; Some Other Race",
    59: "Not Hispanic or Latino; Black or African American; American Indian "
        "and Alaska Native; Asian; Native Hawaiian and Other Pacific Islander",
    60: "Not Hispanic or Latino; Black or African American; American Indian "
        "and Alaska Native; Asian; Some Other Race",
    61: "Not Hispanic or Latino; Black or African American; American Indian "
        "and Alaska Native; Native Hawaiian and Other Pacific Islander; Some "
        "Other Race",
    62: "Not Hispanic or Latino; Black or African American; Asian; Native "
        "Hawaiian and Other Paci c Islander; Some Other Race",
    63: "Not Hispanic or Latino; American Indian and Alaska Native; Asian; "
        "Native Hawaiian and Other Paci c Islander; Some Other Race",
    64: "Not Hispanic or Latino; Population of five races",
    65: "Not Hispanic or Latino; White; Black or African American; American "
        "Indian and Alaska Native; Asian; Native Hawaiian and Other Pacific "
        "Islander",
    66: "Not Hispanic or Latino; White; Black or African American; American "
        "Indian and Alaska Native; Asian; Some Other Race",
    67: "Not Hispanic or Latino; White; Black or African American; American "
        "Indian and Alaska Native; Native Hawaiian and Other Pacific Islander; "
        "Some Other Race",
    68: "Not Hispanic or Latino; White; Black or African American; Asian; "
        "Native Hawaiian and Other Pacific Islander; Some Other Race",
    69: "Not Hispanic or Latino; White; American Indian and Alaska Native; "
        "Asian; Native Hawaiian and Other Pacific Islander; Some Other Race",
    70: "Not Hispanic or Latino; Black or African American; American Indian "
        "and Alaska Native; Asian; Native Hawaiian and Other Pacific Islander; "
        "Some Other Race",
    71: "Not Hispanic or Latino; Population of six races",
    72: "Not Hispanic or Latino; White; Black or African American; American "
        "Indian and Alaska Native; Asian; Native Hawaiian and Other Pacific "
        "Islander; Some Other Race"}

P3_RACE_18OVER = P1_RACE_MATRIX
P4_HISPANIC_18OVER = P2_HISPANIC_MATRIX

H1_OCCUPANCY = {0: "Total housing units",
                1: "Occupied housing units",
                2: "Vacant housing units"}
