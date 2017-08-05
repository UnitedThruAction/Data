"""Parse Suffolk County data file and emit OpenElections CSV.

@author n.o.franklin@gmail.com
@date 2017-07-11
"""

import sys


def parse_information_record(line):
    """Type I.  Read and parse information record data."""
    information = line[5:].rstrip()
    return {'information': information}


def parse_office_record(line):
    """Type R.  Read and parse office record data."""
    office_title = line[5:45].rstrip()

    # Standardize office title
    if 'President of The United States' in office_title:
        office_title_std = 'President'
    elif 'United States Senator' in office_title:
        office_title_std = 'U.S. Senate'
    elif 'Representative in Congress,' in office_title:
        office_title_std = 'U.S. House'
    elif 'Member of Senate' in office_title:
        office_title_std = 'State Assembly'
    elif 'Member of Assembly' in office_title:
        office_title_std = 'State Senate'
    elif 'Justice of the Supreme Court' in office_title:
        office_title_std = 'Supreme Court'
    elif 'District Court Judge' in office_title:
        office_title_std = 'District Court Judge'
    elif 'County Legislator' in office_title:
        office_title_std = 'County Legislator'
    elif 'Receiver of Taxes' in office_title:
        office_title_std = 'Receiver of Taxes'
    elif 'Councilman' in office_title:
        office_title_std = 'Councilman'
    elif 'Councilmember' in office_title:
        office_title_std = 'Councilmember'
    elif 'Superintendent of Highways' in office_title:
        office_title_std = 'Superintendent of Highways'
    elif 'Town Clerk' in office_title:
        office_title_std = 'Town Clerk'
    elif 'Supervisor' in office_title:
        office_title_std = 'Supervisor'
    else:
        office_title_std = office_title.rstrip()

    office_district_type = line[45:46].rstrip()
    try:
        office_district_number = int(line[46:50])
    except ValueError:
        office_district_number = ''
    if office_district_number == 0:
        office_district_number = ''
    opp_to_ballot = line[50:51]
    num_election_districts = int(line[51:55])
    count_eligible_voters = int(line[55:62])
    try:
        num_candidates = int(line[62:64])
    except ValueError:
        num_candidates = 0
    opp_to_ballot_lookup = {'Y': True,
                            'N': False,
                            ' ': 'Unknown',
                            'O': 'Unknown',
                            '0': 'Unknown',
                            '2': 'Unknown'}
    district_type_lookup = {'U': 'United States',
                            'N': 'New York State',
                            'K': 'Suffolk County',
                            'A': 'Unknown',
                            'L': 'Unknown',
                            'T': 'Unknown',
                            'W': 'Unknown',
                            'S': 'Unknown',
                            'J': 'Unknown',
                            'C': 'Unknown'}
    return {'office_title': office_title,
            'office_title_std': office_title_std,
            'office_district_type': district_type_lookup[office_district_type],
            'office_district_number': office_district_number,
            'opp_to_ballot': opp_to_ballot_lookup[opp_to_ballot],
            'num_election_districts': num_election_districts,
            'count_eligible_voters': count_eligible_voters,
            'num_candidates': num_candidates}


def parse_candidate_record(line):
    """Type C.  Read and parse candidate record data."""
    candidate_name = line[5:30].rstrip().title()
    candidate_name_std = candidate_name
    if ', ' in candidate_name:
        # Re-order 'Smith, Bob' as 'Bob Smith'
        names = candidate_name.split(', ')
        candidate_name_std = "{} {}".format(names[1], names[0])
    party_code = line[30:33].rstrip()
    write_in_flag = line[33:34]
    write_in_lookup = {'S': True, ' ': 'Unknown'}
    total_votes = int(line[34:41])
    row_lever_on_ballot = line[41:44].rstrip()
    return {'candidate_name': candidate_name,
            'candidate_name_std': candidate_name_std,
            'party_code': party_code,
            'write_in_flag': write_in_lookup[write_in_flag],
            'total_votes': total_votes,
            'row_lever_on_ballot': row_lever_on_ballot}


