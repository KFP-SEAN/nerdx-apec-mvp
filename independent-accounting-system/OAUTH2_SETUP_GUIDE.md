# OAuth2 Setup Guide - NERDX Accounting System

**Date**: 2025-10-26
**Security Level**: Enterprise-Grade
**Time Required**: 30 minutes

---

## Overview

This guide shows how to set up OAuth2 authentication for maximum security:

**Benefits**:
- No password storage required
- Automatic token refresh
- Granular permission control
- Audit trails
- Token expiration management
- Easy revocation

**vs. Password-based auth**:
- ❌ Password: Stored in plain text, never expires, full access
- ✅ OAuth2: No storage, auto-expires, limited scope, revocable

---

## Part 1: Salesforce OAuth2 Setup (15 minutes)

### Step 1: Create Connected App

1. **Login to Salesforce** → Setup

2. **Navigate to**:
   - Setup → Platform Tools → Apps → App Manager
   - Click "New Connected App"

3. **Configure Connected App**:
   ```
   Connected App Name: NERDX Accounting System
   API Name: NERDX_Accounting_System
   Contact Email: your-email@company.com
   ```

4. **Enable OAuth Settings**:
   - ✅ Enable OAuth Settings
   - Callback URL: `https://your-app.railway.app/oauth2/callback`
     (or `https://localhost:8000/oauth2/callback` for testing)

5. **Select OAuth Scopes**:
   ```
   Selected OAuth Scopes:
   - Access and manage your data (api)
   - Perform requests on your behalf at any time (refresh_token, offline_access)
   ```

   **Recommended (minimum required)**:
   ```
   - Access your basic information (id, profile, email, address, phone)
   - Access and manage your data (api)
   ```

6. **Click Save**

7. **Enable Client Credentials Flow**:
   - After saving, click "Manage"
   - Edit Policies
   - **Permitted Users**: Admin approved users are pre-authorized
   - **IP Relaxation**: Relax IP restrictions (or add Railway IP)
   - ✅ **Enable Client Credentials Flow**
   - Save

### Step 2: Get OAuth2 Credentials

1. **View the Connected App** you just created

2. **Click "Manage Consumer Details"**
   - You may need to verify with 2FA code

3. **Copy these values**:
   ```
   Consumer Key (Client ID): 3MVG9n...abc123...xyz789
   Consumer Secret (Client Secret): 1234567890ABCDEF...
   ```

4. **Set Railway Environment Variables**:
   ```bash
   railway variables set SALESFORCE_CLIENT_ID="3MVG9n...abc123...xyz789"
   railway variables set SALESFORCE_CLIENT_SECRET="1234567890ABCDEF..."
   railway variables set SALESFORCE_INSTANCE_URL="https://your-company.salesforce.com"
   railway variables set SALESFORCE_TOKEN_URL="https://login.salesforce.com/services/oauth2/token"
   ```

### Step 3: Test Salesforce OAuth2

```bash
cd C:/Users/seans/nerdx-apec-mvp/independent-accounting-system

# Set environment variables locally for testing
export SALESFORCE_CLIENT_ID="your_client_id"
export SALESFORCE_CLIENT_SECRET="your_client_secret"
export SALESFORCE_INSTANCE_URL="https://your-company.salesforce.com"

# Run test
python salesforce_oauth.py
```

Expected output:
```
[OAuth2] Requesting new access token...
[OAuth2] Token acquired successfully (expires in 7200s)
[SUCCESS] Salesforce OAuth2 connection test passed
  - Instance: https://your-company.salesforce.com
  - Token valid until: 2025-10-26 14:30:00
[OK] Fetched 5 opportunities
```

---

## Part 2: Odoo API Key Setup (10 minutes)

### Step 1: Generate API Key (Odoo 13+)

1. **Login to Odoo**

2. **Navigate to User Preferences**:
   - Click your profile (top right)
   - Preferences
   - Account Security tab

3. **Generate API Key**:
   - Click "New API Key"
   - Description: `NERDX Accounting System`
   - Click "Generate"
   - **Copy the API Key** (shown only once!)
   ```
   Example: odoo_api_ABCD1234EFGH5678IJKL9012
   ```

4. **Set Railway Environment Variables**:
   ```bash
   railway variables set ODOO_URL="https://your-company.odoo.com"
   railway variables set ODOO_DB="your_database_name"
   railway variables set ODOO_USERNAME="your_username"
   railway variables set ODOO_API_KEY="odoo_api_ABCD1234..."
   ```

