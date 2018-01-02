from google.cloud import pubsub, bigquery
import time
import os
import json
import logging

def format_address(row):
    rhalfcode = '' if not row['RHALFCODE'] else row['RHALFCODE']
    raddnumber = '' if not row['RADDNUMBER'] else row['RADDNUMBER']
    rpredirection = '' if not row['RPREDIRECTION'] else row['RPREDIRECTION']
    rstreetname = '' if not row['RSTREETNAME'] else row['RSTREETNAME']
    rpostdirection = '' if not row['RPOSTDIRECTION'] else row['RPOSTDIRECTION']
    rapartment = '' if not row['RAPARTMENT'] else row['RAPARTMENT']

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
    return address

def run(usps_key):
    publisher = pubsub.PublisherClient()
    logging.info("Starting up")

    topic = "projects/{}/topics/address_requests".format(project)
    topics = []
    for t in publisher.list_topics("projects/{}".format(project)):
        topics.append(t.name)
    logging.info("Existing topics: {}".format(topics))
    if topic not in topics:
        logging.info("Creating new topic {}".format(topic))
        topic = publisher.create_topic(topic)
    else:
        logging.info("Using existing topic")

    client = bigquery.Client(project=project)
    QUERY = (
        "SELECT * FROM NY_State_Voter_List_2017_09_06.ad_75 "
        "LIMIT 100;"
    )
    query_job = client.query(QUERY)
    for row in query_job.result():
        address = format_address(row)
        request = {'address': address,
            'city': row['RCITY'],
            'usps_key': usps_key}
        jj = json.dumps(request)
        logging.info("About to publish: {}".format(jj))
        publisher.publish(topic, jj)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    usps_key = os.environ['USPS_KEY']
    if not usps_key:
        raise Exception("Provide USPS_KEY in environment variables")
    project = "voterdb-test"
    run(usps_key)
