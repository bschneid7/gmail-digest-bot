# Gmail Digest Bot - Complete Deployment Guide

## 📋 Overview

This guide will walk you through deploying the Gmail Digest Bot to Azure with full automation, monitoring, and cost optimization. The deployment includes:

- **Flask Web Application** (Azure App Service)
- **React Frontend** (built and served by Flask)
- **Azure Functions** (scheduled digest delivery)
- **Cosmos DB** (user data and preferences)
- **SendGrid** (email delivery)
- **GitHub Actions** (CI/CD pipeline)

## 🎯 Deployment Options

### Option 1: Automated Deployment (Recommended)
Use the provided script for a fully automated setup.

### Option 2: Manual Deployment
Step-by-step manual deployment for full control.

### Option 3: Local Development
Set up a local development environment.

---

## 🚀 Option 1: Automated Deployment

### Prerequisites
- Azure account with active subscription
- Azure CLI installed (`az --version`)
- Git installed
- GitHub account (for CI/CD)

### Step 1: Prepare Your Environment
```bash
# Clone your repository
git clone https://github.com/bschneid7/gmail-digest-bot.git
cd gmail-digest-bot

# Make scripts executable
chmod +x deploy.sh setup-oauth.py
```

### Step 2: Set Up Google OAuth
```bash
# Run the OAuth setup helper
python3 setup-oauth.py
```

This will:
1. Guide you through Google Cloud Console setup
2. Generate OAuth credentials
3. Save configuration to `.env.oauth`

### Step 3: Deploy to Azure
```bash
# Run the automated deployment
./deploy.sh
```

The script will:
1. Prompt for required configuration values
2. Create Azure resource group
3. Deploy all infrastructure using Bicep templates
4. Configure environment variables
5. Provide next steps for CI/CD setup

### Step 4: Set Up CI/CD
After deployment, set up GitHub Actions:

```bash
# Get publish profiles (run after deployment)
RESOURCE_GROUP="gmail-digest-rg"
az webapp deployment list-publishing-profiles \
  --resource-group $RESOURCE_GROUP \
  --name gmail-digest-app --xml > webapp-profile.xml

az functionapp deployment list-publishing-profiles \
  --resource-group $RESOURCE_GROUP \
  --name gmail-digest-scheduler --xml > function-profile.xml
```

Add GitHub repository secrets:
- `AZURE_WEBAPP_PUBLISH_PROFILE`: Content of `webapp-profile.xml`
- `AZURE_FUNCTIONAPP_PUBLISH_PROFILE`: Content of `function-profile.xml`

---

## 🔧 Option 2: Manual Deployment

### Step 1: Azure Resource Creation

#### Create Resource Group
```bash
az group create --name gmail-digest-rg --location eastus
```

#### Deploy Infrastructure
```bash
# Update azure-parameters.json with your values
az deployment group create \
  --resource-group gmail-digest-rg \
  --template-file azure-resources.bicep \
  --parameters azure-parameters.json
```

### Step 2: Configure Application Settings

#### App Service Settings
```bash
APP_NAME="gmail-digest-app"
az webapp config appsettings set \
  --resource-group gmail-digest-rg \
  --name $APP_NAME \
  --settings \
    FLASK_SECRET_KEY="your-secret-key" \
    GOOGLE_CLIENT_ID="your-client-id" \
    GOOGLE_CLIENT_SECRET="your-client-secret" \
    GMAIL_REFRESH_TOKEN="your-refresh-token" \
    ADMIN_EMAIL="your-admin@example.com" \
    X_API_KEY="your-api-key" \
    SENDGRID_API_KEY="your-sendgrid-key" \
    TZ="America/Los_Angeles"
```

#### Function App Settings
```bash
FUNC_NAME="gmail-digest-scheduler"
az functionapp config appsettings set \
  --resource-group gmail-digest-rg \
  --name $FUNC_NAME \
  --settings \
    BACKEND_BASE_URL="https://gmail-digest-app.azurewebsites.net" \
    X_API_KEY="your-api-key" \
    TZ="America/Los_Angeles"
```

---

## 🏠 Option 3: Local Development

### Setup Environment
```bash
# Copy environment template
cp .env.template .env

# Edit .env with your actual values
nano .env
```

### Install Dependencies
```bash
# Frontend
cd web
npm install
npm run build
cd ..

# Backend
cd app
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cd ..
```

### Run Application

#### Using Docker Compose (Recommended)
```bash
docker-compose up --build
```

