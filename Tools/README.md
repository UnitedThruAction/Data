# Python tools

This directory has some useful tools for extracting and cleaning up data from civic sources.

* `cache.py` creates a local cache of legislation from the [NY Senate API](http://legislation.nysenate.gov/static/docs/html/index.html) in a CouchDB database for further analysis.  `init_db.sh` and `db-views.json` are used to initialize the database.
