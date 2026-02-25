#!/bin/bash
# Setup script for Kolada Fabric deployment
# This script helps set up the required environment variables for deployment

echo "=============================================="
echo "Kolada Fabric - Environment Setup"
echo "=============================================="
echo ""

# Check if .env file exists
if [ -f .env ]; then
    echo "Found existing .env file. Loading..."
    source .env
fi

# Function to prompt for variable if not set
prompt_if_empty() {
    local var_name=$1
    local prompt_text=$2
    local current_value=${!var_name}
    
    if [ -z "$current_value" ]; then
        read -p "$prompt_text: " input_value
        echo "export $var_name=\"$input_value\"" >> .env
    else
        echo "$var_name is already set"
    fi
}

echo "Setting up environment variables..."
echo ""

# Create or append to .env file
touch .env

prompt_if_empty "FABRIC_TENANT_ID" "Enter your Azure AD Tenant ID"
prompt_if_empty "FABRIC_CLIENT_ID" "Enter your Service Principal Client ID"
prompt_if_empty "FABRIC_CLIENT_SECRET" "Enter your Service Principal Client Secret"
prompt_if_empty "FABRIC_WORKSPACE_NAME" "Enter your Fabric Workspace Name (default: KoladaWorkspace)"

# Set default workspace name if not provided
if grep -q "FABRIC_WORKSPACE_NAME=\"\"" .env; then
    sed -i 's/FABRIC_WORKSPACE_NAME=""/FABRIC_WORKSPACE_NAME="KoladaWorkspace"/' .env
fi

echo ""
echo "Environment setup complete!"
echo "Your configuration has been saved to .env"
echo ""
echo "To use these variables, run:"
echo "  source .env"
echo ""
echo "To deploy to Fabric, run:"
echo "  source .env && python deployment/deploy_to_fabric.py"
echo ""
