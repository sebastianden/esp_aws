import boto3

client = boto3.client('lambda')

if __name__ == '__main__':
    try:
        response = client.invoke(
            FunctionName='iot-integration-test-lambda')

        assert response['ResponseMetadata']['HTTPStatusCode'] == 200
        print('Successfully ran integration tests.')
    except Exception:
        print('Integration tests failed.')
