import os
import json
import boto3
from boto3.dynamodb.conditions import Key
from typing import Dict, List
from collections import defaultdict


dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.getenv('DYNAMODB_TABLE'))
measurements = ['temperature', 'humidity']


def query_measurements(start: str, end: str, device: str) -> Dict:
    """
    Query DynamoDB for measurements froma specific device within a time range.

    Parameters
    ----------
    start: str
        Start timestamp
    end: str
        End timestamp
    device: str
        Device

    Returns
    -------
    dict: Result of query
    """
    query_results = {}

    query_results = table.query(
        KeyConditionExpression=Key('device').eq(device) & Key(
            'timestamp').between(int(start), int(end))
    )

    return query_results


def format_results(query_results: Dict) -> Dict[str, List]:
    """
    Arrange the query results into a dict of lists. Each key conatins a list
    with either timestamps, devices or sensor measurements

    Parameters
    ----------
    query_results: dict
        Results of queries

    Returns
    -------
    dict: Formatted results as dict of lists
    """
    data = defaultdict(list)

    for item in query_results['Items']:
        print(item)
        for key, value in item.items():
            if key == 'timestamp':
                data[key].append(int(value))
            elif key == 'device':
                data[key].append(value)
            else:
                data[key].append(float(value))

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

    query_results = query_measurements(req['from'], req['to'], req['device'])
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
