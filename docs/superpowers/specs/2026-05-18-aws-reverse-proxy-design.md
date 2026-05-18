# AWS Reverse Proxy Enhancement Design

**Goal:** Provide ready-to-use reverse proxy configurations (both managed ALB and self-managed Nginx) for AWS deployments, accessible via a new `/aws proxy-init` command.

## Architecture

We are employing a hybrid approach: providing raw IaC and configuration templates, and creating an interactive CLI command to scaffold them into a user's project.

### Components

1. **Templates:**
   - **Nginx (`modules/deployment/aws/templates/nginx.conf.tmpl`):** An optimized Nginx configuration for running as a sidecar or dedicated proxy in ECS/Fargate. It handles health checks for ALBs, real IP extraction, and supports Server-Sent Events (SSE) by disabling buffering.
   - **ALB + WAF (`modules/deployment/aws/templates/alb-waf.yaml.tmpl`):** A CloudFormation/SAM snippet defining an Application Load Balancer and a Web Application Firewall with basic SQLi and XSS protection rules.

2. **Command Handler:**
   - **Script (`modules/deployment/aws/scripts/proxy-init.sh`):** A bash script that prompts the user for their desired architecture (Serverless vs. Dedicated) and proxy type (Managed vs. Self-Managed). It then copies the relevant template to the user's `infrastructure/` directory and injects variables like the backend port.

3. **Module Registration:**
   - **Config (`modules/deployment/aws/b1-module.yaml`):** The new `/aws proxy-init` command and a corresponding skill description will be added to the module definition.
   - **Capabilities (`modules/deployment/aws/context/agent-capabilities.md`):** Documentation will be updated to reflect the new proxy generation capability.

## Data Flow (Scaffolding)
1. User runs `b1 /aws proxy-init`.
2. The `proxy-init.sh` script executes.
3. Script gathers inputs (Managed vs Self-Managed, Port).
4. Script resolves the correct template from the `aws` module's `templates` directory.
5. Script writes the rendered file(s) into the current working directory's `infrastructure/` folder.

## Error Handling
- The script must check if target files already exist and prompt before overwriting.
- If the required templates are missing from the installation, the script should exit gracefully with a helpful error message.
