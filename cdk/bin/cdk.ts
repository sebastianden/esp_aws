#!/usr/bin/env node
import * as cdk from "aws-cdk-lib";
import { CdkStack } from "../lib/cdk-stack";
import { TestStack } from "../lib/test-stack";

const app = new cdk.App();
const context = app.node.tryGetContext("env");

new CdkStack(app, "CdkStack", {
  env: {
    account: context.account,
    region: context.region,
  },
});

new TestStack(app, "TestStack", {
  env: {
    account: context.account,
    region: context.region,
  },
});
