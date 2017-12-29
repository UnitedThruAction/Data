"""A simple example to count the number of people in each ED.

See https://beam.apache.org/get-started/wordcount-example/
https://cloud.google.com/dataflow/docs/quickstarts/quickstart-python

NB: APIs must be enabled and GCS buckets created first.
"""

import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions

class ExtractED(beam.DoFn):

    def process(self, element):
        yield element['ED']


pipeline = beam.Pipeline(options=PipelineOptions())

rows = pipeline | beam.io.Read(beam.io.BigQuerySource(
      query='SELECT ED FROM NY_State_Voter_List_2017_09_06.ad_75'))

counts = (
    rows
    | 'ExtractED' >> beam.ParDo(ExtractED())
    | 'Count.PerElement' >> beam.combiners.Count.PerElement()
    | 'Map' >> beam.Map(lambda count: '%s: %s' % (count[0], count[1]))
    | beam.io.WriteToText('gs://output-stats/counts.txt')
)

result = pipeline.run()
result.wait_until_finish()
