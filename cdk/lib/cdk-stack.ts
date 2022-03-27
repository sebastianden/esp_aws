import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as iot from 'aws-cdk-lib/aws-iot';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as apigw from 'aws-cdk-lib/aws-apigateway'
import * as iam from 'aws-cdk-lib/aws-iam';

export class CdkStack extends cdk.Stack {
  constructor(scope: cdk.App, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const iotTable = new dynamodb.Table(this, 'IotDynamoDbTable', {
      tableName: 'iot-dynamodb-table',
      partitionKey: { name: 'measurement', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'timestamp', type: dynamodb.AttributeType.NUMBER },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
    });

    const iotRuleRole = new iam.Role(this, 'IotDynamoDbTopicRuleRole', {
      roleName: 'iot-dynamodb-topic-rule-role',
      assumedBy: new iam.ServicePrincipal('iot.amazonaws.com'),
      inlinePolicies: {
        IoT2DynamoDb: new iam.PolicyDocument({
          statements: [
            new iam.PolicyStatement({
              resources: [iotTable.tableArn],
              actions: ['dynamodb:PutItem'],
            }),
          ],
        }),
      },
    });

    const queryDynamodbLambdaRole = new iam.Role(this, 'IotQueryDynamoDbLambdaRole', {
      roleName: 'iot-query-dynamodb-lambda-role',
      assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'),
      managedPolicies: [
        iam.ManagedPolicy.fromAwsManagedPolicyName(
          'service-role/AWSLambdaBasicExecutionRole',
        ),
      ],
      inlinePolicies: {
        GetDynamoDb: new iam.PolicyDocument({
          statements: [
            new iam.PolicyStatement({
              resources: [iotTable.tableArn],
              actions: ['dynamodb:Query'],
            }),
          ],
        }),
      },
    });

    const iotDynamoDbRule = new iot.CfnTopicRule(this, 'IotDynamoDbRule', {
      ruleName: 'iotdynamodbtopicrule',
      topicRulePayload: {
        actions: [{
          dynamoDBv2: {
            putItem: {
              tableName: iotTable.tableName,
            },
            roleArn: iotRuleRole.roleArn,
          },
        }],
        sql: "SELECT * FROM 'esp8266/pub'",
        ruleDisabled: false,
      },
    });

    const queryDynamoDbLambda = new lambda.Function(this, 'IoTQueryDynamoDbLambda',
      {
        runtime: lambda.Runtime.PYTHON_3_8,
        handler: 'query-dynamo-db.lambda_handler',
        code: lambda.Code.fromAsset('../lambda/'),
        role: queryDynamodbLambdaRole,
        functionName: 'iot-query-dynamo-db-lambda',
        environment: {
          'DYNAMODB_TABLE': iotTable.tableName,
        },
      },
    );

    const queryApiGateway = new apigw.LambdaRestApi(this, 'IotQueryApiGateway', {
      handler: queryDynamoDbLambda,
      restApiName: 'iot-query-api-gateway',
    });

    const queryApiUrl = new cdk.CfnOutput(this, 'IotQueryApiUrl', {
      value: queryApiGateway.url
    });

  }
}
