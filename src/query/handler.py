import json
import os

import boto3

import sagemaker_handler as sh

table_name = os.environ['FLIGHTINFO_TABLE_NAME']
model_name = 'model_name'

boto3.setup_default_session(profile_name='default')
dynamodb = boto3.resource('dynamodb')


def handler(event, context):
    item = json.loads(event['body'])
    print(item['flight_id'])
    # get flight_id from event
    flight_id = item['flight_id']
    query_params = item['query_params']

    return sh.make_prediction(flight_id, query_params)
