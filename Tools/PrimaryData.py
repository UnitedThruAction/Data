"""Process primary data from NY State Board of Elections PDF extract
(via Tabula) and convert to sensible format.

INPUT: Data/tabula-2016StateLocalPrimaryElectionResults.csv

OUTPUT: Data/2016StateLocalPrimaryFormatted.csv
"""

import re
import pandas as pd
import numpy as np

def df_from_raw(raw):
    """Read Tabula-generated CSV and output dataframe for future use."""
    row_num = 0
    candidates = []
    row_format = False
    for series in raw.iterrows():
        cols = series[1]
        if "DISTRICT" in str(cols.iloc[0]).upper():
            district_name = cols.iloc[0]
            print("Starting district {}".format(district_name))
            opp_to_ballot_present = False
            cand_created = False
            row_format = False
            row_num = 2
            if 'district_candidates' in locals():
                if district_candidates:
                    candidates.extend(district_candidates)
            district_candidates = []
            continue
        if row_num == 2:  # Forenames
            match = re.search('Candidates - (\w+)', cols.astype(str).iloc[0])
            if match:
                row_format = True
                party = match.group(1)
                row_num += 1
                continue
            else:
                forenames = cols.astype(str)
                row_num += 1
                continue
        if not row_format:
            if row_num == 3:  # Surnames
                surnames = cols.astype(str)
                row_num += 1
                continue
            if row_num == 4:
                if "OPP. TO BALLOT" in "".join(cols.astype(str).tolist()):
                    opp_to_ballot = cols
                    opp_to_ballot_present = True
                    row_num += 1
                    continue
                else:  # Party
                    parties = cols
                    opp_to_ballot = pd.Series(
                        ['' for _ in range(cols.shape[0])])
                    row_num += 1
                    continue
            if row_num == 5 and opp_to_ballot_present:
                parties = cols
                row_num += 1
                continue
            if (row_num == 5 and not opp_to_ballot_present) or row_num > 5:
                if cols.iloc[0] != "Total":
                    # Results
                    for i in range(1, cols.shape[0]):
                        if parties.iloc[i]: # i.e., there was a candidate
                            if not cand_created:  # first row of results
                                candidate = {}
                                candidate['District'] = district_name
                                candidate['Name'] = " ".join(
                                    [forenames.iloc[i], surnames.iloc[i]])
                                candidate['Party'] = parties.iloc[i]
                                candidate['Votes'] = int(
                                    str(cols.fillna(0).iloc[i]).replace(',', ''))
                                candidate['OppToBallot'] = opp_to_ballot.iloc[i]
                                print(
                                    "Writing candidate {}".format(
                                        candidate['Name']))
                                district_candidates.append(candidate)
                            else:  # further rows of results
                                cand_index = i - 1  # starts at 0
                                district_candidates[cand_index][
                                    'Votes'] += int(str(cols.fillna(0).iloc[i]).replace(',', ''))
                    cand_created = True
                row_num += 1
                continue
        if row_format:
            if row_num == 3:  # Counties etc.
                if "OPP. TO BALLOT" in cols.iloc[0]:
                    opp_to_ballot_value = "OPP. TO BALLOT"
                else:
                    opp_to_ballot_value = ""
                if 'Total' in cols.tolist():
                    total_col = cols.tolist().index('Total')
                else:
                    total_col = 1 # by default
                row_num += 1
                continue
            else:
                candidate = {}
                candidate['District'] = district_name
                candidate['Name'] = cols.iloc[0]
                candidate['Party'] = party
                candidate['Votes'] = cols.iloc[total_col]
                candidate['OppToBallot'] = opp_to_ballot_value
                candidates.append(candidate)
                row_num += 1
                continue
    # Last district
    if district_candidates:
        candidates.extend(district_candidates)
    return pd.DataFrame(candidates)

if __name__ == "__main__":
    raw_file = pd.read_csv(
        "../Data/tabula-2016StateLocalPrimaryElectionResults.csv",
        thousands=',',header=0)
    df = df_from_raw(raw_file)
    df.dropna(inplace=True)
    df.to_csv("../Data/2016StateLocalPrimaryFormatted.csv", index=False)
