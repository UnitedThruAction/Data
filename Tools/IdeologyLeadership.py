"""Calculate ideology and leadership scores for the NY State Senate.

Approach copied from https://www.govtrack.us/about/analysis#ideology.
"Ideology" is calculated using principal component analysis, i.e. the reduction
of the cosponsorship network to one dimension.  "Leadership" is calculated
using eigenvector centrality, i.e. a measure of how central a legislator is in
the cosponsorship network, as famously used in Google PageRank. This is better
than a simple count of cosponsors, as it avoids distortion by e.g. two extreme
legislators constantly sponsoring each other.

Uses local CouchDB cache of bills.  See Cache.py.

Input: NY State Senate API key.  See docs & get API key here:
http://legislation.nysenate.gov/static/docs/html/index.html.  Pass API key
as first argument to this script.

Output: ../Data/2016 State Senate Leadership Analysis.xls and
../Data/2016 State Senate Vulnerability Matrix.xls
"""

import sys
import couchdb
from collections import defaultdict
import numpy as np
import pandas as pd
import networkx as nx

from Cache import Cache

if len(sys.argv) < 2:
    print("Provide API key as first argument.")
    sys.exit(1)

api_key = sys.argv[1]

print("Connecting to CouchDB and refreshing 2016 bills from API.")
try:
    server = couchdb.Server()
    db = server['united-thru-action']
    db_cache = Cache(api_key)
    # db_cache.reconcile("2016") # Load 2016 bills into cache
except ConnectionRefusedError:
    print("Launch CouchDB and restart.")
    sys.exit(1)

# Create asymmetric co-sponsorship matrix and member list
print("Creating asymmetric co-sponsorship matrix and member list")
sponsorgroups = []
members = defaultdict(int)
for doc in db.view('db-views/by_year')["2016"]:
    bill = doc.value
    sponsordict = {}
    if bill['billType']['chamber'] == 'SENATE':
        if 'sponsor' in bill:
            if 'member' in bill['sponsor'] and bill[
                    'sponsor']['member'] is not None:
                name = bill['sponsor']['member']['shortName'].title()
                sponsordict['sponsor'] = name
                members[name] += 1
        if 'amendments' in bill:
            if 'items' in bill['amendments']:
                keys = list(bill['amendments']['items'].keys())
                amd_key = keys[-1]
                if 'coSponsors' in bill['amendments']['items'][amd_key]:
                    cosponsors = [n['shortName'].title() for n in bill['amendments']['items'][
                        amd_key]['coSponsors']['items']]
                    sponsordict['cosponsors'] = cosponsors
                    for cosponsor in cosponsors:
                        members[cosponsor] += 1
    sponsorgroups.append(sponsordict)

member_list = list(members.keys())
sz = len(member_list)
arr = np.zeros((sz, sz))
for sponsordict in sponsorgroups:
    if 'sponsor' in sponsordict and 'cosponsors' in sponsordict:
        sponsor = sponsordict['sponsor']
        for cosponsor in sponsordict['cosponsors']:
            arr[member_list.index(sponsor), member_list.index(cosponsor)] += 1

# Principal component analysis
print("Principal component analysis")
u, s, vT = np.linalg.svd(arr)
axis_one = vT[1, :]
members_by_axis_one = sorted(
    [z for z in zip(member_list, -1 * axis_one)], key=lambda z: -1 * z[1])

# Get party from elections Data
elections = pd.read_csv('../Data/2014-2016-elections-raw.csv')


def get_party(year, name):
    df = elections.loc[elections['Name'].apply(lambda x: name in x)]
    ll = df.loc[df['Year'] == year, 'Party'].tolist()
    return ll[0] if ll else ""

# Segregate members
new = [{'Name': t[0], 'Party':get_party(2016, t[0]), 'IdeologyScore':t[
    1]} for t in members_by_axis_one]
df = pd.DataFrame(new)
labels = [
    'Very Liberal',
    'Liberal',
    'Neutral',
    'Conservative',
    'Very Conservative']
