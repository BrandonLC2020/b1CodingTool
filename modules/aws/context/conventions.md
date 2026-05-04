# AWS: Conventions

## Resource Naming
- **Uniqueness:** Use a consistent naming scheme that includes the project name and environment (e.g., `b1coding-prod-orders-bucket`).
- **Casing:** Follow the conventions of the specific IaC tool (e.g., `PascalCase` for CloudFormation logical IDs, `snake_case` for Terraform resource names).

## Tagging Strategy
Required tags for all resources:
| Tag | Purpose | Example |
|-----|---------|---------|
| `Project` | Identifier for the project | `b1CodingTool` |
| `Environment` | Deploy stage | `dev`, `staging`, `prod` |
| `Owner` | Responsible team or person | `platform-team` |
| `ManagedBy` | Tool used for management | `terraform`, `cdk` |

## Directory Structure (IaC)
Recommended layout for infrastructure files:
```
infrastructure/
├── aws/
│   ├── base/           # VPC, IAM, shared roles
│   ├── modules/        # Reusable component templates
│   └── services/       # Feature-specific infrastructure
│       ├── web-app.yml
│       └── database.yml
└── variables/          # Environment-specific params
    ├── dev.json
    └── prod.json
```

## Region Selection
- **Proximity:** Deploy resources in regions closest to your user base to minimize latency.
- **Compliance:** Ensure the selected region meets any data residency requirements.
- **Service Availability:** Verify that required AWS services are available in the selected region.
