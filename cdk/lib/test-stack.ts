import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as iam from 'aws-cdk-lib/aws-iam';

export class TestStack extends cdk.Stack {

  ACCOUNT = '274607345716';
  REGION = 'eu-central-1';
  TOPIC = 'iot/test/data';
  IOT_ENDPOINT = 'https://a2mddjle8tpgu2-ats.iot.eu-central-1.amazonaws.com';

  constructor(scope: cdk.App, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const queryApiUrl = cdk.Fn.importValue('iot-api-url');
    const queryDynamoDbLambdaName = cdk.Fn.importValue('query-dynamodb-lambda-name');
    const iotTableArn = cdk.Fn.importValue('iot-dynamodb-table-arn');
    const iotTableName = cdk.Fn.importValue('iot-dynamodb-table-name');

    const integrationTestLambdaRole = new iam.Role(this, 'IotIntegrationTestLambdaRole', {
      roleName: 'iot-integration-test-lambda-role',
      assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'),
      managedPolicies: [
        iam.ManagedPolicy.fromAwsManagedPolicyName(
          'service-role/AWSLambdaBasicExecutionRole',
        ),
      ],
      inlinePolicies: {
        IoTCorePublish: new iam.PolicyDocument({
          statements: [
            new iam.PolicyStatement({
              resources: [`arn:aws:iot:${this.REGION}:${this.ACCOUNT}:topic/${this.TOPIC}`],
              actions: ['iot:Publish'],
            }),
          ],
        }),
        DynamoDBWrite: new iam.PolicyDocument({
          statements: [
            new iam.PolicyStatement({
              resources: [iotTableArn],
              actions: ['dynamodb:DeleteItem'],
            }),
          ],
        })
      },
    });

    const integrationTestLambdaLayer = new lambda.LayerVersion(this, 'IotIntegrationTestLambdaLayer', {
      code: lambda.Code.fromAsset('../test/lambda/layer/'),
      compatibleRuntimes: [lambda.Runtime.PYTHON_3_8],
      layerVersionName: 'requests-layer',
    })

    const integrationTestLambda = new lambda.Function(this, 'IotIntegrationTestLambda', {
      runtime: lambda.Runtime.PYTHON_3_8,
      handler: 'index.lambda_handler',
      code: lambda.Code.fromAsset('../test/lambda/integration-test/'),
      role: integrationTestLambdaRole,
      functionName: 'iot-integration-test-lambda',
      layers: [integrationTestLambdaLayer],
      timeout: cdk.Duration.seconds(30),
      environment: {
        'API_URL': queryApiUrl,
        'LAMBDA_NAME': queryDynamoDbLambdaName,
        'DYNAMODB_TABLE': iotTableName,
        'IOT_ENDPOINT': this.IOT_ENDPOINT,
      },
    });
  }
}