df['IdeoLabel'] = pd.qcut(df['IdeologyScore'], 5, labels)
df['Name'] = df.apply(lambda row: row['Name'].title(), axis=1)

# Fill gaps in election data and prepare data frame
missing_party = {'Defrancisco': 'REP', 'Nozzolio': 'REP', 'Lavalle': 'REP',
                 'Farley': 'REP', 'Panepinto': 'REP', 'Skelos': 'REP',
                 'Libous': 'DEM', 'Sampson': 'DEM', 'Hassell-Thompson': 'DEM'}

df['Party'] = df.apply(lambda row: missing_party[row['Name']] if row[
                       'Party'] == "" else row['Party'], axis=1)
df.set_index('Name', inplace=True)

# Calculate leadership (eigenvector centrality) scores
print("Calculating leadership (eigenvector centrality) scores")
G = nx.DiGraph(arr)
centrality = nx.eigenvector_centrality(G)
df2 = pd.DataFrame([{'Name': m, 'LeadershipScore': centrality[i]}
                    for i, m in enumerate(member_list)])
df2['Name'] = df2.apply(lambda row: row['Name'], axis=1)
df2.set_index('Name', inplace=True)
df3 = df2.join(df).sort_values('LeadershipScore')
df3['LeaderLabel'] = pd.qcut(
    df3['LeadershipScore'], 3, [
        "Low Leadership", "Moderate Leadership", "High Leadership"])

# Handle IDC as separate caucus.
idc_members = [
    'Alcantara',
    'Avella',
    'Carlucci',
    'Felder',
    'Hamilton',
    'Klein',
    'Peralta',
    'Savino',
    'Valesky']
df3['Party'] = df3.apply(
    lambda row: 'IDC' if row.name in idc_members else row.Party,
    axis=1)

# Write to Excel.
df3.to_excel('../Data/2016 State Senate Leadership Analysis.xls')

# Calculate 5 x 5 matrix ("25-Box Score") of member vs. district ideology.
print("Calculating 5 x 5 matrix ('25-Box Score') of member vs. district ideology.")
elections = pd.read_excel('../Data/2016 NY State Election Details.xls')


def get_district_class(name, party):
    if party == 'DEM' or party == 'IDC':
        ll = elections.loc[
            elections.apply(
                lambda row: (
                    row['2014DemWin'] == 1) and row['DistrictType'] == 'SENATE' and (
                    name in str(
                        row['2014DemName']).title()),
                axis=1),
            'DistrictClass'].tolist()
        if len(ll) == 1:
            return ll[0]
        elif len(ll) == 0:
            return ""
        else:
            raise KeyError("Multiple rows for {}, {}".format(name, party))
    if party == 'REP':
        ll = elections.loc[
            elections.apply(
                lambda row: (
                    row['2014DemWin'] != 1) and row['DistrictType'] == 'SENATE' and (
                    name in str(
                        row['2014RepName']).title()),
                axis=1),
            'DistrictClass'].tolist()
        if len(ll) == 1:
            return ll[0]
        elif len(ll) == 0:
            return ""
        else:
            raise KeyError(
                "Zero or multiple rows for {}, {}".format(
                    name, party))
df3['DistrictLabel'] = df3.apply(
    lambda row: get_district_class(
        row.name, row['Party']), axis=1)

missing_districts = {
    'Libous': 'Conservative',
    'Kaminsky': 'Neutral',
    'Persaud': 'Very Liberal',
    'Akshar': 'Conservative',
    'Hassell-Thompson': 'Very Liberal',
    'Panepinto': 'Liberal'}

df3['DistrictLabel'] = df3.apply(lambda row: row['DistrictLabel'] if row[
                                 'DistrictLabel'] != "" else missing_districts[row.name], axis=1)
member_dict = defaultdict(lambda: defaultdict(str))
for row in df3.reset_index().iterrows():
    cols = row[1]
    member_dict[cols['IdeoLabel']][cols['DistrictLabel']
                                   ] += '{} ({})\n'.format(cols['Name'], cols['Party'][0])

df4 = pd.DataFrame(member_dict)
df4.to_excel('../Data/2016 State Senate Vulnerability Matrix.xls')
