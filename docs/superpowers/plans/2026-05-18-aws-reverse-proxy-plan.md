# AWS Reverse Proxy Enhancement Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Enhance the AWS module with reverse proxy setup templates and an initialization command.

**Architecture:** We are creating two IaC templates (Nginx config and an ALB+WAF CloudFormation snippet) and a bash script that acts as an interactive command handler to scaffold these files into a user's project. The module configuration and documentation will also be updated.

**Tech Stack:** Nginx, CloudFormation/SAM, Bash, YAML, Markdown

---

### Task 1: Create Nginx Reverse Proxy Template

**Files:**
- Create: `modules/deployment/aws/templates/nginx.conf.tmpl`

- [ ] **Step 1: Write the Nginx Template**

Create the file `modules/deployment/aws/templates/nginx.conf.tmpl` with the following content:

```nginx
worker_processes auto;
events { worker_connections 1024; }

http {
    include       mime.types;
    default_type  application/octet-stream;
    sendfile        on;
    keepalive_timeout  65;

    # Extract original client IP if behind an ALB
    set_real_ip_from  10.0.0.0/8; # VPC CIDR (Adjust as needed)
    real_ip_header    X-Forwarded-For;

    server {
        listen 80;
        server_name _;

        # Health check for ALB
        location /health {
            access_log off;
            return 200 'OK';
        }

        location / {
            proxy_pass http://localhost:{{BACKEND_PORT}};
            proxy_http_version 1.1;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # SSE Support
            proxy_set_header Connection '';
            proxy_buffering off;
            proxy_cache off;
            chunked_transfer_encoding off;
        }
    }
}
```

- [ ] **Step 2: Commit**

```bash
git add modules/deployment/aws/templates/nginx.conf.tmpl
git commit -m "feat(aws): add optimized nginx reverse proxy template"
```

---

### Task 2: Create ALB + WAF Template

**Files:**
- Create: `modules/deployment/aws/templates/alb-waf.yaml.tmpl`

- [ ] **Step 1: Write the CloudFormation Snippet**

Create the file `modules/deployment/aws/templates/alb-waf.yaml.tmpl` with the following content:

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: Application Load Balancer and basic WAF configuration

Parameters:
  VpcId:
    Type: AWS::EC2::VPC::Id
  SubnetIds:
    Type: List<AWS::EC2::Subnet::Id>

Resources:
  LoadBalancerSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Allow HTTP/HTTPS inbound
      VpcId: !Ref VpcId
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          CidrIp: 0.0.0.0/0
        - IpProtocol: tcp
          FromPort: 443
          ToPort: 443
          CidrIp: 0.0.0.0/0

  ApplicationLoadBalancer:
    Type: AWS::ElasticLoadBalancingV2::LoadBalancer
    Properties:
      Scheme: internet-facing
      Subnets: !Ref SubnetIds
      SecurityGroups:
        - !Ref LoadBalancerSecurityGroup

  BasicWafWebACL:
    Type: AWS::WAFv2::WebACL
    Properties:
      DefaultAction:
        Allow: {}
      Scope: REGIONAL
      VisibilityConfig:
        CloudWatchMetricsEnabled: true
        MetricName: BasicWafMetrics
        SampledRequestsEnabled: true
      Rules:
        - Name: AWS-AWSManagedRulesCommonRuleSet
          Priority: 0
          Statement:
            ManagedRuleGroupStatement:
              VendorName: AWS
              Name: AWSManagedRulesCommonRuleSet
          OverrideAction:
            None: {}
          VisibilityConfig:
            SampledRequestsEnabled: true
            CloudWatchMetricsEnabled: true
            MetricName: AWSManagedRulesCommonRuleSetMetric

  WebACLAssociation:
    Type: AWS::WAFv2::WebACLAssociation
    Properties:
      ResourceArn: !Ref ApplicationLoadBalancer
      WebACLArn: !GetAtt BasicWafWebACL.Arn
