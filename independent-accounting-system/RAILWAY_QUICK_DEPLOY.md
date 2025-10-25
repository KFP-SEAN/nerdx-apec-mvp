# Railway Quick Deploy Guide - NERDX Independent Accounting System

**Time Required**: 15 minutes
**Last Updated**: 2025-10-25

---

## Prerequisites Completed

- [x] Railway CLI installed (v4.11.0)
- [x] All deployment files ready (Procfile, runtime.txt, railway.json)
- [x] Database schema ready (init_database.sql)
- [x] Application code ready

---

## Step 1: Railway Login (MANUAL - 2 minutes)

Open a NEW terminal window and run:

```bash
cd C:/Users/seans/nerdx-apec-mvp/independent-accounting-system
railway login
```

This will open your browser. Complete the authentication, then return to the terminal.

Verify login:
```bash
railway whoami
```

---

## Step 2: Initialize Project (MANUAL - 1 minute)

In the same terminal:

```bash
railway init
```

When prompted:
- Project name: `nerdx-accounting-system`
- Select: "Create new project"

---

## Step 3: Add PostgreSQL (MANUAL - 1 minute)

```bash
railway add
```

Select: **PostgreSQL**

Wait 10 seconds for database provisioning.

Verify:
```bash
railway variables | grep DATABASE_URL
```

You should see: `DATABASE_URL=postgresql://...`

---

## Step 4: Enable pgvector Extension (MANUAL - 2 minutes)

```bash
railway connect postgresql
```

In the PostgreSQL shell, run:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Verify
SELECT extname, extversion FROM pg_extension WHERE extname IN ('vector', 'uuid-ossp', 'pg_trgm');
```

You should see 3 extensions listed.

Exit PostgreSQL:
```sql
\q
```

---

## Step 5: Initialize Database Schema (MANUAL - 1 minute)

```bash
railway run psql $DATABASE_URL -f init_database.sql
```

Expected output: Multiple "CREATE TABLE", "CREATE INDEX" messages

---

## Step 6: Set Environment Variables (MANUAL - 5 minutes)

### Option A: Interactive (Recommended for first time)

```bash
railway variables --set SALESFORCE_INSTANCE_URL="https://your-instance.salesforce.com"
railway variables --set SALESFORCE_USERNAME="your_email@company.com"
railway variables --set SALESFORCE_PASSWORD="YOUR_PASSWORD"
railway variables --set SALESFORCE_SECURITY_TOKEN="YOUR_TOKEN"

railway variables --set ODOO_URL="https://your-company.odoo.com"
railway variables --set ODOO_DB="your_database_name"
railway variables --set ODOO_USERNAME="your_username"
railway variables --set ODOO_PASSWORD="YOUR_PASSWORD"

railway variables --set SMTP_HOST="smtp.gmail.com"
railway variables --set SMTP_PORT="587"
railway variables --set SMTP_USERNAME="noreply@nerdx.com"
railway variables --set SMTP_PASSWORD="YOUR_APP_PASSWORD"
railway variables --set SMTP_FROM_EMAIL="noreply@nerdx.com"

# Generate secret keys with:
# python -c "import secrets; print(secrets.token_urlsafe(32))"
railway variables --set SECRET_KEY="YOUR_GENERATED_SECRET"
railway variables --set JWT_SECRET_KEY="YOUR_GENERATED_JWT_SECRET"

railway variables --set API_ENVIRONMENT="production"
railway variables --set DEBUG_MODE="False"
```

### Option B: From .env file (if you have one)

```bash
# Create .env file first with all variables, then:
cat .env | while IFS='=' read -r key value; do
  railway variables --set "$key=$value"
done
```

---

## Step 7: Deploy (MANUAL - 3 minutes)

```bash
railway up
```

This will:
1. Upload your code
2. Install dependencies from requirements.txt
3. Start the application with Procfile command

Wait for: "Deployment successful" message

---

## Step 8: Verify Deployment (MANUAL - 2 minutes)

Get your deployment URL:
```bash
railway domain
```

If no domain assigned:
```bash
railway domain add
```

Open in browser:
```bash
railway open
```

Test API:
```bash
# Get deployment URL first
RAILWAY_URL=$(railway domain)

# Health check
curl https://$RAILWAY_URL/health

# API docs
echo "Open: https://$RAILWAY_URL/docs"
```

---

## Step 9: Monitor Deployment

View real-time logs:
```bash
railway logs --follow
```

Check status:
```bash
railway status
```

---

## Troubleshooting

### Issue: "No project linked"

```bash
railway init
```

### Issue: "DATABASE_URL not found"

```bash
railway add
# Select: PostgreSQL
```

### Issue: "Module not found" during deployment

```bash
# Ensure all dependencies are in requirements.txt
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Update dependencies"
git push
railway up
```

### Issue: Email sending fails

1. Go to https://myaccount.google.com/apppasswords
2. Generate new app password
3. Update: `railway variables --set SMTP_PASSWORD="new_password"`

---

## Post-Deployment Checklist

- [ ] Health endpoint returns 200: `https://your-app.railway.app/health`
- [ ] API docs accessible: `https://your-app.railway.app/docs`
- [ ] Database has tables: `railway connect postgresql` then `\dt`
- [ ] Environment variables set: `railway variables`
- [ ] Logs are clean: `railway logs`
- [ ] Can create test cell via API
- [ ] Daily reports generate correctly

---

## Quick Command Reference

```bash
# Deployment
railway up                          # Deploy
railway logs                        # View logs
railway logs --follow               # Real-time logs
railway status                      # Check status
railway open                        # Open in browser

# Database
railway connect postgresql          # Connect to DB
railway run psql $DATABASE_URL      # Run psql commands

# Environment
railway variables                   # List all variables
railway variables --set KEY=VALUE   # Set variable

# Domain
railway domain                      # Show domain
railway domain add                  # Add custom domain

# Project
railway init                        # Initialize/link project
railway whoami                      # Check login status
```

---

## Next Steps After Deployment

1. **Test Salesforce Integration**:
   ```bash
   curl -X POST https://your-app.railway.app/api/sync/salesforce
   ```

2. **Test Odoo Integration**:
   ```bash
   curl -X POST https://your-app.railway.app/api/sync/odoo
   ```

3. **Generate Daily Reports**:
   ```bash
   curl -X POST https://your-app.railway.app/api/reports/generate-all
   ```

4. **Set Up Cron Jobs** (via GitHub Actions or cron-job.org):
   - URL: `https://your-app.railway.app/api/reports/generate-all`
   - Schedule: `0 6 * * *` (daily at 6 AM)
   - Method: POST

5. **Enable Monitoring**:
   - Add Sentry for error tracking
   - Set up UptimeRobot for uptime monitoring

---

## Support

- **Railway Docs**: https://docs.railway.app
- **NERDX Guides**:
  - `RAILWAY_DEPLOYMENT_GUIDE.md` - Full deployment guide
  - `PGVECTOR_AI_GUIDE.md` - AI features guide
  - `QUICK_START_GUIDE.md` - Quick start guide

---

**Deployment Time**: ~15 minutes
**Next**: Continue with Salesforce/Odoo integration testing
