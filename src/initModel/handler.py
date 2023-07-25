# This program is a Lambda function to load a json file from S3 bucket and generate a dataTable on dynamodb.
import datetime
import json
import os

import boto3

import sagemaker_handler as sh


bucket_name = os.environ['DATASOURCE_BUCKET_NAME']
json_file_name = 'testdata'
table_name = os.environ['FLIGHTINFO_TABLE_NAME']
model_name = 'model_name'

dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')


# use boto3 to load json file from S3 bucket
def load_json_file_from_s3():
    s3_object = s3.get_object(Bucket=bucket_name, Key=json_file_name)
    json_file = json.loads(s3_object['Body'].read())
    return json_file


# use boto3 to load json to dynamodb table
def load_dynamodb_table(json_file, flight_id):
    table = dynamodb.Table(table_name)
    now = datetime.datetime.now()
    expiration = now + datetime.timedelta(days=30)
    for item in json_file:
        item['flight_id'] = flight_id
        item['timestamp'] = now.strftime("%Y-%m-%d %H:%M:%S")
        item['expiration'] = expiration.strftime("%Y-%m-%d %H:%M:%S")
        table.put_item(Item=item)


def handler(event, context):
    print("print all event information")
    item = json.loads(event['body'])
    print(item['flight_id'])
    flight_id = item['flight_id']
    data_source = load_json_file_from_s3()
    load_dynamodb_table(data_source, flight_id)
    sh.load_model(model_name)
    return {
        'statusCode': 200,
        'body': json.dumps('Initialization successfully')
    }
