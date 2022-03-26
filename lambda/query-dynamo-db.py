import os
import json
import boto3
from boto3.dynamodb.conditions import Key


dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.getenv('DYNAMODB_TABLE'))


def lambda_handler(event, context):

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

    response1 = table.query(
        KeyConditionExpression=Key('measurement').eq('temperature') & Key(
            'timestamp').between(int(req['from']), int(req['to']))
    )
    response2 = table.query(
        KeyConditionExpression=Key('measurement').eq('humidity') & Key(
            'timestamp').between(int(req['from']), int(req['to']))
    )

    timestamp_t = [int(item['timestamp']) for item in response1['Items']]
    temperature = [float(item['value']) for item in response1['Items']]
    timestamp_h = [int(item['timestamp']) for item in response2['Items']]
    humidity = [float(item['value']) for item in response2['Items']]
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
