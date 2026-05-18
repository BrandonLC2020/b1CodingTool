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
