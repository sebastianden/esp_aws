import boto3
import json
import os
import requests
from typing import Dict
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

iot = boto3.client(
    'iot-data', endpoint_url=os.getenv('IOT_ENDPOINT'))
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.getenv('DYNAMODB_TABLE'))
measurements = ['temperature', 'humidity']
start = 0
end = 100

query_string_params = f'?from={start}&to={end}'

payload = {
    'from': start,
    'to': end
}

expected_response_empty = '{"data": []}'
expected_response_data = '{"data": [[10, 21.0, 50.0]]}'


def test_get(expected_response):
    r = requests.get(os.getenv('API_URL') +
                     os.getenv('LAMBDA_NAME') + query_string_params)
    logging.info(r.text)
    assert r.text == expected_response


def test_post(expected_response):
    r = requests.post(os.getenv('API_URL') +
                      os.getenv('LAMBDA_NAME'), data=json.dumps(payload))
    logging.info(r.text)
    assert r.text == expected_response


def lambda_handler(event: Dict, _) -> Dict:
    try:

        logger.info('Testing empty response')
        # GIVEN a new DynamoDB table
        # WHEN I query the API
        logger.info('Testing GET request')
        test_get(expected_response_empty)

        logger.info('Testing POST request')
        test_post(expected_response_empty)
        # THEN I get an empty response

        logger.info('Publishing dummy messages')
        # GIVEN a table with sample items
        # Publish sample message containing temperature data
        iot.publish(
            topic=os.getenv('TOPIC'),
            qos=1,
            payload=json.dumps({'measurement': 'temperature',
                                'value': 21,
                                'timestamp': 10,
                                'uom': '°C'})
        )

        # Publish sample message containing temperature data
        iot.publish(
            topic=os.getenv('TOPIC'),
            qos=1,
            payload=json.dumps({'measurement': 'humidity',
                                'value': 50,
                                'timestamp': 10,
                                'uom': '%'})
        )

        # WHEN I query the API
        # THEN I get the expected response
        logger.info('Testing GET request')
        test_get(expected_response_data)

        logger.info('Testing POST request')
        test_post(expected_response_data)

        status = 200
        message = 'Integration tests successful'

    except AssertionError:
        status = 400
        message = 'Integration test failed. Unexpected result.'

    # Clean up (delete dummy elements from dynamodb)
    for m in measurements:
        table.delete_item(Key={'measurement': m, 'timestamp': 10})
    logger.info('Cleaning up successful. Removed dummy entries.')

    return {
        'statusCode': status,
        'body': json.dumps({
            'message': message})
    }
