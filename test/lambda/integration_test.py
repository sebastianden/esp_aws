import boto3
import json
import os
import requests
from typing import Dict

client = boto3.client('iot-data')

start = 0
end = 100
expected_response = '{"data": [[10, 20.0, null], [12, 20.0, null]]}'


def lambda_handler(event: Dict, _) -> Dict:

    # Publish sample message containing temperature data
    client.publish(
        topic=os.getenv('TOPIC'),
        qos=1,
        payload=json.dumps({'measurement': 'temperature',
                            'value': 21,
                            'timestamp': 10,
                            'uom': '°C'})
    )

    # Publish sample message containing temperature data
    client.publish(
        topic=os.getenv('TOPIC'),
        qos=1,
        payload=json.dumps({'measurement': 'temperature',
                            'value': 50,
                            'timestamp': 10,
                            'uom': '%'})
    )

    try:
        # Test GET request
        query_string_params = f'?from={start}&to={end}'
        r = requests.get(os.getenv('API_URL') +
                         os.getenv('LAMBDA_NAME') + query_string_params)

        assert r.text == expected_response

        # Test POST request
        payload = {
            'from': start,
            'to': end
        }
        r = requests.post(os.getenv('API_URL') +
                          os.getenv('LAMBDA_NAME'), data=json.dumps(payload))

        assert r.text == expected_response

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Integration tests successful'})
        }

    except AssertionError as e:
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': f'Integration tests failed: {e}'})
        }
