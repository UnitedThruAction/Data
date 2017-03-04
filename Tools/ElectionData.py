"""Collect information from the NY State Board of Elections website (http://www.elections.ny.gov/2016ElectionResults.html) and publish in a way more sensible format.

Code is given for 2016 and 2014 below, but could easily be extended.  Note the NY State Board of Elections uses inconsistent names on their website, and data from before 2014 is only published in PDF format, so an intermediary XLS must be produced first.  Use `df_from_raw_pdf(raw)` to process data from these intermediary XLS files, as the line spacing is slightly different.  Tabula (http://tabula.technology) can be used to manually extract tables from PDFs.

Enrollment data is similar, in that it is only published in PDF format.  This script assumes you have used Tabula to extract this and it is is available in file `../Data/tabula-congress_nov16.csv`, `../Data/tabula-senate_nov16.csv` and `../Data/tabula-assembly_nov16.csv`.

INPUT:  Elections data from web in non-sensible Excel format, enrollment data from scraped PDFs.
OUTPUT: ../Data/NY State Senate Election Details.xls, Excel sheet of elections data in sensible summary format.

"""

import pandas as pd
import numpy as np
import re
from collections import defaultdict

def df_from_raw(raw):
    """Read an Excel file and output a dataframe for further use."""
    row_num = 0
    candidates = []
    forenames, surnames, parties = (), (), ()
    district_name = ""
    for series in raw.iterrows():
        cols = series[1]
        if "DISTRICT" in str(
                cols.iloc[0]):  # If col 0 contains word DISTRICT then initialize row_num, store name
            district_name = cols.iloc[0]
            row_num = 1
            continue
        if row_num == 2:  # Forenames
            forenames = cols
            row_num += 1
            continue
        if row_num == 3:  # Surnames
            surnames = cols
            row_num += 1
            continue
        if row_num == 4:  # Party
            parties = cols
            row_num += 1
            continue
        if "RECAP" in str(cols.iloc[0]):  # Recap totals
            for i in range(1, cols.shape[0]):
                if pd.notnull(cols.iloc[i]) and int(cols.iloc[i]) != 0:  # Recap total is not null
                    candidate = {}
                    candidate['District'] = district_name
                    candidate['Name'] = " ".join(
                        [forenames.iloc[i], surnames.iloc[i]])
                    candidate['Party'] = parties.iloc[i]
                    candidate['Votes'] = cols.iloc[i]
                    candidates.append(candidate)
        else:  # Skip rows with no data or irrelevant data
            row_num += 1
            continue
    df = pd.DataFrame(candidates)
    df['Won'] = df.groupby(['District'])['Votes'].transform(max) == df['Votes']
    return df


def df_from_raw_pdf(raw):
    row_num = 0
    candidates = []
    forenames, surnames, parties = (), (), ()
    district_name = ""
    for series in raw.iterrows():
        cols = series[1]
        if "DISTRICT" in str(
                cols.iloc[0]):  # If col 0 contains word DISTRICT then initialize row_num, store name
            district_name = cols.iloc[0]
            row_num = 1
            continue
        if row_num == 1:  # Forenames
            forenames = cols
            row_num += 1
            continue
        if row_num == 2:  # Surnames
            surnames = cols
            row_num += 1
            continue
        if row_num == 3:  # Party
            parties = cols
            row_num += 1
            continue
        if "RECAP" in str(cols.iloc[0]):  # Recap totals
            for i in range(1, cols.shape[0]):
                if pd.notnull(cols.iloc[i]) and int(cols.iloc[i]) != 0:  # Recap total is not null
                    candidate = {}
                    candidate['District'] = district_name
                    candidate['Name'] = " ".join([forenames.iloc[i], surnames.iloc[i]])
                    candidate['Party'] = parties.iloc[i]
                    candidate['Votes'] = cols.iloc[i]
                    candidates.append(candidate)
        else:  # Skip rows with no data or irrelevant data
            row_num += 1
            continue
    df = pd.DataFrame(candidates)
    df['Won'] = df.groupby(['District'])['Votes'].transform(max) == df['Votes']
    return df

