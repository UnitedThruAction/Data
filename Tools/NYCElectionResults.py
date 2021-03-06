"""Download NYC election results from the Board of Elections website.

@author n.o.franklin (at) gmail.com
@date 2018-01-20

This code is governed by the Apache License at http://www.apache.org/licenses/LICENSE-2.0.txt.
Copyright 2018 Google.

"""

import csv
import logging
import pandas as pd
import re
import sys

from bs4 import BeautifulSoup
from requests import get
from tqdm import tqdm

SPECIAL_TYPES = ['Absentee / Military',
                 'Absentee/Military',
                 'Public Counter',
                 'Scattered',
                 'Manually Counted Emergency',
                 'Special Presidential',
                 'Emergency',
                 'Affidavit',
                 'Federal',
                 'Yes',
                 'No']

URLS = [
    'http://vote.nyc.ny.us/html/results/results.shtml', # 2018
    'http://vote.nyc.ny.us/html/results/2017.shtml',
    'http://vote.nyc.ny.us/html/results/2016.shtml',
    'http://vote.nyc.ny.us/html/results/2015.shtml',
    'http://vote.nyc.ny.us/html/results/2014.shtml'
]

def download_parse(url):
    logging.info("Downloading {}".format(url))
    response = get(url)
    logging.info(
        "Got {:0,.0f} kb, parsing.".format(
            sys.getsizeof(
                response.text) /
            1024))
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "lxml")

    # Step through all links in page and find CSVs
    urls = []
    for link in soup.find_all('a', href=True):
        href = link['href']
        if '.csv' in href:
            if href[0] == '/':
                urls.append(u"http://vote.nyc.ny.us{}".format(href))
            else:
                urls.append(
                    u"http://vote.nyc.ny.us/html/results/{}".format(href))

    # Download each CSV and append results to list
    logging.info("Downloading and parsing individual CSVs.")
    recap_output, ed_output = [], []
    for url in tqdm(urls):
        response = get(url)
        response.raise_for_status()
        lines = response.text.encode('utf-8').splitlines()
        reader = csv.DictReader(lines)
        for row in reader:
            #if 'Recap' in url:
            #    recap_output.append(row)
            if 'EDLevel' in url:
                ed_output.append(row)
    logging.info("Got {} precinct-level results.".format(len(ed_output)))

    # Convert to DataFrame
    return pd.DataFrame(ed_output).rename(
        columns={
            'District Key': 'DistrictKey',
            'EDAD Status': 'EDADStatus',
            'Office/Position Title': 'OfficePositionTitle',
            'Party/Independent Body': 'PartyIndependentBody',
            'Unit Name': 'UnitName'})


def get_date(row):
    m = re.match(r'(.*) - (\d{2})/(\d{2})/(\d{4})', row['Event'])
    if m:
        return "{}{}{}".format(m.group(4), m.group(2), m.group(3))
    else:
        return None


def get_election_type(row):
    m = re.match(r'(.*) Election.*(\d{2})/(\d{2})/(\d{4})', row['Event'])
    if m:
        return m.group(1).lower()
    m = re.match(r'(.*) - .*', row['Event'])
    if m:
        return m.group(1).lower().replace(' ', '_')
    else:
        return "special"


def get_candidate(row):
    if (row['election_type'] == 'primary') or (row['UnitName'] in SPECIAL_TYPES):
        return row['UnitName']
    else:
        m = re.match(r"(.*)\W+\((.*)\)", row['UnitName'].strip())
        if m:
            return m.group(1)
        else:
            return row['UnitName'].strip()


def get_party(row):
    if row['election_type'] == 'primary':
        if 'PartyIndependentBody' in row:
            return row['PartyIndependentBody']
        if 'Party/Independent Body' in row:
            return row['Party/Independent Body']
        else:
            return None
    if row['UnitName'] in SPECIAL_TYPES:
        return None
    else:
        m = re.match(r"(.*)\W+\((.*)\)", row['UnitName'])
        if m:
            return m.group(2)
        else:
            return None


def get_transformed_df(df, filename):
    output = df.loc[df['filename'] == filename,
                    ['County',
                     'precinct',
                     'OfficePositionTitle',
                     'DistrictKey',
                     'candidate',
                     'party',
                     'Tally']].rename(columns={'County': 'county',
                                                'OfficePositionTitle': 'office',
                                                'DistrictKey': 'district',
                                                'Tally': 'votes'})
    return output.drop_duplicates()


def run():
    for url in URLS:
        df = download_parse(url)
        logging.info("Converting dates.")
        df['date'] = df.apply(get_date, axis=1)
        logging.info("Converting election types.")
        df['election_type'] = df.apply(get_election_type, axis=1)
        logging.info("Generating filenames.")
        df['filename'] = df.apply(lambda row: "{}__ny__{}__{}__precinct.csv".format(
            row['date'], row['election_type'], row['County'].lower().replace(' ', '_')), axis=1)
        logging.info("Converting precinct codes.")
        df['precinct'] = df.apply(lambda row: "{:03.0f}/{:02.0f}".format(
            int(row['ED']), int(row['AD'])), axis=1)
        logging.info("Converting candidate names.")
        df['candidate'] = df.apply(lambda row: get_candidate(row), axis=1)
        logging.info("Converting party names.")
        df['party'] = df.apply(lambda row: get_party(row), axis=1)
        files = df.loc[:, 'filename'].drop_duplicates()
        logging.info("Writing files.")
        for filename in tqdm(files):
            output = get_transformed_df(df, filename)
            output.to_csv(filename, index=False, encoding='utf-8')


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    run()
