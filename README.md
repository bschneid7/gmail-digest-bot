# Gmail Digest Bot — Azure Ready Deployment

A comprehensive Gmail digest bot with Google OAuth authentication, Azure Cosmos DB storage, and SendGrid email delivery. Features include:

- **Google OIDC** authentication with multi-user support
- **Multi-user allowlist** stored in Azure Cosmos DB
- **Azure Cosmos DB serverless** for preferences, history, and user management
- **SendGrid** email digests delivered at 5:00 AM, 12:00 PM, and 4:00 PM PT
- **6-month retention** with automatic cleanup
- **React + Tailwind CSS** frontend with settings management
- **Azure Functions** scheduler for automated digest delivery
- **Docker** containerization for easy deployment

## 🚀 Quick Start

### 1. Deploy to Azure (Automated)
```bash
# Make scripts executable
chmod +x deploy.sh setup-oauth.py

# Set up Google OAuth
python3 setup-oauth.py

# Deploy to Azure
./deploy.sh
```

### 2. Set up CI/CD
After deployment, configure GitHub Actions secrets:
- `AZURE_WEBAPP_PUBLISH_PROFILE`
- `AZURE_FUNCTIONAPP_PUBLISH_PROFILE`

### 3. Push and Deploy
```bash
git add .
git commit -m "Add Azure deployment infrastructure"
git push origin main
```

## 📁 Project Structure

```
gmail-digest-bot/
├── .github/workflows/          # GitHub Actions CI/CD
├── app/                        # Flask backend application
├── web/                        # React frontend
├── scheduler/                  # Azure Functions
├── azure-resources.bicep       # Azure infrastructure template
├── deploy.sh                   # Automated deployment script
├── setup-oauth.py             # OAuth setup helper
└── DEPLOYMENT_GUIDE.md        # Comprehensive deployment guide
```

## 🔧 Environment Variables

### App Service Configuration
- `FLASK_SECRET_KEY` - Flask session secret
- `GOOGLE_CLIENT_ID` - Google OAuth client ID
- `GOOGLE_CLIENT_SECRET` - Google OAuth client secret
- `GMAIL_REFRESH_TOKEN` - Gmail API refresh token
- `ADMIN_EMAIL` - Initial admin user email
- `X_API_KEY` - Internal API security key
- `COSMOS_URL` - Cosmos DB endpoint URL
- `COSMOS_KEY` - Cosmos DB primary key
- `SENDGRID_API_KEY` - SendGrid API key
- `TZ` - Timezone (America/Los_Angeles)

### Functions App Configuration
- `BACKEND_BASE_URL` - App Service base URL
- `X_API_KEY` - Same as App Service
- `TZ` - Timezone (America/Los_Angeles)

## 🏠 Local Development

```bash
# Copy environment template
cp .env.template .env
# Edit .env with your values

# Using Docker Compose (Recommended)
docker-compose up --build

# Or manual setup
cd web && npm install && npm run build && cd ..
cd app && python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
python app.py
```

## 💰 Cost Estimate

- **App Service (B1)**: ~$13/month
- **Cosmos DB (Serverless)**: ~$1-5/month
- **Functions (Consumption)**: ~$0-2/month
- **Storage Account**: ~$1/month
- **Total**: ~$15-20/month

## 🔒 Security Features

- **HTTPS Enforcement**: All traffic redirected to HTTPS
- **CSRF Protection**: Built-in Flask-Talisman security
- **OAuth Authentication**: Secure Google login integration
- **API Key Protection**: Internal API endpoints secured
- **User Allowlist**: Admin-controlled user access

## 📖 Documentation

- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - Complete deployment instructions
- [.env.template](.env.template) - Environment variables template

## 🆘 Support

For detailed deployment instructions, troubleshooting, and configuration options, see the [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md).

---

**Ready for 24/7 operation on Azure with automated deployments!**

