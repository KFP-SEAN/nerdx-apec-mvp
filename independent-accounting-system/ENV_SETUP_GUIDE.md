# Environment Variables Setup Guide - NERDX Accounting System

**Date**: 2025-10-25
**Status**: Ready for Configuration
**Time Required**: 10 minutes

---

## Overview

This guide provides the complete list of environment variables needed for Railway deployment. The database is already initialized and ready - you just need to configure these credentials.

---

## Required Environment Variables

### 1. Database (Already Configured)

Railway automatically sets this when you add PostgreSQL:
```bash
DATABASE_URL=postgresql://postgres:GRRydiOlZsvNALSMpDVkmtDJuhbVQbCS@ballast.proxy.rlwy.net:38243/railway
```

Status: CONFIGURED (Railway automatically set this)

---

### 2. Salesforce CRM Integration

```bash
SALESFORCE_INSTANCE_URL=https://your-instance.salesforce.com
SALESFORCE_USERNAME=your_email@company.com
SALESFORCE_PASSWORD=YOUR_PASSWORD
SALESFORCE_SECURITY_TOKEN=YOUR_TOKEN
```

**How to Get Salesforce Credentials**:
1. Log in to Salesforce
2. Go to Setup → Apps → App Manager
3. Create a Connected App (if not exists)
4. Get your Security Token: Setup → Personal Information → Reset Security Token
5. Token will be emailed to you

**Status**: REQUIRED for Salesforce revenue sync

---

### 3. Odoo ERP Integration

```bash
ODOO_URL=https://your-company.odoo.com
ODOO_DB=your_database_name
ODOO_USERNAME=your_username
ODOO_PASSWORD=YOUR_PASSWORD
```

**How to Get Odoo Credentials**:
1. Log in to Odoo
2. Your URL is the login page URL
3. Database name is shown in the database selection dropdown
4. Use your Odoo login credentials

**Status**: REQUIRED for Odoo cost tracking

---

### 4. Email Service (SMTP)

```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=noreply@nerdx.com
SMTP_PASSWORD=YOUR_APP_PASSWORD
SMTP_FROM_EMAIL=noreply@nerdx.com
```

**For Gmail App Password**:
1. Go to https://myaccount.google.com/apppasswords
2. Select "Mail" and "Other (Custom name)"
3. Enter "NERDX Accounting System"
4. Copy the 16-character password
5. Use this as SMTP_PASSWORD (not your regular Gmail password)

**Status**: REQUIRED for daily email reports

---

### 5. Application Security

```bash
SECRET_KEY=YOUR_GENERATED_SECRET_32_CHARS
JWT_SECRET_KEY=YOUR_GENERATED_JWT_SECRET_32_CHARS
```

**Generate Secure Keys**:
```bash
# Run this in Python to generate random secure keys
python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"
python -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_urlsafe(32))"
```

**Status**: REQUIRED for application security

---

### 6. Application Configuration

```bash
API_ENVIRONMENT=production
DEBUG_MODE=False
```

**Status**: OPTIONAL (will use defaults if not set)

---

### 7. OpenAI API (Optional - for AI features)

```bash
OPENAI_API_KEY=sk-your-openai-api-key
```

**Note**: Only needed if you want real AI embeddings. The system works with mock embeddings by default.

**Cost**: ~$0.03/month for 100 cells with daily reports

**Status**: OPTIONAL (AI features use mock embeddings if not provided)

---

## Quick Setup - Copy/Paste Commands

### Option 1: Set via Railway CLI (Recommended)

```bash
# Navigate to project
cd C:/Users/seans/nerdx-apec-mvp/independent-accounting-system

# Set Salesforce credentials
railway variables set SALESFORCE_INSTANCE_URL="https://your-instance.salesforce.com"
railway variables set SALESFORCE_USERNAME="your_email@company.com"
railway variables set SALESFORCE_PASSWORD="YOUR_PASSWORD"
railway variables set SALESFORCE_SECURITY_TOKEN="YOUR_TOKEN"

# Set Odoo credentials
railway variables set ODOO_URL="https://your-company.odoo.com"
railway variables set ODOO_DB="your_database_name"
railway variables set ODOO_USERNAME="your_username"
railway variables set ODOO_PASSWORD="YOUR_PASSWORD"

# Set SMTP credentials
railway variables set SMTP_HOST="smtp.gmail.com"
railway variables set SMTP_PORT="587"
railway variables set SMTP_USERNAME="noreply@nerdx.com"
railway variables set SMTP_PASSWORD="YOUR_APP_PASSWORD"
railway variables set SMTP_FROM_EMAIL="noreply@nerdx.com"

# Generate and set security keys
railway variables set SECRET_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"
railway variables set JWT_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"

# Set application config
railway variables set API_ENVIRONMENT="production"
railway variables set DEBUG_MODE="False"

# Optional: Set OpenAI API key (for real AI embeddings)
railway variables set OPENAI_API_KEY="sk-your-openai-api-key"
```

### Option 2: Set via Railway Web Dashboard

1. Go to https://railway.app/dashboard
2. Select your project: `nerdx-accounting-system`
3. Click on your service
4. Go to "Variables" tab
5. Click "Add Variable" for each variable above
6. Copy/paste the names and values

