import boto3

client = boto3.client('lambda')

if __name__ == "__main__":

    response = client.invoke(
        FunctionName='iot-integration-test-lambda')

    assert response['status'] == 200
