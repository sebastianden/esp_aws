from multiprocessing import get_logger
import boto3
import json
import os
import requests
from typing import Dict
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

iot = boto3.client('iot')
dynamodb = boto3.client('dynamodb')
table = dynamodb.Table(os.getenv('DYNAMODB_TABLE'))
measurements = ['temperature', 'humidity']
start = 0
end = 100
expected_response = '{"data": [[10, 20.0, 50.0], [12, 20.0, 50.0]]}'


def lambda_handler(event: Dict, _) -> Dict:

    logger.info("Publishing dummy messages")
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

    try:
        logger.info("Testing GET request")
        # Test GET request
        query_string_params = f'?from={start}&to={end}'
        r = requests.get(os.getenv('API_URL') +
                         os.getenv('LAMBDA_NAME') + query_string_params)

        assert r.text == expected_response

        logger.info("Testing POST request")
        # Test POST request
        payload = {
            'from': start,
            'to': end
        }
        r = requests.post(os.getenv('API_URL') +
                          os.getenv('LAMBDA_NAME'), data=json.dumps(payload))

        assert r.text == expected_response

        # Clean up (delete elements from dynamodb)
        for m in measurements:
            response = table.delete_item(Key={
                'measurement': m,
                'timestamp': 10
            })
            logger.info(
                f"Cleaning up successful. Removed dummy entries: {response}")

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Integration tests successful'})
        }

    except Exception as e:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'message': f'Integration tests failed: {e}'})
        }
