#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import { CdkStack, TestStack } from '../lib/cdk-stack';

const app = new cdk.App();
new CdkStack(app, 'CdkStack');
new TestStack(app, 'TestStak');
