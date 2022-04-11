from behave import *
import boto3
import json


@given('the MQTT messages {message} are sent to the {topic}')
def step_connect(context, message, topic):
    context.client = boto3.client('lambda')
    context.message = json.loads(message)
    context.topic = topic


@when('querying the API with a {method} request')
def step_connect(context, method):
    response = context.client.invoke(
        FunctionName='iot-integration-test-lambda',
        Payload=json.dumps({
            'data': context.message,
            'topic': context.topic,
            'method': method
        }))
    response = json.loads(response["Payload"].read())
    context.body = json.loads(response['body'])


@then('then the response is: {response}')
def step_connect(context, response):
    print(context.body)
    assert context.body == response