### Step 2: Test Odoo API Key

```bash
# Set environment variables locally
export ODOO_URL="https://your-company.odoo.com"
export ODOO_DB="your_database_name"
export ODOO_USERNAME="your_username"
export ODOO_API_KEY="odoo_api_ABCD1234..."

# Run test
python salesforce_oauth.py
```

Expected output:
```
[SUCCESS] Odoo API Key authentication successful (UID: 2)
[SUCCESS] Odoo API Key connection test passed
  - URL: https://your-company.odoo.com
  - Database: production
  - User: Admin
[OK] Fetched 5 expense records
```

---

## Part 3: Gmail OAuth2 Setup (5 minutes)

### Option A: Gmail App Password (Recommended for simplicity)

1. **Go to**: https://myaccount.google.com/apppasswords

2. **Select**:
   - App: Mail
   - Device: Other (Custom name)
   - Name: `NERDX Accounting System`

3. **Generate** → Copy 16-character password
   ```
   Example: abcd efgh ijkl mnop
   ```

4. **Set Railway Environment Variables**:
   ```bash
   railway variables set SMTP_HOST="smtp.gmail.com"
   railway variables set SMTP_PORT="587"
   railway variables set SMTP_USERNAME="noreply@nerdx.com"
   railway variables set SMTP_PASSWORD="abcdefghijklmnop"
   railway variables set SMTP_FROM_EMAIL="noreply@nerdx.com"
   ```

### Option B: Gmail OAuth2 (Advanced)

For full OAuth2 with Gmail (more complex, better security):

1. **Google Cloud Console**: https://console.cloud.google.com

2. **Create Project** → Enable Gmail API

3. **Create OAuth2 Credentials**
   - Type: OAuth client ID
   - Application type: Web application
   - Authorized redirect URIs: `https://your-app.railway.app/oauth2/gmail/callback`

4. **Download credentials JSON**

5. **Set environment variables**:
   ```bash
   railway variables set GMAIL_CLIENT_ID="...apps.googleusercontent.com"
   railway variables set GMAIL_CLIENT_SECRET="GOCSPX-..."
   railway variables set GMAIL_REFRESH_TOKEN="1//..."
   ```

---

## Part 4: Security Keys Generation

Generate secure random keys for application security:

```bash
# SECRET_KEY (for general app security)
python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"

# JWT_SECRET_KEY (for JWT token signing)
python -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_urlsafe(32))"
```

Copy the generated keys and set them:

```bash
railway variables set SECRET_KEY="<generated_secret_key>"
railway variables set JWT_SECRET_KEY="<generated_jwt_secret>"
railway variables set API_ENVIRONMENT="production"
railway variables set DEBUG_MODE="False"
```

---

## Part 5: Verify All Settings

### Railway Variables Checklist

```bash
railway variables
```

Expected variables:

```
# Database (auto-configured)
DATABASE_URL=postgresql://...

# Salesforce OAuth2
SALESFORCE_CLIENT_ID=3MVG9n...
SALESFORCE_CLIENT_SECRET=1234567890ABCDEF...
SALESFORCE_INSTANCE_URL=https://your-company.salesforce.com
SALESFORCE_TOKEN_URL=https://login.salesforce.com/services/oauth2/token

# Odoo API Key
ODOO_URL=https://your-company.odoo.com
ODOO_DB=your_database_name
ODOO_USERNAME=your_username
ODOO_API_KEY=odoo_api_...

# Email (App Password)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=noreply@nerdx.com
SMTP_PASSWORD=abcdefghijklmnop
SMTP_FROM_EMAIL=noreply@nerdx.com

# Application Security
SECRET_KEY=<random_32_chars>
JWT_SECRET_KEY=<random_32_chars>
API_ENVIRONMENT=production
DEBUG_MODE=False
```

---

## Part 6: Deploy to Railway

Now that OAuth2 is configured, deploy the application:

```bash
cd C:/Users/seans/nerdx-apec-mvp/independent-accounting-system

# Deploy
railway up

# Monitor logs
railway logs --follow
```

Expected deployment output:
```
Building...
Installing dependencies...
Starting application...
[OAuth2] Salesforce OAuth2 service initialized
[OAuth2] Odoo API Key service initialized
[INFO] Application started successfully
[INFO] Listening on port 8000
```

---

## Part 7: Test Integrations

