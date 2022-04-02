import os
import json
import boto3
from boto3.dynamodb.conditions import Key
from typing import Dict, List

# TODO: Clean up rearranging logic, maybe just return dict? {timestamps: [...], temperature: [...], humidity: [...]}

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.getenv('DYNAMODB_TABLE'))
measurements = ['temperature', 'humidity']


def query_measurements(start: str, end: str) -> Dict:
    """
    Query DynamoDB for temperature and humidity measurements.

    Parameters
    ----------
    start: str
        Start timestamp

    end: str
        End timestamp

    Returns
    -------
    dict: Results of queries
    """
    query_results = {}

    for m in measurements:
        query_results[m] = table.query(
            KeyConditionExpression=Key('measurement').eq(m) & Key(
                'timestamp').between(int(start), int(end))
        )

    return query_results


def format_results(query_results: Dict) -> List:
    """
    Arrange the query results into a list of lists. Each sub-list consists of
    three items: Timestamp, temperature and humidity. Missing values are filled
    with null values

    TODO: Write unit tests


    Parameters
    ----------
    query_results: dict
        Results of queries

    Returns
    -------
    list: Formatted results as list of lists
    """
    timestamp_t = [int(item['timestamp'])
                   for item in query_results['temperature']['Items']]
    temperature = [float(item['value'])
                   for item in query_results['temperature']['Items']]
    timestamp_h = [int(item['timestamp'])
                   for item in query_results['humidity']['Items']]
    humidity = [float(item['value'])
                for item in query_results['humidity']['Items']]
    timestamp = list(set(timestamp_t + timestamp_h))

    data = []
    for t in sorted(timestamp):
        if t in timestamp_t:
            temp = temperature[timestamp_t.index(t)]
        else:
            temp = None
        if t in timestamp_h:
            hum = humidity[timestamp_h.index(t)]
        else:
            hum = None
        data.append([t, temp, hum])

    return data


def lambda_handler(event: Dict, _) -> Dict:

    if event["httpMethod"] == "POST":
        req = json.loads(event['body'])
    elif event["httpMethod"] == "GET":
        req = event["queryStringParameters"]
    elif event["httpMethod"] == "OPTIONS":
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
        }

    query_results = query_measurements(req['from'], req['to'])
    data = format_results(query_results)

    return {
        'statusCode': 200,
        'body': json.dumps({
            'data': data
        }),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
    }
