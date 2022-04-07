import boto3
import json
import os
import requests
from typing import Dict
import logging
import time

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

iot = boto3.client(
    'iot-data', endpoint_url=os.getenv('IOT_ENDPOINT'))
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.getenv('DYNAMODB_TABLE'))

start = 0
end = 100
device = 'test'

query_string_params = f'?from={start}&to={end}&device={device}'
payload = {
    'from': start,
    'to': end,
    'device': device
}


def test_request(method: str):
    if method == 'GET':
        r = requests.get(os.getenv('API_URL') +
                         os.getenv('LAMBDA_NAME') + query_string_params)
        logging.info(r.text)
        return r.text
    if method == 'POST':
        r = requests.post(os.getenv('API_URL') +
                          os.getenv('LAMBDA_NAME'), data=json.dumps(payload))
        logging.info(r.text)
        return r.text


def lambda_handler(event: Dict, _) -> Dict:
    try:
        if event['data']:
            for data in event['data']:
                iot.publish(topic=os.getenv('TOPIC'),
                            qos=1, payload=json.dumps(data))
            logger.info('Published dummy events')
            # Wait a short time to allow the IoT rule to process the message
            time.sleep(1)

        response = test_request(event['method'])

        # Clean up (delete dummy elements from dynamodb)
        if event['data']:
            for m in event['data']:
                table.delete_item(
                    Key={'measurement': m['measurement'], 'timestamp': m['timestamp']})
            logger.info('Cleaning up successful. Removed dummy entries.')
    except Exception as e:
        logger.exception(f'Unknown error. Integration test failed. {e}')

    return {
        'statusCode': 200,
        'body': json.dumps(response)
    }
