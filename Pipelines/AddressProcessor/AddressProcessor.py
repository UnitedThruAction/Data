"""A Python app to service US address distributed formatting requests."""

from pyusps import address_information
from google.cloud import pubsub
import time
import json
import logging


def gen_standardize_address(address, city, usps_key):
    addr = {'address': address, 'city': city, 'state': 'NY'}
    res = address_information.verify(usps_key, addr)
    zip4 = "-{}".format(res['zip4']) if res['zip4'] else ''
    return "{}, {}, {} {}{}".format(res['address'], res['city'], res['state'], res['zip5'], zip4)


def callback(message):
    try:
        msg = message.data.decode("utf-8")
        logging.info("Got message: {}".format(msg))
        obj = json.loads(msg)
        output = gen_standardize_address(obj['address'], obj['city'], obj['usps_key'])
        logging.info("Got output: {}".format(output))
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
