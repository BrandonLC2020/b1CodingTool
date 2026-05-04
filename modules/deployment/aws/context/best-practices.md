# AWS: Best Practices

## Infrastructure as Code (IaC)
- **Declarative over Imperative:** Use AWS CloudFormation, AWS CDK, or Terraform for all production infrastructure. Never use the AWS Console for manual resource creation in production.
- **Version Control:** Commit all IaC templates to the repository and use automated CI/CD pipelines (e.g., AWS CodePipeline, GitHub Actions) for deployments.
- **Modularity:** Break large infrastructure templates into smaller, reusable stacks or modules (e.g., Network, Database, Application).

## Security & IAM
- **Principle of Least Privilege:** Grant only the minimum permissions required for a task. Use IAM Roles for services (e.g., ECS tasks, Lambda functions) instead of IAM User keys.
- **Encryption by Default:** Enable server-side encryption for S3 buckets, RDS databases, and EBS volumes using AWS KMS.
- **Secret Management:** Use AWS Secrets Manager or AWS Systems Manager Parameter Store for sensitive configuration; never hardcode secrets in code or IaC templates.

## Performance & Scalability
- **Compute Selection:** Match the compute type to the workload:
  - **Lambda:** Event-driven, ephemeral tasks.
  - **ECS/Fargate:** Long-running containerized services.
  - **EC2:** Specialized workloads requiring custom OS configuration.
- **Auto Scaling:** Use Auto Scaling groups or ECS service scaling to handle fluctuating demand and minimize costs.

## Cost Optimization
- **Tagging:** Apply consistent tags (e.g., `Environment`, `Project`, `Owner`) to all resources for cost allocation and tracking.
- **Right-sizing:** Monitor resource utilization (e.g., via CloudWatch) and adjust instance sizes to match actual needs.