```

- [ ] **Step 2: Commit**

```bash
git add modules/deployment/aws/templates/alb-waf.yaml.tmpl
git commit -m "feat(aws): add cloudformation template for ALB and WAF"
```

---

### Task 3: Create Proxy Initialization Script

**Files:**
- Create: `modules/deployment/aws/scripts/proxy-init.sh`

- [ ] **Step 1: Write the Bash Script**

Create the file `modules/deployment/aws/scripts/proxy-init.sh`. Note: We don't have a test suite specifically for bash interactive scripts here, but we will make it robust.

```bash
#!/bin/bash
set -e

# Determine the directory of this script to locate templates
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE_DIR="$(dirname "$SCRIPT_DIR")/templates"
TARGET_DIR="${PWD}/infrastructure/proxy"

echo "=== AWS Reverse Proxy Setup ==="

# Prompt for Proxy Type
echo "Select the type of proxy you want to generate:"
echo "1) Managed (AWS Application Load Balancer + WAF)"
echo "2) Self-Managed (Nginx container configuration)"
read -p "Selection (1 or 2): " PROXY_TYPE

mkdir -p "$TARGET_DIR"

if [ "$PROXY_TYPE" = "1" ]; then
    TARGET_FILE="$TARGET_DIR/alb-waf.yaml"
    if [ -f "$TARGET_FILE" ]; then
        read -p "$TARGET_FILE already exists. Overwrite? (y/N) " OVERWRITE
        if [[ ! "$OVERWRITE" =~ ^[Yy]$ ]]; then
            echo "Skipping."
            exit 0
        fi
    fi
    cp "$TEMPLATE_DIR/alb-waf.yaml.tmpl" "$TARGET_FILE"
    echo "Created $TARGET_FILE"

elif [ "$PROXY_TYPE" = "2" ]; then
    read -p "Enter the backend port (default: 8000): " BACKEND_PORT
    BACKEND_PORT=${BACKEND_PORT:-8000}
    
    TARGET_FILE="$TARGET_DIR/nginx.conf"
    if [ -f "$TARGET_FILE" ]; then
        read -p "$TARGET_FILE already exists. Overwrite? (y/N) " OVERWRITE
        if [[ ! "$OVERWRITE" =~ ^[Yy]$ ]]; then
            echo "Skipping."
            exit 0
        fi
    fi
    
    # Use sed to replace the placeholder
    sed "s/{{BACKEND_PORT}}/$BACKEND_PORT/g" "$TEMPLATE_DIR/nginx.conf.tmpl" > "$TARGET_FILE"
    echo "Created $TARGET_FILE (configured for backend port $BACKEND_PORT)"

else
    echo "Invalid selection. Exiting."
    exit 1
fi

echo "Done!"
```

- [ ] **Step 2: Make the script executable and Commit**

```bash
chmod +x modules/deployment/aws/scripts/proxy-init.sh
git add modules/deployment/aws/scripts/proxy-init.sh
git commit -m "feat(aws): add interactive script to scaffold reverse proxies"
```

---

### Task 4: Update Module Configuration and Documentation

**Files:**
- Modify: `modules/deployment/aws/b1-module.yaml`
- Modify: `modules/deployment/aws/context/agent-capabilities.md`

- [ ] **Step 1: Update `b1-module.yaml`**

Add the new command to the `commands` list in `modules/deployment/aws/b1-module.yaml`. Also add a skill description.

Add this under the `skills` array:
```yaml
  - name: "Reverse Proxy Configurator"
    description: "Helps generate Nginx or ALB configuration files for reverse proxying and security."
```

Add this under the `commands` array:
```yaml
  - name: "/aws proxy-init"
    description: "Generate a reverse proxy configuration (Nginx or ALB) for your deployment"
```

- [ ] **Step 2: Update `agent-capabilities.md`**

In `modules/deployment/aws/context/agent-capabilities.md`, add the new skill to `## Recommended Skills`:
```markdown
- **Reverse Proxy Configurator:** Helps generate Nginx or ALB configuration files for reverse proxying and security.
```

And add the command to `## Common Agent Commands`:
```markdown
- `/aws proxy-init`: Generate a reverse proxy configuration (Nginx or ALB) for your deployment.
```

- [ ] **Step 3: Commit**

```bash
git add modules/deployment/aws/b1-module.yaml modules/deployment/aws/context/agent-capabilities.md
git commit -m "docs(aws): register reverse proxy tools in module config and capabilities"
```