#### Manual Startup
```bash
# Terminal 1: Backend
cd app
source .venv/bin/activate
python app.py

# Terminal 2: Frontend (development mode)
cd web
npm run dev
```

Access at: `http://localhost:8000`

---

## 🔐 Security Configuration

### Google OAuth Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create/select project
3. Enable Gmail API
4. Create OAuth 2.0 credentials (Web application)
5. Add redirect URI: `https://your-app-name.azurewebsites.net/oauth/callback`
6. Download client configuration

### SendGrid Setup
1. Create [SendGrid account](https://sendgrid.com/)
2. Verify sender email
3. Create API key with mail send permissions
4. Add API key to environment variables

### Cosmos DB Security
- Firewall configured to allow Azure services
- Primary keys automatically configured
- Connection strings secured in App Service settings

---

## 💰 Cost Management

### Current Cost Estimate
- **App Service (B1)**: ~$13/month
- **Cosmos DB (Serverless)**: ~$1-5/month
- **Functions (Consumption)**: ~$0-2/month
- **Storage Account**: ~$1/month
- **Total**: ~$15-20/month

### Cost Optimization Tips
1. **Use Serverless Cosmos DB**: Pay only for what you use
2. **Monitor Function executions**: Optimize digest frequency if needed
3. **Review App Service plan**: Scale down if traffic is low
4. **Set up cost alerts**: Get notified of unexpected charges

---

## 🔄 CI/CD Pipeline Details

### GitHub Actions Workflow
The included workflow (`.github/workflows/azure-deploy.yml`) provides:

1. **Automated builds** on push to main branch
2. **Frontend compilation** with npm
3. **Backend packaging** with Python dependencies
4. **Parallel deployment** to App Service and Functions
5. **Environment-specific configuration**

### Deployment Triggers
- **Push to main**: Full deployment
- **Pull request**: Build validation only
- **Manual trigger**: On-demand deployment

---

## 🆘 Troubleshooting

### Common Issues

#### 1. OAuth Redirect Mismatch
**Error**: `redirect_uri_mismatch`
**Solution**: 
- Check Google Console redirect URI matches exactly
- Format: `https://your-app-name.azurewebsites.net/oauth/callback`

#### 2. Cosmos DB Connection Failed
**Error**: `CosmosDB connection timeout`
**Solution**:
- Verify COSMOS_URL and COSMOS_KEY in App Service settings
- Check Cosmos DB firewall allows Azure services
- Restart App Service after configuration changes

#### 3. SendGrid Authentication Failed
**Error**: `SendGrid API key invalid`
**Solution**:
- Verify API key in SendGrid dashboard
- Check sender email is verified
- Ensure API key has mail send permissions

#### 4. Function Not Triggering
**Error**: Digest emails not being sent
**Solution**:
- Check Function App logs for errors
- Verify BACKEND_BASE_URL points to correct App Service
- Ensure X_API_KEY matches between App Service and Functions
- Check timezone setting (TZ=America/Los_Angeles)

### Debug Commands
```bash
# Check App Service status
az webapp show --resource-group gmail-digest-rg --name gmail-digest-app --query state

# Test Function manually
az functionapp function invoke \
  --resource-group gmail-digest-rg \
  --name gmail-digest-scheduler \
  --function-name run_digest

# View recent deployments
az webapp deployment list --resource-group gmail-digest-rg --name gmail-digest-app
```

---

## 📈 Scaling and Performance

### Horizontal Scaling
```bash
# Scale App Service instances
az appservice plan update \
  --resource-group gmail-digest-rg \
  --name gmail-digest-plan \
  --number-of-workers 2
```

### Performance Monitoring
- Use Application Insights for detailed metrics
- Monitor response times and error rates
- Set up alerts for performance degradation

---

## 🔒 Security Best Practices

### Environment Security
- All secrets stored in Azure Key Vault or App Service settings
- HTTPS enforced for all connections
- CSRF protection enabled
- Security headers automatically applied

### Access Control
- Admin-controlled user allowlist
- OAuth-based authentication only
- API endpoints protected with keys
- Regular security updates via CI/CD

### Data Protection
- All data encrypted at rest (Cosmos DB)
- All data encrypted in transit (HTTPS)
- 6-month automatic data retention
- Regular automated backups

This deployment guide provides everything needed for a successful, production-ready Gmail Digest Bot deployment on Azure with full automation, monitoring, and cost optimization.

