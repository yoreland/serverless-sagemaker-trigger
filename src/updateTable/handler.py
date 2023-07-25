import datetime
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
    # get timestamp from event
    timestamp = item['timestamp']
    data = item['data']
    key = query_nearest_record(timestamp, flight_id)
    if key is None:
        return {
            'statusCode': 200,
            'body': json.dumps('No record found')
        }
    else:
        # delete the record by given primary key
        table = dynamodb.Table(table_name)
        table.delete_item(
            Key={
                'id': key
            }
        )
    insert_record(data, timestamp, flight_id)
    sh.load_model(model_name)
    return {
        'statusCode': 200,
        'body': json.dumps('Update successfully')
    }


# query the nearest record in dynamodb by given a timestamp, and where the flight_id equals to the given flight_id
def query_nearest_record(timestamp, flight_id):
    table = dynamodb.Table(table_name)
    response = table.query(
        KeyConditionExpression='flight_id = :flight_id AND timestamp <= :timestamp',
        ExpressionAttributeValues={
            ':flight_id': flight_id,
            ':timestamp': timestamp
        },
        ScanIndexForward=False,
        Limit=1
    )
    # get primary key of response, if response is empty, return None
    if len(response['Items']) == 0:
        return None
    else:
        return response['Items'][0]['id']['S']


# insert a record into dynamodb by given data
def insert_record(item, timestamp, flight_id):
    table = dynamodb.Table(table_name)
    expiration = timestamp + datetime.timedelta(months=1)
    item['flight_id'] = flight_id
    item['timestamp'] = timestamp.strftime("%Y-%m-%d %H:%M:%S")
    item['expiration'] = expiration.strftime("%Y-%m-%d %H:%M:%S")
    table.put_item(
        Item={item}
    )
