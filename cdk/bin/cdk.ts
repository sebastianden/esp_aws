#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import { CdkStack } from '../lib/cdk-stack';
import { TestStack } from '../lib/test-stack'

const app = new cdk.App();
new CdkStack(app, 'CdkStack');
new TestStack(app, 'TestStack');
