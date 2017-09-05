# Python tools

This directory has some useful tools for extracting and cleaning up data from civic sources.

* `Cache.py` creates a local cache of legislation from the [NY Senate API](http://legislation.nysenate.gov/static/docs/html/index.html) in a CouchDB database for further analysis.  `init_db.sh` and `db-views.json` are used to initialize the database.

* `ElectionData.py` scrapes election data for 2014 and 2016 from the NY Board of Elections website and makes it available in a sensible format.  This includes vote margin, winning candidate, classification of district, etc.

* `IdeologyLeadership.py` calculates "Ideology" and "Leadership" scores
for members of the 2006 New York State Senate, based on bill co-sponsorship.

* `KMLWriter.py` converts Geopandas DataFrames of polygons, e.g. election districts, into KML files for visualization in Google Maps.

* `SuffolkParser.py` processes vote data in fixed-length record format received from Suffolk County Board of Elections and translates into the standard OpenElections CSV format.

* `WriteinSheets.py` generate HTML write-in sheets for volunteers to record voter contact.  Can be quickly and easily printed to PDF inside modern browsers.

* `FuzzyMatch.py` performs a fuzzy match of a dict() of personal attributes against the Voter File.

* `CachingGeocoder.py` is a really simple implementation of a caching geocoder using the
Google Maps Geocoding API, which takes in a Pandas DataFrame of addresses and converts it into a Geopandas GeoDataFrame with points in CRS 84 for each address.