def parse_ed_record(line):
    """Type E.  Read ED-result record data."""
    record_length = int(line[:4])
    town_code = line[5:6]
    town_code_lookup = {'0': 'Shelter Island',
                        '1': 'Brookhaven',
                        '2': 'Huntington',
                        '3': 'Islip',
                        '4': 'Babylon',
                        '5': 'Smithtown',
                        '6': 'Southampton',
                        '7': 'East Hampton',
                        '8': 'Southold',
                        '9': 'Riverhead'}
    ed_number = int(line[6:9])
    reported_status = line[9:10].rstrip()
    eligible_voters = int(line[10:14])
    try:
        whole_number = int(line[14:20])
    except ValueError:
        whole_number = 0
    congress_district = int(line[34:35])
    senate_district = int(line[35:36])
    assembly_district = int(line[36:38])
    legislative_district = int(line[38:40])
    towncouncil_district = line[40:42].rstrip()
    try:
        blank_votes = int(line[42:46])
    except ValueError:
        blank_votes = 0
    void_votes = int(line[46:49])
    try:
        scattering_votes = int(line[49:52])
    except ValueError:
        scattering_votes = 0

    # Handle variable-length candidate fields
    num_candidates = (record_length - 52) / 4
    if num_candidates % 1 != 0:
        raise ValueError("Incorrect number of characters on line.")
    votes = []
    try:
        for i in range(int(num_candidates)):
            start_index = 52 + (4 * i)
            end_index = 56 + (4 * i)
            votes.append(int(line[start_index:end_index]))
    except TypeError as t:
        print("Caught TypeError with num_candidates {}, record_length {}, "
              "line '{}'".format(num_candidates, record_length, line))

    # Generate Suffolk-specific precinct code
    precinct_code = "{} #: {:>3}".format(town_code_lookup[town_code].title(),
                                         "{:02.0f}".format(ed_number))

    return {'town_name': town_code_lookup[town_code],
            'ed_number': ed_number,
            'reported_status': reported_status,
            'eligible_voters': eligible_voters,
            'whole_number': whole_number,
            'congress_district': congress_district,
            'senate_district': senate_district,
            'assembly_district': assembly_district,
            'legislative_district': legislative_district,
            'towncouncil_district': towncouncil_district,
            'blank_votes': blank_votes,
            'void_votes': void_votes,
            'scattering_votes': scattering_votes,
            'num_candidates': num_candidates,
            'votes': votes,
            'precinct_code': precinct_code}


def process_file(filename):
    """Read the whole file and emit output in standard OE format."""
    out_handle = open("{}-output.csv".format(filename), 'w')
    out_handle.write('county,precinct,eligible_voters,office,district,party,candidate,votes\n')
    candidates = None
    office = None
    in_handle = open(filename, 'r')
    for line in in_handle:
        if line[4:5] == 'I':
            # Information
            print(parse_information_record(line))
        if line[4:5] == 'R':
            # Office
            office = parse_office_record(line)
            # Reset candidates
            candidates = []
        if line[4:5] == 'C':
            # Candidate
            candidates.append(parse_candidate_record(line))
        if line[4:5] == 'E':
            # ED Breakdown
            election_district = parse_ed_record(line)
            for i, vote in enumerate(election_district['votes']):
                # County
                output = ['Suffolk']
                # Precinct
                output.append(election_district['precinct_code'])
                # Eligible voters
                output.append(str(election_district['eligible_voters']))
                # Office
                output.append(office['office_title_std'])
                # District
                output.append(str(office['office_district_number']))
                # Party
                try:
                    output.append(candidates[i]['party_code'])
                except IndexError:
                    output.append('')
                # Candidate
                try:
                    output.append(candidates[i]['candidate_name_std'])
                except IndexError:
                    output.append('')
                # Votes
                output.append(str(vote))
                out_handle.write(",".join(output))
                out_handle.write("\n")

            # Append ED void/scattering votes
            special_types = {'Scattering': 'scattering_votes',
                             'Void': 'void_votes',
                             'Blank': 'blank_votes'}
            for name in special_types:
                if election_district[special_types[name]] > 0:
                    output = ['Suffolk',
                              election_district['precinct_code'],
                              str(election_district['eligible_voters']),
                              office['office_title_std'],
                              str(office['office_district_number']),
                              '',
                              name,
                              str(election_district[special_types[name]])]
                    out_handle.write(",".join(output))
                    out_handle.write("\n")

    in_handle.close()
    out_handle.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Provide filename on command-line.")
    else:
        process_file(sys.argv[1])