if __name__ == "__main__":
    o = open("../Data/2014-2016-elections-raw.csv", "w")
    # 2016 election data.
    raw = pd.read_excel("http://www.elections.ny.gov/NYSBOE/elections/2016/General/2016Senate.xls")
    df = df_from_raw(raw)
    df['Year'] = "2016"
    df.to_csv(o, header=True)
    raw = pd.read_excel("http://www.elections.ny.gov/NYSBOE/elections/2016/General/2016Assembly.xls")
    df = df_from_raw(raw)
    df['Year'] = "2016"
    df.to_csv(o, header=False)
    raw = pd.read_excel("http://www.elections.ny.gov/NYSBOE/elections/2016/General/2016Congress.xls")
    df = df_from_raw(raw)
    df['Year'] = "2016"
    df.to_csv(o, header=False)
    # 2014 election data.
    raw = pd.read_excel("http://www.elections.ny.gov/NYSBOE/elections/2014/general/2014Senate.xlsx")
    df = df_from_raw(raw)
    df['Year'] = "2014"
    df.head()
    df.to_csv(o, header=False)
    raw = pd.read_excel("http://www.elections.ny.gov/NYSBOE/elections/2014/General/2014Assembly.xlsx")
    df = df_from_raw(raw)
    df['Year'] = "2014"
    df.to_csv(o, header=False)
    raw = pd.read_excel("http://www.elections.ny.gov/NYSBOE/elections/2014/General/2014Congress.xlsx")
    df = df_from_raw(raw)
    df['Year'] = "2014"
    df.to_csv(o, header=False)
    o.close()
    # Enrollment data.
    cols = [
        'District',
        'County',
        'Status',
        'DEM',
        'REP',
        'CON',
        'GRE',
        'WOR',
        'IND',
        'WEP',
        'REF',
        'OTH',
        'BLANK',
        'TOTAL']
    coltypes = {
        'District': str,
        'County': str,
        'Status': str,
        'DEM': np.int32,
        'REP': np.int32,
        'CON': np.int32,
        'GRE': np.int32,
        'WOR': np.int32,
        'IND': np.int32,
        'WEP': np.int32,
        'REF': np.int32,
        'OTH': np.int32,
        'BLANK': np.int32,
        'TOTAL': np.int32}
    district_class_labels = [
        'Very Conservative',
        'Conservative',
        'Neutral',
        'Liberal',
        'Very Liberal']
    senate = pd.read_csv(
        '../Data/tabula-senate_enrollment_nov16.csv',
        header=0,
        names=cols,
        dtype=coltypes,
        thousands=',')
    senate['DemPct'] = senate['DEM'] / senate['TOTAL']
    senate['DistrictClass'] = pd.qcut(
        senate['DemPct'],
        5,
        labels=district_class_labels)
    assembly = pd.read_csv(
        '../Data/tabula-assembly_enrollment_nov16.csv',
        header=0,
        names=cols,
        dtype=coltypes,
        thousands=',')
    assembly['DemPct'] = assembly['DEM'] / assembly['TOTAL']
    assembly['DistrictClass'] = pd.qcut(
        assembly['DemPct'],
        5,
        labels=district_class_labels)
    congress = pd.read_csv(
        '../Data/tabula-congress_enrollment_nov16.csv',
        header=0,
        names=cols,
        dtype=coltypes,
        thousands=',')
    congress['DemPct'] = congress['DEM'] / congress['TOTAL']
    congress['DistrictClass'] = pd.qcut(
        congress['DemPct'],
        5,
        labels=district_class_labels)
    df = pd.read_csv("../Data/2014-2016-elections-raw.csv")
    df.drop('Unnamed: 0', axis=1, inplace=True)

    districts = defaultdict(list)
    for row in df.itertuples():
        districts[row.District].append(row)
    regexp = re.compile('^(\d+).*(CONGRESS|ASSEMBLY|SENATE).*')
    clean = []
    for district in districts.keys():
        new = {}
        total_votes_2014 = 0
        total_votes_2016 = 0
        m = regexp.match(district)
        if m:
            district_num = m.group(1)
            district_type = m.group(2)
        else:
            raise ValueError("Cannot match district " + district)
        for row in districts[district]:
            new['DistrictNum'] = district_num
            new['DistrictType'] = district_type
            if row.Year == 2016:
                enroll_data = {
                    'CONGRESS': congress,
                    'ASSEMBLY': assembly,
                    'SENATE': senate}[district_type]
                new['2016TotalEnrollment'] = enroll_data.loc[
                    (enroll_data['County'] == 'District Total') & (
                        enroll_data['Status'] == 'Total') & (
                        enroll_data['District'] == district_num),
                    'TOTAL'].tolist()[0]
                new['2016DemEnrollment'] = enroll_data.loc[
                    (enroll_data['County'] == 'District Total') & (
                        enroll_data['Status'] == 'Total') & (
                        enroll_data['District'] == district_num),
                    'DEM'].tolist()[0]
                new['2016RepEnrollment'] = enroll_data.loc[
                    (enroll_data['County'] == 'District Total') & (
                        enroll_data['Status'] == 'Total') & (
                        enroll_data['District'] == district_num),
                    'REP'].tolist()[0]
                new['DistrictClass'] = enroll_data.loc[
                    (enroll_data['County'] == 'District Total') & (
                        enroll_data['Status'] == 'Total') & (
                        enroll_data['District'] == district_num),
                    'DistrictClass'].tolist()[0]
                total_votes_2016 += row.Votes
                if row.Party in 'DEM':
                    new['2016DemName'] = row.Name
                    new['2016DemVotes'] = row.Votes
                    new['2016DemWin'] = row.Won
                if row.Party in 'REP + TRPREP/TRP':
                    new['2016RepName'] = row.Name
                    new['2016RepVotes'] = row.Votes
                    new['2016RepWin'] = row.Won
            if row.Year == 2014:
                total_votes_2014 += row.Votes
                if row.Party in 'DEM':
                    new['2014DemName'] = row.Name
                    new['2014DemVotes'] = row.Votes
                    new['2014DemWin'] = row.Won
                if row.Party in 'REP + TRPREP/TRP':
                    new['2014RepName'] = row.Name
                    new['2014RepVotes'] = row.Votes
                    new['2016RepWin'] = row.Won
        new['2016TotalVotes'] = total_votes_2016
        new['2014TotalVotes'] = total_votes_2014
        clean.append(new)

    df2 = pd.DataFrame(clean)
    df2['2016DemMargin'] = df2['2016DemVotes'] - df2['2016RepVotes']
    df2['2016DemMarginPct'] = 100 * \
        df2['2016DemMargin'] / (df2['2016TotalVotes'])
    df2['2014DemMargin'] = df2['2014DemVotes'] - df2['2014RepVotes']
    df2['2014DemMarginPct'] = 100 * \
        df2['2014DemMargin'] / (df2['2014TotalVotes'])
    df2.to_excel("../Data/NY State Senate Election Details.xls")
