# NERD12 Warm Lead Generation - Final Setup Guide

## 🎯 Current Status: 95% Complete - 2 Steps Remaining

### ✅ What's Already Done

1. **Railway Service Created**
   - Service: `warm-lead-generation`
   - Service ID: `31e0581c-9ec4-4805-a9e2-abf4c7ad907e`
   - Project: `nerdx-accounting-system`
   - GitHub: KFP-SEAN/nerdx-apec-mvp

2. **All 17 Environment Variables Set via CLI**
   - API Configuration (2)
   - Salesforce Credentials (6) - placeholders
   - Helios Integration (2) - placeholders
   - NBRS Weights (3)
   - Tier Thresholds (3)
   - Revenue Target (1)

3. **Code Deployed to GitHub**
   - All files in `warm-lead-generation/` directory
   - Procfile, railway.json configured
   - Requirements.txt ready

---

## 🔧 Final Setup Steps (Railway Dashboard)

### Railway Dashboard URL:
```
https://railway.app/project/53c2f700-32ca-491f-b525-8552114b6fd6
```

---

### Step 1: Set Root Directory (REQUIRED)

**Why?** Railway needs to know which directory contains your application.

1. Open Railway Dashboard (URL above)
2. Click on `warm-lead-generation` service
3. Go to **Settings** tab (left sidebar)
4. Scroll to **Source** section
5. Find **Root Directory** field
6. Enter: `warm-lead-generation`
7. Click outside the field or press Enter (auto-saves)

**Verification:** You should see "warm-lead-generation" in the Root Directory field.

---

### Step 2: Update Environment Variables (REQUIRED)

**Why?** Placeholder values need to be replaced with real credentials.

Still in Railway Dashboard:

1. Go to **Variables** tab (left sidebar)
2. Click on each variable below and update with actual values:

#### Salesforce Credentials

```plaintext
SALESFORCE_INSTANCE_URL
  Current: https://your-instance.salesforce.com
  Update to: https://[YOUR-ACTUAL-INSTANCE].salesforce.com

SALESFORCE_USERNAME
  Current: your-username@domain.com
  Update to: [YOUR-ACTUAL-USERNAME]@domain.com

SALESFORCE_PASSWORD
  Current: your-password
  Update to: [YOUR-ACTUAL-PASSWORD]

SALESFORCE_SECURITY_TOKEN
  Current: your-token
  Update to: [YOUR-ACTUAL-TOKEN]

SALESFORCE_CONSUMER_KEY
  Current: your-consumer-key
  Update to: [YOUR-CONNECTED-APP-CONSUMER-KEY]

SALESFORCE_CONSUMER_SECRET
  Current: your-consumer-secret
  Update to: [YOUR-CONNECTED-APP-CONSUMER-SECRET]
```

#### Helios Integration

```plaintext
HELIOS_API_URL
  Current: https://your-helios-instance.railway.app
  Update to: https://[YOUR-HELIOS-SERVICE].railway.app
  (Deploy Helios first if not done)

HELIOS_API_KEY
  Current: your-helios-api-key
  Update to: [YOUR-ACTUAL-HELIOS-KEY]
```

**Note:** Variables auto-save when you click outside the field.

---

### Step 3: Monitor Deployment (Automatic)

After updating variables, Railway will automatically trigger a deployment.

1. Go to **Deployments** tab
2. Watch the latest deployment
3. Click on the deployment to see build logs
4. Wait for "Build successful" message
5. Wait for "Deployment live" status

**Typical deployment time:** 2-5 minutes

---

## ✅ Verification & Testing

### Once Deployment is Complete

Railway will provide a public URL. It will look like:
```
https://warm-lead-generation-production.up.railway.app
```

### Test 1: Health Check

```bash
curl https://warm-lead-generation-production.up.railway.app/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "service": "NERDX Warm Lead Generation",
  "version": "1.0.0",
  "environment": "production"
}
```

### Test 2: API Documentation

Open in browser:
```
https://warm-lead-generation-production.up.railway.app/docs
```

You should see FastAPI's interactive API documentation (Swagger UI).

### Test 3: Statistics Endpoint

```bash
curl https://warm-lead-generation-production.up.railway.app/api/v1/lead-scoring/stats
```

**Expected Response:**
```json
{
  "total_leads_scored": 0,
  "tier_distribution": {
    "TIER1": 0,
    "TIER2": 0,
    "TIER3": 0,
    "TIER4": 0
  },
  "average_nbrs_score": 0,
  "target_monthly_revenue_krw": 500000000
}
```

