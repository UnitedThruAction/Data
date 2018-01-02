"""A simple Address Formatter pipeline, based on
https://github.com/apache/beam/blob/master/sdks/python/apache_beam/examples/wordcount_minimal.py.

Formats the first 100 rows in a BigQuery table.

TODO:
* Parallelize this, so that it's not single-threaded for each API call
"""

from __future__ import absolute_import

import argparse
import logging
import threading

import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.options.pipeline_options import SetupOptions
from pyusps import address_information
from collections import deque

def vf_standardize_address(row, usps_key, output_arr):
    """Used for the NY State Voter File only."""
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
    try:
        address = address.upper()
        addr = {'address': address, 'city': row['RCITY'], 'state': 'NY'}
        result = address_information.verify(usps_key, addr)
        zip4 = "-{}".format(result['zip4']) if result['zip4'] else ''
        output, err = "{}, {} {} {}{}".format(
            result['address'], result['city'], result['state'], result['zip5'], zip4), None
    except Exception as e:
        output, err = None, str(e)

    output_arr.append({'SBOEID': row['SBOEID'],
            'FMT_ADDR': output,
            'ERR': err})
    return

class StandardizeAddress(beam.DoFn):
    NUM_THREADS = 50

    def start_bundle(self):
        self.threads = deque()
        self.output = deque()

    def push_queue(self, element, usps_key):
        t = threading.Thread(
            target=vf_standardize_address, args=(
                element, usps_key, self.output))
        t.start()
        self.threads.append(t)

    def pop_queue(self):
        for t in self.threads:
            if ~t.is_alive():
                t.join()

        while self.output:
            yield self.output.popleft()

    def process(self, element, usps_key):
        if len(self.threads) < self.NUM_THREADS:
            self.push_queue(element, usps_key)
        else:
            self.pop_queue()
            self.push_queue(element, usps_key)

    def finish_bundle(self):
        for t in self.threads:
            t.join()
        for o in self.output:
            yield o

def run(argv=None):
  """Main entry point; defines and runs the pipeline."""

  parser = argparse.ArgumentParser()
  parser.add_argument('--usps_key',
                      dest='usps_key',
                      default=None,
                      help='USPS API key')
  known_args, pipeline_args = parser.parse_known_args(argv)
  pipeline_args.extend([
      '--runner=DataflowRunner',
      '--project=voterdb-test',
      '--temp_location=gs://nof20-dataflow-temp/',
      '--job_name=addressformatter',
  ])

  if not known_args.usps_key:
      raise Exception("Provide USPS API key.")

  pipeline_options = PipelineOptions(pipeline_args)
  pipeline_options.view_as(SetupOptions).save_main_session = True
  with beam.Pipeline(options=pipeline_options) as p:

    rows = p | beam.io.Read(beam.io.BigQuerySource(
          query='SELECT * FROM NY_State_Voter_List_2017_09_06.ad_75 LIMIT 100;'))

    output = (
        rows
        | 'StandardizeAddress' >> beam.ParDo(StandardizeAddress(), known_args.usps_key)
    )

    output | beam.io.Write(
        beam.io.BigQuerySink(table='NY_State_Voter_List_2017_09_06.addresses_2',
            validate=True,
            schema='SBOEID:STRING,FMT_ADDR:STRING,ERR:STRING'))

    #output | beam.io.WriteToText('gs://output-stats/addresses.txt')

if __name__ == '__main__':
  logging.getLogger().setLevel(logging.INFO)
  run()
