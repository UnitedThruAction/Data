# PrecinctData

This tool builds a database of voting history, and basic demographic information,
from several sources:

* Precinct by precinct voting history from the OpenElections Project
* Precinct (Election District) information from the 2010 Redistricting Census,
as distributed by the New York State Legislative Taskforce on demographic
research and reapportionment (LATFOR) website

Input files are processed and intermediate results stored in JSON documents in
a local CouchDB database.

The goal is to output:

* Interactive, online maps allowing analysis by volunteers
* Target lists of precincts for canvassing/phone banking.

To get setup and start working:

* Install a Scientific Python distribution, e.g. [Anaconda](https://www.continuum.io/downloads)
* [Download CouchDB](http://couchdb.apache.org) and run locally.
* Install the CouchDB Python library, e.g. `$ pip install CouchDB`
* Run `$ python PrecinctData.py` to load, process and print results.
