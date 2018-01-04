"""A Python app to service US address distributed formatting requests.

This:
* Subscribes on a Cloud Pub/Sub topic called "address_requests"
* Deserializes the JSON message into a Python object
* Uses data in the object to make a call to the USPS Address Lookup API
* Saves results to a BigQuery table called "test_dest"

This uses Google App Default Credentials.  To run on GKE, see:
https://cloud.google.com/kubernetes-engine/docs/tutorials/authenticating-to-cloud-platform

"""

from pyusps import address_information
from google.cloud import pubsub, bigquery
import time
import json
import logging

# PEP 318
def singleton(cls):
    instances = {}
    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return getinstance()

@singleton
class BQHelper(object):

    def __init__(self):
        self.client = bigquery.Client()
        self.dset = self.client.get_dataset(bigquery.DatasetReference('voterdb-test', 'NY_State_Voter_List_2017_09_06'))
        self.tab =  self.client.get_table(bigquery.TableReference(self.dset, "test_dest"))

    def store(self, address, city, output):
        ROWS = [
            (address, city, output)
        ]
        errors = self.client.create_rows(self.tab, ROWS)
        if errors is not []:
            raise Exception("Error saving to BigQuery: {}".format(str(errors)))


def gen_standardize_address(address, city, usps_key):
    addr = {'address': address, 'city': city, 'state': 'NY'}
    res = address_information.verify(usps_key, addr)
    zip4 = "-{}".format(res['zip4']) if res['zip4'] else ''
    return "{}, {}, {} {}{}".format(res['address'], res['city'], res['state'], res['zip5'], zip4)


def callback(message):
    try:
        msg = message.data.decode("utf-8")
        logging.debug("Got message: {}".format(msg))
        obj = json.loads(msg)
        output = gen_standardize_address(obj['address'], obj['city'], obj['usps_key'])
        logging.debug("Got output: {}".format(output))
        BQHelper.store(obj['address'], obj['city'], output)
        message.ack()
    except Exception as err:
        logging.error("Caught error: {}".format(str(err)))
        message.ack()


def run():
    subscriber = pubsub.SubscriberClient()
    project = "voterdb-test"
    topic_name = "projects/{}/topics/address_requests".format(project)
    sub_name = "projects/{}/subscriptions/address_requests".format(project)
    subs = []
    for s in subscriber.list_subscriptions("projects/{}".format(project)):
        subs.append(s.name)
    logging.info("Existing subscriptions: {}".format(subs))
    if sub_name not in subs:
        logging.info("Creating new subscription")
        subscriber.create_subscription(sub_name, topic_name)
    else:
        logging.info("Using existing subscription")

    subscription = subscriber.subscribe(sub_name)
    future = subscription.open(callback)

    while True:
        time.sleep(1)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run()
