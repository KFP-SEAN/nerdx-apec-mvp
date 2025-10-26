# Railway Deployment Guide - NERDX Independent Accounting System

**Last Updated**: 2025-10-25
**Status**: Production Ready
**Estimated Time**: 30 minutes

---

## Overview

This guide walks you through deploying the NERDX Independent Accounting System to Railway.app, a modern PaaS platform with automatic PostgreSQL database provisioning.

**Why Railway?**
- Automatic HTTPS/SSL certificates
- Built-in PostgreSQL with pgvector support
- Environment variable management
- Auto-scaling and monitoring
- Cost-effective: $15/month for small deployments

---

## Prerequisites

### Required
- [x] GitHub account with repository access
- [x] Railway account (https://railway.app)
- [x] Railway CLI installed
- [x] Git installed locally

### Optional
- [ ] Domain name (for custom domain)
- [ ] Sentry account (for error tracking)

---

## Part 1: Railway CLI Setup (5 minutes)

### 1.1 Install Railway CLI

```bash
# Windows (PowerShell)
iwr https://railway.app/install.ps1 | iex

# macOS/Linux
curl -fsSL https://railway.app/install.sh | sh

# Verify installation
railway --version
```

### 1.2 Login to Railway

```bash
# Login via browser
railway login

# Or use browserless mode
railway login --browserless
# Then click the authentication link in your terminal
```

### 1.3 Link to GitHub Repository

```bash
cd C:/Users/seans/nerdx-apec-mvp/independent-accounting-system

# Initialize Railway project
railway init

# Follow prompts:
# - Create new project: Yes
# - Project name: nerdx-accounting-system
```

---

## Part 2: Database Setup (10 minutes)

### 2.1 Add PostgreSQL Plugin

```bash
# Add PostgreSQL database to your Railway project
railway add postgresql

# Verify database was created
railway variables
# You should see DATABASE_URL automatically set
```

### 2.2 Enable pgvector Extension

Railway's PostgreSQL includes pgvector by default, but you need to enable it:

```bash
# Connect to Railway PostgreSQL
railway connect postgresql

# In PostgreSQL shell, run:
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS pg_trgm;

# Exit
\q
```

### 2.3 Initialize Database Schema

```bash
# Option A: Using Railway connect
railway connect postgresql < init_database.sql

# Option B: Using psql directly with DATABASE_URL
railway variables | grep DATABASE_URL
# Copy the DATABASE_URL and use it:
psql "YOUR_DATABASE_URL" -f init_database.sql
```

---

## Part 3: Environment Variables (5 minutes)

### 3.1 Set Required Environment Variables

```bash
# Salesforce CRM
railway variables --set SALESFORCE_INSTANCE_URL=https://your-instance.salesforce.com
railway variables --set SALESFORCE_USERNAME=your_email@company.com
railway variables --set SALESFORCE_PASSWORD=YOUR_PASSWORD
railway variables --set SALESFORCE_SECURITY_TOKEN=YOUR_TOKEN

# Odoo ERP
railway variables --set ODOO_URL=https://your-company.odoo.com
railway variables --set ODOO_DB=your_database_name
railway variables --set ODOO_USERNAME=your_username
railway variables --set ODOO_PASSWORD=YOUR_PASSWORD

# Email (Resend API - SMTP is blocked on Railway!)
# Get API key from: https://resend.com/api-keys
railway variables --set RESEND_API_KEY=re_your_api_key_here
railway variables --set SMTP_FROM_EMAIL=noreply@yourdomain.com

# IMPORTANT: Railway blocks SMTP ports 25/587/465
# You MUST use Resend API or another HTTP-based email service
# See RAILWAY_EMAIL_SETUP.md for detailed instructions

# Application Settings
railway variables --set API_ENVIRONMENT=production
railway variables --set DEBUG_MODE=False

# Secret Keys (generate with: python -c "import secrets; print(secrets.token_urlsafe(32))")
railway variables --set SECRET_KEY=YOUR_GENERATED_SECRET_KEY
railway variables --set JWT_SECRET_KEY=YOUR_GENERATED_JWT_SECRET
```

### 3.2 Verify Environment Variables

```bash
railway variables

# Check that DATABASE_URL is set automatically by PostgreSQL plugin
# All other variables should be visible
```

---

## Part 4: Deploy to Railway (5 minutes)

### 4.1 Commit and Push Deployment Files

```bash
# Ensure all deployment files are committed
git add Procfile runtime.txt railway.json .dockerignore requirements.txt
git commit -m "Add Railway deployment configuration"
git push origin main
```

### 4.2 Deploy

```bash
# Deploy from current directory
railway up

# Or trigger deployment from GitHub
# Railway will automatically detect changes and deploy
```

### 4.3 Monitor Deployment

```bash
# Watch deployment logs
railway logs

# Check deployment status
railway status

# Expected output:
# Project: nerdx-accounting-system
# Environment: production
# Service: web (running)
# Database: postgresql (running)
```

---

## Part 5: Verification (5 minutes)

### 5.1 Health Check

```bash
# Get your Railway URL
railway open

# Or manually check
railway domain
# Example: nerdx-accounting-system-production.up.railway.app

# Test health endpoint
curl https://your-app.railway.app/health

# Expected response:
# {"status":"ok","database":"connected"}
```

### 5.2 API Documentation

```bash
# Open API docs in browser
railway open
# Navigate to: https://your-app.railway.app/docs
```

### 5.3 Test Database Connection

```bash
# Connect to Railway PostgreSQL
railway connect postgresql

# Check tables
\dt

# Check sample data
SELECT * FROM cells LIMIT 5;

# Exit
\q
```

### 5.4 Test API Endpoints

```bash
# Get all cells
curl https://your-app.railway.app/api/cells

# Create a test cell
curl -X POST https://your-app.railway.app/api/cells \
  -H "Content-Type: application/json" \
  -d '{
    "cell_id": "TEST-001",
    "cell_name": "Test Cell",
    "manager_email": "test@nerdx.com"
  }'
```

---

## Part 6: Custom Domain (Optional)

### 6.1 Add Custom Domain

```bash
# In Railway dashboard or CLI
railway domain add accounting.yourdomain.com

# Follow instructions to update DNS:
# 1. Add CNAME record in your DNS provider
# 2. Point to: your-app.railway.app
# 3. Wait for DNS propagation (5-30 minutes)
```

### 6.2 Verify SSL Certificate

```bash
# Railway automatically provisions SSL certificates
# Verify HTTPS is working:
curl -I https://accounting.yourdomain.com

# Should return: HTTP/2 200
```

---

## Part 7: Monitoring & Maintenance

### 7.1 View Logs

```bash
# Real-time logs
railway logs --follow

# Filter logs
railway logs --filter error

# Export logs
railway logs > logs_$(date +%Y%m%d).txt
```

### 7.2 Database Backups

```bash
# Manual backup
railway connect postgresql
pg_dump -U postgres > backup_$(date +%Y%m%d).sql

# Automatic backups (Railway Pro plan)
# Backups are automatically taken daily
```

### 7.3 Scaling

```bash
# Railway auto-scales based on traffic
# To manually adjust:

# In Railway dashboard:
# 1. Go to Project Settings
# 2. Click on "Resources"
# 3. Adjust memory/CPU limits
```

---

## Part 8: CI/CD Setup (Optional)

### 8.1 GitHub Actions Integration

Railway automatically deploys on git push to main branch.

To customize, create `.github/workflows/railway-deploy.yml`:

```yaml
name: Railway Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install Railway CLI
        run: npm install -g @railway/cli

      - name: Deploy to Railway
        run: railway up
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
```

### 8.2 Get Railway Token

```bash
railway token
# Add this token to GitHub Secrets as RAILWAY_TOKEN
```

---

## Part 9: Cron Jobs for Daily Reports

### 9.1 Install Railway Cron Plugin

```bash
# Railway doesn't have built-in cron
# Use Railway + GitHub Actions instead

# Create .github/workflows/daily-reports.yml
```

```yaml
name: Daily Reports

on:
  schedule:
    - cron: '0 6 * * *'  # Every day at 6 AM UTC
  workflow_dispatch:  # Manual trigger

jobs:
  generate-reports:
    runs-on: ubuntu-latest
    steps:
      - name: Trigger daily report endpoint
        run: |
          curl -X POST https://your-app.railway.app/api/reports/generate-all \
            -H "Authorization: Bearer ${{ secrets.API_KEY }}"
```

### 9.2 Alternative: Use External Cron Service

- **cron-job.org** (Free)
- **EasyCron** (Free tier available)
- **AWS EventBridge** ($0.001/event)

Example configuration:
- URL: `https://your-app.railway.app/api/reports/generate-all`
- Method: POST
- Schedule: `0 6 * * *` (6 AM daily)
- Headers: `Authorization: Bearer YOUR_API_KEY`

---

## Part 10: Cost Optimization

### 10.1 Resource Usage Monitoring

```bash
# Check current usage
railway status

# View metrics in Railway dashboard:
# - CPU usage
# - Memory usage
# - Network traffic
```

### 10.2 Estimated Costs

| Service | Plan | Monthly Cost |
|---------|------|--------------|
| Railway Compute | Hobby | $5 |
| PostgreSQL | Standard | $10 |
| **Total** | | **$15/month** |

### 10.3 Cost Optimization Tips

1. **Use connection pooling**: Already configured in `database.py`
2. **Enable caching**: Redis integration (optional, +$5/month)
3. **Optimize queries**: Add database indexes (already included in `init_database.sql`)
4. **Monitor logs**: Reduce logging in production

---

## Troubleshooting

### Issue: Deployment fails with "Module not found"

**Solution**: Ensure all dependencies are in `requirements.txt`

```bash
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Update dependencies"
git push
```

### Issue: Database connection error

**Solution**: Verify DATABASE_URL is set

```bash
railway variables | grep DATABASE_URL

# If missing, re-add PostgreSQL plugin
railway add postgresql
```

### Issue: Email sending fails

**Solution**: Railway blocks SMTP ports - use Resend API instead

**IMPORTANT: Railway blocks SMTP ports (25, 587, 465) for security reasons.**

You MUST use HTTP-based email APIs like Resend:

1. Sign up at https://resend.com
2. Verify your domain in Resend dashboard
3. Get API key from https://resend.com/api-keys
4. Update Railway variables:
   ```bash
   railway variables --set RESEND_API_KEY=re_your_api_key_here
   railway variables --set SMTP_FROM_EMAIL=noreply@yourdomain.com
   ```
5. See [RAILWAY_EMAIL_SETUP.md](./RAILWAY_EMAIL_SETUP.md) for detailed setup guide

### Issue: Out of memory errors

**Solution**: Increase memory limit in Railway dashboard

1. Go to Project Settings
2. Click "Resources"
3. Increase memory to 1GB or 2GB

---

## Security Checklist

- [ ] All environment variables are set (no placeholder values)
- [ ] `SECRET_KEY` and `JWT_SECRET_KEY` are randomly generated (min 32 chars)
- [ ] Database credentials are secure (use Railway-generated DATABASE_URL)
- [ ] CORS origins are configured for production domain only
- [ ] API rate limiting is enabled
- [ ] HTTPS/SSL is enforced (automatic with Railway)
- [ ] `.env` file is in `.gitignore` (never commit secrets)

---

## Post-Deployment Checklist

- [ ] Health check endpoint returns 200 OK
- [ ] API documentation is accessible at `/docs`
- [ ] Database schema is initialized (tables exist)
- [ ] Sample cells are created
- [ ] Daily report generation works
- [ ] **Email sending works** (test with: `python test_email.py your_email@example.com`)
- [ ] Resend API key is configured and domain is verified
- [ ] Logs are clean (no errors)
- [ ] Custom domain is configured (if applicable)
- [ ] SSL certificate is valid
- [ ] Monitoring/alerts are set up

---

## Next Steps

1. **Configure Salesforce/Odoo Integration**:
   - Test real data synchronization
   - Set up webhooks for real-time updates

2. **Enable Monitoring**:
   - Add Sentry for error tracking
   - Set up uptime monitoring (UptimeRobot, Pingdom)

3. **Set Up Backups**:
   - Schedule daily database backups
   - Store backups in S3 or Railway volumes

4. **Implement CI/CD**:
   - Add automated tests
   - Set up staging environment

5. **Add AI Features** (Priority 3):
   - Integrate pgvector for embeddings
   - Implement similarity search
   - Add predictive analytics

---

## Support & Resources

### Documentation
- Railway Docs: https://docs.railway.app
- FastAPI Docs: https://fastapi.tiangolo.com
- PostgreSQL + pgvector: https://github.com/pgvector/pgvector

### Railway Support
- Discord: https://discord.gg/railway
- GitHub: https://github.com/railwayapp
- Email: team@railway.app

### NERDX Support
- Project README: `README.md`
- Database Guide: `DATABASE_OPTIMIZATION_ANALYSIS.md`
- Quick Start: `QUICK_START_GUIDE.md`

---

## Appendix A: Environment Variable Reference

| Variable | Required | Example | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Yes (auto) | `postgresql://...` | Auto-set by Railway PostgreSQL plugin |
| `SALESFORCE_INSTANCE_URL` | Yes | `https://mycompany.salesforce.com` | Salesforce instance URL |
| `SALESFORCE_USERNAME` | Yes | `user@company.com` | Salesforce login email |
| `SALESFORCE_PASSWORD` | Yes | `MyPassword123` | Salesforce password |
| `SALESFORCE_SECURITY_TOKEN` | Yes | `ABC123DEF456` | Salesforce security token |
| `ODOO_URL` | Yes | `https://mycompany.odoo.com` | Odoo instance URL |
| `ODOO_DB` | Yes | `production` | Odoo database name |
| `ODOO_USERNAME` | Yes | `admin` | Odoo username |
| `ODOO_PASSWORD` | Yes | `MyPassword123` | Odoo password |
| `RESEND_API_KEY` | **Yes** | `re_abc123...` | **Resend API key (SMTP blocked on Railway)** |
| `SMTP_FROM_EMAIL` | Yes | `noreply@yourdomain.com` | Email sender address (domain must be verified in Resend) |
| `SECRET_KEY` | Yes | `random_32_char_string` | Flask/FastAPI secret key |
| `JWT_SECRET_KEY` | Yes | `random_32_char_string` | JWT signing key |
| `API_ENVIRONMENT` | No | `production` | Environment name |
| `DEBUG_MODE` | No | `False` | Debug mode (set to False in production) |

---

## Appendix B: Quick Command Reference

```bash
# Deployment
railway up                          # Deploy current directory
railway logs                        # View logs
railway status                      # Check deployment status
railway open                        # Open app in browser

# Database
railway connect postgresql          # Connect to PostgreSQL shell
railway variables                   # List all environment variables
railway variables --set KEY=VALUE   # Set environment variable

# Domain
railway domain                      # List domains
railway domain add example.com      # Add custom domain

# Monitoring
railway logs --follow               # Real-time logs
railway logs --filter error         # Filter error logs

# Cleanup
railway down                        # Stop all services
railway delete                      # Delete project
```

---

**Deployment Guide Version**: 1.0
**Last Tested**: 2025-10-25
**Maintainer**: NERDX Development Team
