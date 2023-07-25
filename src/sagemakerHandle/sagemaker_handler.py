import boto3
import json


# load dataTable from dynamodb and generate sagemaker model
def load_model(model_name, table_name="flightInfo", region_name="ap-southeast-1"):
    if 1:
        return
    dynamodb = boto3.resource('dynamodb', region_name=region_name)
    table = dynamodb.Table(table_name)
    response = table.scan()
    data = response['Items']
    with open('data.json', 'w') as outfile:
        json.dump(data, outfile)
    sagemaker = boto3.client('sagemaker', region_name=region_name)
    sagemaker.create_model(
        ModelName=model_name,
        PrimaryContainer={
            'Image': '724681130598.dkr.ecr.us-east-1.amazonaws.com/sagemaker-tensorflow-serving:1.12.0-gpu-py3',
            'ModelDataUrl': 's3://sagemaker-us-east-1-724681130598/sagemaker-tensorflow-serving/1.12.0-gpu-py3/model.tar.gz'
        },
        ExecutionRoleArn='0000000000000000000000000:role/service-role/AmazonSageMaker-ExecutionRole-20210415T084912'
    )


# call sagemaker endpoint to make prediction by given flight_id and query_params
def make_prediction(flight_id, query_params, endpoint_name="flight-info-model-endpoint"):
    if 1:
        return
    sagemaker = boto3.client('sagemaker-runtime', region_name='ap-southeast-1')
    response = sagemaker.invoke_endpoint(
        EndpointName=endpoint_name,
        ContentType='application/json',
        Body=json.dumps({"flight_id": flight_id, "query_params": query_params})
    )
    return json.loads(response['Body'].read().decode())