### Test 4: NBRS Calculation (Full Test)

Use the test script:
```bash
cd C:/Users/seans/nerdx-apec-mvp/warm-lead-generation
./test_deployment.sh <RAILWAY_URL>
```

Or manually:
```bash
curl -X POST https://warm-lead-generation-production.up.railway.app/api/v1/lead-scoring/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "lead_id": "test-prod-001",
    "company_name": "Test Production Corp",
    "brand_affinity": {
      "past_interaction_score": 85,
      "email_engagement_score": 90,
      "meeting_history_score": 80,
      "relationship_duration_score": 85,
      "contact_frequency_score": 85,
      "decision_maker_access_score": 95,
      "nps_score": 90,
      "testimonial_provided": true,
      "reference_willing": true
    },
    "market_positioning": {
      "annual_revenue_krw": 100000000000,
      "employee_count": 500,
      "marketing_budget_krw": 1000000000,
      "target_industry_match": true,
      "target_geography_match": true,
      "pain_point_alignment_score": 90,
      "revenue_growth_yoy": 30,
      "expansion_plans_score": 85
    },
    "digital_presence": {
      "website_traffic_monthly": 100000,
      "social_media_followers": 25000,
      "content_engagement_score": 85,
      "modern_website": true,
      "marketing_automation": true,
      "mobile_app": true,
      "ecommerce_enabled": true
    },
    "update_salesforce": false
  }'
```

**Expected Response:** NBRS score calculation with tier assignment.

---

## 🚨 Troubleshooting

### Deployment Failed

1. Check **Deployments** tab for error logs
2. Common issues:
   - Missing dependencies in requirements.txt
   - Wrong root directory
   - Invalid environment variables
   - Python version mismatch

### Service Not Starting

1. Check **Logs** tab for runtime errors
2. Verify environment variables are set correctly
3. Ensure Salesforce credentials are valid
4. Confirm Helios service is running (if deployed)

### API Returns 500 Error

1. Check logs for Python exceptions
2. Verify Salesforce connection
3. Test with `update_salesforce: false` first
4. Check NBRS calculation logic

---

## 📋 Deployment Checklist

Before marking as complete, verify:

- [ ] Root directory set to `warm-lead-generation`
- [ ] All 8 placeholder variables updated with real values
- [ ] Deployment completed successfully
- [ ] Health endpoint returns 200 OK
- [ ] API documentation accessible at /docs
- [ ] Statistics endpoint working
- [ ] NBRS calculation test passes
- [ ] Salesforce integration tested (if credentials provided)
- [ ] Helios integration tested (if service deployed)

---

## 🎯 Next Steps After Deployment

### 1. Salesforce Configuration (If Not Done)

See `SALESFORCE_SETUP.md` for:
- Custom fields on Lead object
- Platform Event `NBRS_Calculation__e`
- Process Builder for auto-assignment
- Email templates
- Reports and dashboards

### 2. Helios Service Deployment

If Helios is not deployed yet:
1. Deploy Helios model service to Railway
2. Update `HELIOS_API_URL` variable
3. Test Helios integration

### 3. Production Testing

1. Test with real Salesforce lead data
2. Verify NBRS calculations are accurate
3. Test tier assignments
4. Validate Salesforce updates
5. Monitor API performance

### 4. Monitoring & Alerts

1. Set up Railway monitoring
2. Configure error alerts
3. Track API metrics
4. Monitor NBRS score distribution

---

## 📊 System Architecture

```
User/System
    ↓
Railway (warm-lead-generation)
    ↓
┌──────────────┬──────────────┬──────────────┐
│              │              │              │
│  Salesforce  │   Helios     │   NBRS      │
│  Integration │   AI Model   │   Engine    │
│              │              │              │
└──────────────┴──────────────┴──────────────┘
```

**Goal:** Identify top 10% warm leads to achieve 500M KRW MRR

---

## 📞 Support

### Railway Issues
- Dashboard: https://railway.app/project/53c2f700-32ca-491f-b525-8552114b6fd6
- Logs tab for runtime errors
- Deployments tab for build issues

### Salesforce Issues
- Verify credentials in Variables tab
- Test with `update_salesforce: false` first
- Check Salesforce API limits

### Helios Issues
- Ensure Helios service is deployed
- Verify HELIOS_API_URL is correct
- Test Helios endpoint directly

---

**Deployment Date:** 2025-10-26
**Status:** Ready for Final Configuration
**Completion:** 95% → 100% after Steps 1 & 2
