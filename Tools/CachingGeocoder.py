"""A very simple implementation of a caching geocoder using the Google Maps
(community-supported) Web Services Geocoding API.

Input:  1. Pandas dataframe containing a column named 'address_string'
        2. Google Maps API key.  See https://goo.gl/XSBqid

Output: Geopandas geodataframe containing a geometry column, made up of points
in CRS 84 coordinates.

A very simple, append-only cache is implemented in a CSV on the local disk.

@author n.o.franklin@gmail.com
@date 2017-09-04
"""

import sys
import googlemaps
import json
import pandas as pd
import geopandas as gpd
from tqdm import tqdm
from shapely.geometry import Point
from shapely.geometry import mapping, shape


def create_geodf(df, api_key):
    # Populate cache
    try:
        geolog = pd.read_csv('geolocation_log.csv',
                             header=None, error_bad_lines=False,
                             names=['address_string', 'point_json'], quotechar="'")
        geolog.drop_duplicates(inplace=True)
        cache = {}
        for index, row in geolog.iterrows():
            cache[row.address_string] = shape(json.loads(row.point_json))

        print "Loaded " + str(len(cache)) + " into cache"
    except IOError:
        cache = {}
        print "No log found, continuing with empty cache"
    sys.stdout.flush()
    sys.stderr.flush()

    # Now iterate through
    gmaps = googlemaps.Client(key=api_key)
    log = open('geolocation_log.csv', 'a+')
    cache_hits, cache_misses = 0, 0
    geometry_col = []
    for index, row in tqdm(df.iterrows(), total=len(df)):
        point = None
        if row.address_string:
            if row.address_string in cache:
                point = cache[row.address_string]
                cache_hits += 1
            else:
                geocode_result = gmaps.geocode(row.address_string)
                cache_misses += 1
                if geocode_result:
                    point = Point(geocode_result[0]['geometry']['location']['lng'],
                                  geocode_result[0]['geometry']['location']['lat'])
                    try:
                        log.write("".join(["'", row.address_string,
                                       "','", json.dumps(mapping(point)), "'\n"]))
                    except TypeError:
                        print "Error writing to log, continuing"
                    cache[row.address_string] = point
        geometry_col.append(point)
    log.close()
    sys.stdout.flush()
    sys.stderr.flush()

    print str(cache_hits) + " cache hits, " + str(cache_misses) + " cache misses"

    return gpd.GeoDataFrame(
        df,
        crs={
            'init': 'epsg:4326'},
        geometry=geometry_col)
