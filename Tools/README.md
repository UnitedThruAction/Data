# Python tools

This directory has some useful tools for extracting and cleaning up data from civic sources.

* `Cache.py` creates a local cache of legislation from the [NY Senate API](http://legislation.nysenate.gov/static/docs/html/index.html) in a CouchDB database for further analysis.  `init_db.sh` and `db-views.json` are used to initialize the database.

* `ElectionData.py` scrapes election data for 2014 and 2016 from the NY Board of Elections website and makes it available in a sensible format.  This includes vote margin, winning candidate, classification of district, etc.

* `IdeologyLeadership.py` calculates "Ideology" and "Leadership" scores
for members of the 2006 New York State Senate, based on bill co-sponsorship.
