#!/bin/sh 

#TODO: Use hostname/port from .ini file

curl -X DELETE 'http://localhost:5984/united-thru-action'

curl -X PUT 'http://localhost:5984/united-thru-action'

#curl -X DELETE 'http://localhost:5984/united-thru-action/_design/db-views'

curl -X PUT -d @db-views.json 'http://localhost:5984/united-thru-action/_design/db-views'