### Option 3: Set via .env File (then sync to Railway)

1. Create `.env` file in project root:
```bash
# Salesforce
SALESFORCE_INSTANCE_URL=https://your-instance.salesforce.com
SALESFORCE_USERNAME=your_email@company.com
SALESFORCE_PASSWORD=YOUR_PASSWORD
SALESFORCE_SECURITY_TOKEN=YOUR_TOKEN

# Odoo
ODOO_URL=https://your-company.odoo.com
ODOO_DB=your_database_name
ODOO_USERNAME=your_username
ODOO_PASSWORD=YOUR_PASSWORD

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=noreply@nerdx.com
SMTP_PASSWORD=YOUR_APP_PASSWORD
SMTP_FROM_EMAIL=noreply@nerdx.com

# Security
SECRET_KEY=generate_with_python_command_above
JWT_SECRET_KEY=generate_with_python_command_above

# Application
API_ENVIRONMENT=production
DEBUG_MODE=False

# Optional: OpenAI
# OPENAI_API_KEY=sk-your-openai-api-key
```

2. Then sync to Railway:
```bash
# Load from .env file
cat .env | while IFS='=' read -r key value; do
  if [ ! -z "$key" ] && [ "${key:0:1}" != "#" ]; then
    railway variables set "$key=$value"
  fi
done
```

---

## Verification

After setting variables, verify they're configured:

```bash
# List all environment variables
railway variables

# Check specific variable
railway variables | grep SALESFORCE_INSTANCE_URL
```

Expected output should show all your configured variables.

---

## What Happens Next?

After environment variables are set:

1. **Deploy Application**:
   ```bash
   railway up
   ```

2. **Monitor Deployment**:
   ```bash
   railway logs --follow
   ```

3. **Get Your URL**:
   ```bash
   railway domain
   ```

4. **Test Integration**:
   ```bash
   RAILWAY_URL=$(railway domain)

   # Test health
   curl https://$RAILWAY_URL/health

   # Test Salesforce sync
   curl -X POST https://$RAILWAY_URL/api/sync/salesforce

   # Test Odoo sync
   curl -X POST https://$RAILWAY_URL/api/sync/odoo

   # Generate daily reports
   curl -X POST https://$RAILWAY_URL/api/reports/generate-all
   ```

---

## Security Best Practices

1. **Never commit .env file to git**
   - Already in .gitignore
   - Use Railway's encrypted variables instead

2. **Use App Passwords for Gmail**
   - Never use your actual Gmail password
   - Use 16-character app password from Google

3. **Rotate Keys Regularly**
   - Change SECRET_KEY and JWT_SECRET_KEY periodically
   - Update Salesforce/Odoo passwords as per company policy

4. **Limit API Access**
   - Use Salesforce Connected App with limited permissions
   - Create dedicated Odoo user with minimal required access

---

## Troubleshooting

### Issue: "Missing environment variable: SALESFORCE_INSTANCE_URL"

**Solution**: Set the variable via Railway CLI or dashboard
```bash
railway variables set SALESFORCE_INSTANCE_URL="https://your-instance.salesforce.com"
```

### Issue: Email sending fails

**Solution**: Verify Gmail App Password
1. Go to https://myaccount.google.com/apppasswords
2. Generate new app password
3. Update: `railway variables set SMTP_PASSWORD="new_password"`

### Issue: Salesforce authentication fails

**Solution**: Check Security Token
1. Reset token in Salesforce: Setup → Personal Information → Reset Security Token
2. Check email for new token
3. Update: `railway variables set SALESFORCE_SECURITY_TOKEN="new_token"`

### Issue: Odoo connection fails

**Solution**: Verify Odoo credentials
1. Test login at your Odoo URL
2. Confirm database name in dropdown
3. Update credentials if needed

---

## Current Status

- [x] DATABASE_URL configured by Railway
- [ ] Salesforce credentials need to be set
- [ ] Odoo credentials need to be set
- [ ] SMTP credentials need to be set
- [ ] Security keys need to be generated
- [ ] Application config can use defaults

**Ready for**: Environment variable configuration and deployment

---

## Time Estimate

- Gather credentials: 5-10 minutes
- Set variables: 2-3 minutes
- Deploy and test: 5-10 minutes
- **Total: 15-25 minutes**

---

## Next Steps

1. **Gather Credentials** (10 min):
   - Get Salesforce instance URL, username, password, security token
   - Get Odoo URL, database name, username, password
   - Generate Gmail app password
   - Generate security keys

2. **Set Variables** (3 min):
   - Use Option 1 (Railway CLI) for fastest setup
   - Or use Option 2 (Web Dashboard) for GUI preference

3. **Deploy** (5 min):
   - Run `railway up`
   - Monitor logs
   - Get deployment URL

4. **Test** (5 min):
   - Test health endpoint
   - Test Salesforce sync
   - Test Odoo sync
   - Generate daily reports

---

**Total Setup Time**: 15-25 minutes
**Status**: Database ready, awaiting credentials
**Guide Version**: 1.0

---

*Generated with Claude Code*
*https://claude.com/claude-code*
*Last Updated: 2025-10-25*
