"""Standardize a list of addresses using the USPS API.
Multi-threaded, since the API response time is slow.

Get an API key at https://registration.shippingapis.com.
"""

from __future__ import print_function

import threading
import sys
import pandas as pd
from tqdm import tqdm
from collections import deque
from pyusps import address_information

NUM_THREADS = 100


def standardize_address(
        df,
        type='vf',
        col1=None,
        col2=None,
        key=None,
        usps_key=None,
        new_col='standardized_address'):
    """Standardize a list of addresses using the USPS API.
    Arguments:
        df: a DataFrame of data
        type: 'vf' (NY State Voter File)
            or 'raw', two columns
        col1: if using 'raw', column name for first line of address
        col2: if using 'raw', column name for second line of address
        key: if using 'raw', column name for the key to lookup on
        usps_key: USPS API key
        new_col: name of new column to add."""

    threads = deque()
    results = {}
    for obj in tqdm(df.iterrows(), total=df.shape[0]):
        row = obj[1]
        if len(threads) < NUM_THREADS:
            if type == 'vf':
                t = threading.Thread(
                    target=vf_standardize_address, args=(
                        row, results, usps_key))
            elif type == 'raw':
                t = threading.Thread(
                    target=gen_standardize_address, args=(
                        row[col1], row[col2], row[key], results, usps_key))
            else:
                raise Exception("type not recognized")
            t.start()
            threads.append(t)
            continue
        else:
            t = threads.popleft()
            t.join()
            continue

    while threads:
        t = threads.popleft()
        t.join()

    sys.stderr.flush()
    sys.stdout.flush()
    if type == 'vf':
        df[new_col] = df['SBOEID'].map(results)
    elif type == 'raw':
        df[new_col] = df[key].map(results)


def vf_standardize_address(row, results, usps_key):
    """Used for the NY State Voter File only."""
    rhalfcode = '' if pd.isnull(row['RHALFCODE']) else row['RHALFCODE']
    raddnumber = '' if pd.isnull(row['RADDNUMBER']) else row['RADDNUMBER']
    rpredirection = '' if pd.isnull(
        row['RPREDIRECTION']) else row['RPREDIRECTION']
    rstreetname = '' if pd.isnull(row['RSTREETNAME']) else row['RSTREETNAME']
    rpostdirection = '' if pd.isnull(
        row['RPOSTDIRECTION']) else row['RPOSTDIRECTION']
    rapartment = '' if pd.isnull(row['RAPARTMENT']) else row['RAPARTMENT']

    if ('APT' in str(row['RAPARTMENT']).upper()) \
            or ('UNIT' in str(row['RAPARTMENT']).upper()) \
            or (row['RAPARTMENT'] == ''):
        address = "{} {} {} {} {} {}".format(
            raddnumber,
            rhalfcode,
            rpredirection,
            rstreetname,
            rpostdirection,
            rapartment)
    else:
        address = "{} {} {} {} {} APT {}".format(
            raddnumber,
            rhalfcode,
            rpredirection,
            rstreetname,
            rpostdirection,
            rapartment)
    try:
        address = address.upper()
        addr = {'address': address, 'city': row['RCITY'], 'state': 'NY'}
        result = address_information.verify(usps_key, addr)
        zip4 = "-{}".format(result['zip4']) if result['zip4'] else ''
        results[row['SBOEID']] = "{}, {} {} {}{}".format(
            result['address'], result['city'], result['state'], result['zip5'], zip4)
    except Exception:
        results[row['SBOEID']] = address


def gen_standardize_address(addr1, addr2, key, results, usps_key):
    addr = {'address': addr1, 'city': addr2, 'state': 'NY'}
    try:
        result = address_information.verify(usps_key, addr)
        zip4 = "-{}".format(result['zip4']) if ('zip4' in result) and result['zip4'] else ''
        results[key] = "{}, {} {} {}{}".format(
            result['address'],
            result['city'],
            result['state'],
            result['zip5'],
            zip4)
    except Exception as e:
        results[key] = "{}, {}".format(addr1, addr2)
