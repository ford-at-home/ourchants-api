# Infrastructure

This directory contains the AWS CDK infrastructure code for deploying the OurChants API.

## Directory Structure

```
infrastructure/
├── api/                # API Stack resources
│   └── stacks/
│       └── api_stack.py  # API Gateway, Lambda configuration
├── database/           # Database Stack resources
│   └── stacks/
│       └── database_stack.py  # DynamoDB configuration
├── app.py             # CDK app entry point
├── deploy.sh          # Deployment script
└── README.md          # This file
```

## Components

### API Stack (`api/stacks/api_stack.py`)

Defines AWS resources for the API:
- Lambda function configuration
- API Gateway setup
- IAM roles and permissions
- Integration with Database Stack

### Database Stack (`database/stacks/database_stack.py`)

Defines AWS resources for data storage:
- DynamoDB table configuration
- Table properties and indexes
- Access patterns optimization
- Backup and scaling settings

### CDK App (`app.py`)

The main CDK application:
- Stack initialization
- Environment configuration
- Stack dependencies
- Resource tagging

### Deployment Script (`deploy.sh`)

Automates the deployment process:
- Virtual environment setup
- Dependency installation
- CDK bootstrapping
- Stack deployment
- Verbose output for debugging

## Deployment

1. Ensure AWS credentials are configured
2. Run the deployment script:
```bash
./deploy.sh
```

The script will:
1. Create and activate a virtual environment
2. Install dependencies
3. Bootstrap CDK (if needed)
4. Deploy the Database Stack
5. Deploy the API Stack

## Stack Dependencies

The stacks are deployed in order:
1. Database Stack
2. API Stack (depends on Database Stack)

## Infrastructure Updates

To update the infrastructure:
1. Modify the relevant stack code
2. Run the deployment script
3. Review the changes in AWS CloudFormation
4. Monitor the deployment progress

## Cleanup

To remove all resources:
```bash
cdk destroy --all
```

## AWS Resources Created

### API Stack
- Lambda Function
- API Gateway
- IAM Roles
- CloudWatch Logs

### Database Stack
- DynamoDB Table
- IAM Policies
- Backup Configuration

## Cost Considerations

The infrastructure uses:
- Pay-per-request Lambda pricing
- On-demand DynamoDB capacity
- API Gateway request pricing

Monitor AWS Cost Explorer for usage details.

## Security

- IAM roles follow least privilege
- API Gateway uses AWS_IAM auth
- DynamoDB encryption at rest
- CloudWatch logging enabled

## Troubleshooting

Common issues:
1. CDK bootstrap errors
   - Ensure correct AWS credentials
   - Check account/region settings

2. Deployment failures
   - Check CloudFormation events
   - Review CloudWatch logs
   - Verify IAM permissions

3. Stack dependency issues
   - Ensure correct deployment order
   - Check cross-stack references 