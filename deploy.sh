#!/bin/bash

# Gmail Digest Bot - Azure Deployment Script
# This script deploys the Gmail Digest Bot to Azure using Bicep templates

set -e

# Configuration
RESOURCE_GROUP="gmail-digest-rg"
LOCATION="eastus"
DEPLOYMENT_NAME="gmail-digest-deployment-$(date +%Y%m%d-%H%M%S)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Gmail Digest Bot - Azure Deployment${NC}"
echo "======================================"

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo -e "${RED}Error: Azure CLI is not installed. Please install it first.${NC}"
    exit 1
fi

# Check if user is logged in
if ! az account show &> /dev/null; then
    echo -e "${YELLOW}Please log in to Azure...${NC}"
    az login
fi

# Get current subscription
SUBSCRIPTION=$(az account show --query id -o tsv)
echo -e "${GREEN}Using subscription: ${SUBSCRIPTION}${NC}"

# Prompt for required parameters
echo ""
echo "Please provide the following configuration values:"

read -p "Admin Email (for initial access): " ADMIN_EMAIL
if [[ -z "$ADMIN_EMAIL" ]]; then
    echo -e "${RED}Admin email is required${NC}"
    exit 1
fi

read -p "Google OAuth Client ID: " GOOGLE_CLIENT_ID
if [[ -z "$GOOGLE_CLIENT_ID" ]]; then
    echo -e "${RED}Google Client ID is required${NC}"
    exit 1
fi

read -s -p "Google OAuth Client Secret: " GOOGLE_CLIENT_SECRET
echo ""
if [[ -z "$GOOGLE_CLIENT_SECRET" ]]; then
    echo -e "${RED}Google Client Secret is required${NC}"
    exit 1
fi

read -s -p "Gmail Refresh Token: " GMAIL_REFRESH_TOKEN
echo ""
if [[ -z "$GMAIL_REFRESH_TOKEN" ]]; then
    echo -e "${RED}Gmail Refresh Token is required${NC}"
    exit 1
fi

read -s -p "SendGrid API Key: " SENDGRID_API_KEY
echo ""
if [[ -z "$SENDGRID_API_KEY" ]]; then
    echo -e "${RED}SendGrid API Key is required${NC}"
    exit 1
fi

# Create resource group
echo -e "${YELLOW}Creating resource group...${NC}"
az group create --name $RESOURCE_GROUP --location $LOCATION

# Deploy Bicep template
echo -e "${YELLOW}Deploying Azure resources...${NC}"
DEPLOYMENT_OUTPUT=$(az deployment group create \
    --resource-group $RESOURCE_GROUP \
    --template-file azure-resources.bicep \
    --parameters \
        adminEmail="$ADMIN_EMAIL" \
        googleClientId="$GOOGLE_CLIENT_ID" \
        googleClientSecret="$GOOGLE_CLIENT_SECRET" \
        gmailRefreshToken="$GMAIL_REFRESH_TOKEN" \
        sendGridApiKey="$SENDGRID_API_KEY" \
    --name $DEPLOYMENT_NAME \
    --query 'properties.outputs' \
    -o json)

# Extract outputs
WEB_APP_URL=$(echo $DEPLOYMENT_OUTPUT | jq -r '.webAppUrl.value')
FUNCTION_APP_NAME=$(echo $DEPLOYMENT_OUTPUT | jq -r '.functionAppName.value')

echo ""
echo -e "${GREEN}Deployment completed successfully!${NC}"
echo "======================================"
echo -e "Web App URL: ${GREEN}$WEB_APP_URL${NC}"
echo -e "Function App: ${GREEN}$FUNCTION_APP_NAME${NC}"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Set up GitHub repository with this code"
echo "2. Configure GitHub Actions secrets:"
echo "   - AZURE_WEBAPP_PUBLISH_PROFILE"
echo "   - AZURE_FUNCTIONAPP_PUBLISH_PROFILE"
echo "3. Push code to trigger deployment"
echo ""
echo -e "${YELLOW}To get publish profiles:${NC}"
echo "az webapp deployment list-publishing-profiles --resource-group $RESOURCE_GROUP --name gmail-digest-app --xml"
echo "az functionapp deployment list-publishing-profiles --resource-group $RESOURCE_GROUP --name $FUNCTION_APP_NAME --xml"

