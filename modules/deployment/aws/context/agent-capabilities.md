# AWS: Agent Commands & Skills

## Recommended Skills
- **Infrastructure Auditor:** Scans CloudFormation, SAM, or Terraform files for insecure configurations (e.g., overly broad IAM permissions, unencrypted S3 buckets).
- **Serverless Config Generator:** Assists in creating `serverless.yml` or `template.yaml` files for Lambda-based projects.
- **IAM Policy Builder:** Generates fine-grained IAM JSON policies based on the specific AWS actions the application needs to perform.

## Common Agent Commands
- `/aws audit`: Trigger a security audit of the `infrastructure/` directory.
- `/aws lambda-init`: Generate a boilerplate AWS Lambda function and SAM template.
- `/aws cost-check`: Provide advice on cost-saving measures based on the resource definitions found in the workspace.

## Sync with b1
- `b1 install aws`: Initializes the `infrastructure/aws` directory structure and adds AWS-specific agent context.
- `b1 pair`: Ensures that AWS deployment guidelines are synchronized across all agent-specific instruction files.