```bash
# Get Railway URL
RAILWAY_URL=$(railway domain)

# Test health
curl https://$RAILWAY_URL/health

# Test Salesforce OAuth2
curl -X POST https://$RAILWAY_URL/api/sync/salesforce

# Test Odoo API Key
curl -X POST https://$RAILWAY_URL/api/sync/odoo

# Generate daily reports
curl -X POST https://$RAILWAY_URL/api/reports/generate-all
```

---

## Security Advantages Summary

### Before (Password-based):
```
SALESFORCE_PASSWORD=MyPassword123        ← Stored in plain text
ODOO_PASSWORD=MyPassword456               ← Never expires
SMTP_PASSWORD=MyPassword789               ← Full account access
```

**Risks**:
- Passwords in environment variables
- Terminal history exposure
- No audit trail
- No automatic rotation
- Full account access

### After (OAuth2/API Keys):
```
SALESFORCE_CLIENT_SECRET=ABC123...        ← Limited scope, expires
ODOO_API_KEY=odoo_api_XYZ789...          ← Revocable, user-specific
SMTP_PASSWORD=app_password_...            ← App-specific, revocable
```

**Benefits**:
- ✅ No user passwords stored
- ✅ Tokens auto-expire (2 hours default)
- ✅ Limited permissions (read-only possible)
- ✅ Audit trail in Salesforce/Odoo
- ✅ Easy revocation
- ✅ IP restrictions possible

---

## Troubleshooting

### Issue: "Invalid client credentials"

**Salesforce**:
- Verify Client ID and Secret are correct
- Check Connected App is enabled
- Ensure Client Credentials Flow is enabled
- Verify IP restrictions allow Railway IP

**Solution**:
```bash
# Re-copy credentials from Salesforce
railway variables set SALESFORCE_CLIENT_ID="<new_client_id>"
railway variables set SALESFORCE_CLIENT_SECRET="<new_secret>"
```

### Issue: "Invalid API key"

**Odoo**:
- Regenerate API key in Odoo preferences
- Verify username is correct
- Check database name matches

**Solution**:
```bash
# Generate new API key in Odoo, then:
railway variables set ODOO_API_KEY="<new_api_key>"
```

### Issue: "Token expired"

**This is normal**! OAuth2 tokens expire by design.

The `salesforce_oauth.py` service automatically refreshes tokens:
```python
# Automatic token refresh
if token_expired:
    new_token = refresh_token()  # Happens automatically
```

---

## Advanced: Token Rotation

For enhanced security, rotate credentials regularly:

### Salesforce Connected App Rotation (Every 90 days)

```bash
# 1. Create new Connected App with different name
# 2. Get new Client ID/Secret
# 3. Update Railway variables
railway variables set SALESFORCE_CLIENT_ID="<new_id>"
railway variables set SALESFORCE_CLIENT_SECRET="<new_secret>"

# 4. Test deployment
railway up

# 5. After successful deployment, delete old Connected App
```

### Odoo API Key Rotation (Every 90 days)

```bash
# 1. Generate new API key in Odoo
# 2. Update Railway
railway variables set ODOO_API_KEY="<new_key>"

# 3. Test deployment
railway up

# 4. Revoke old API key in Odoo preferences
```

---

## Monitoring & Auditing

### Salesforce Audit Trail

View OAuth2 access logs:
- Setup → Security → Login History
- Setup → Security → API Usage
- Setup → Identity → OAuth and OpenID Connect Logs

### Odoo Access Logs

View API key usage:
- Settings → Technical → Logging → Audit

---

## Next Steps

1. ✅ **OAuth2 Setup Complete**
2. **Deploy Application**: `railway up`
3. **Test Integrations**: Run test commands above
4. **Set Up Monitoring**: Add Sentry for error tracking
5. **Configure Cron**: Schedule daily reports
6. **Document Credentials**: Store Client IDs (not secrets!) in documentation

---

## Support Resources

- **Salesforce OAuth2**: https://help.salesforce.com/s/articleView?id=sf.connected_app_client_credentials_setup.htm
- **Odoo API Keys**: https://www.odoo.com/documentation/16.0/developer/reference/external_api.html
- **Railway Variables**: https://docs.railway.app/develop/variables

---

**Setup Time**: 30 minutes
**Security Level**: Enterprise-Grade ⭐⭐⭐⭐⭐
**Maintenance**: Rotate every 90 days

---

*Generated with Claude Code*
*https://claude.com/claude-code*
*Last Updated: 2025-10-26*
