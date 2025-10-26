# NERD12 Warm Lead Generation - Railway Deployment Guide

## Quick Deployment Steps

### 1. Railway Dashboard Deployment (Recommended)

1. **Go to Railway Dashboard**: https://railway.app/dashboard
2. **Create New Project** or select existing project
3. **Add New Service**:
   - Click "New" → "GitHub Repo"
   - Select repository: `KFP-SEAN/nerdx-apec-mvp`
   - Set Root Directory: `warm-lead-generation`
4. **Configure Environment Variables** (see below)
5. **Deploy**

### 2. Required Environment Variables

Configure these in Railway Dashboard → Service → Variables:

```bash
# API Configuration
API_ENVIRONMENT=production
API_HOST=0.0.0.0

# Salesforce Integration (REQUIRED)
SALESFORCE_INSTANCE_URL=https://your-instance.salesforce.com
SALESFORCE_USERNAME=your-salesforce-username
SALESFORCE_PASSWORD=your-salesforce-password
SALESFORCE_SECURITY_TOKEN=your-security-token
SALESFORCE_CONSUMER_KEY=your-consumer-key
SALESFORCE_CONSUMER_SECRET=your-consumer-secret

# Helios Integration (REQUIRED)
HELIOS_API_URL=https://your-helios-instance.railway.app
HELIOS_API_KEY=your-helios-api-key

# NBRS Weights (Optional - defaults provided)
NBRS_WEIGHT_BRAND_AFFINITY=0.40
NBRS_WEIGHT_MARKET_POSITIONING=0.35
NBRS_WEIGHT_DIGITAL_PRESENCE=0.25

# Tier Thresholds (Optional - defaults provided)
NBRS_THRESHOLD_TIER1=80.0
NBRS_THRESHOLD_TIER2=60.0
NBRS_THRESHOLD_TIER3=40.0

# Target Revenue
TARGET_MONTHLY_REVENUE_KRW=500000000
```

### 3. Salesforce Setup

Before deployment, complete Salesforce configuration:

1. **Create Custom Fields** on Lead object:
   - `NBRS_Score__c` (Number 5,2)
   - `NBRS_Tier__c` (Picklist: TIER1, TIER2, TIER3, TIER4)
   - `Brand_Affinity_Score__c` (Number 5,2)
   - `Market_Positioning_Score__c` (Number 5,2)
   - `Digital_Presence_Score__c` (Number 5,2)
   - `NBRS_Calculated_Date__c` (DateTime)
   - `Priority_Rank__c` (Number 5,0)
   - `Next_Action__c` (Text 255)

2. **Create Platform Event** `NBRS_Calculation__e`:
   - See `SALESFORCE_SETUP.md` for complete field list

3. **Create Auto-Assignment Flow**:
   - Trigger: Platform Event `NBRS_Calculation__e`
   - Actions based on tier (TIER1-4)

See `SALESFORCE_SETUP.md` for detailed instructions.

### 4. Helios Service Deployment

The warm-lead-generation system depends on Helios for data enrichment.

**Deploy Helios first**:
1. Railway Dashboard → New Service
2. Select `helios-model` from repo
3. Note the deployment URL
4. Use this URL in `HELIOS_API_URL` env variable

### 5. Post-Deployment Verification

After deployment, verify the system:

```bash
# Health check
curl https://your-service.railway.app/health

# Test NBRS calculation
curl -X POST https://your-service.railway.app/api/v1/lead-scoring/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "lead_id": "test-001",
    "company_name": "Test Corp",
    "brand_affinity": {
      "salesforce_activity_score": 80,
      "email_engagement_score": 85,
      "meeting_history_score": 75,
      "relationship_duration_months": 18,
      "contact_frequency_score": 80,
      "decision_maker_access": true,
      "nps_score": 70,
      "testimonial_provided": true,
      "reference_willing": true
    },
    "market_positioning": {
      "annual_revenue_usd": 50000000,
      "employee_count": 250,
      "marketing_budget_usd": 2000000,
      "target_industry_match": true,
      "target_geography_match": true,
      "pain_point_alignment": 85,
      "revenue_growth_yoy_percent": 25,
      "expansion_plans": true
    },
    "digital_presence": {
      "website_traffic_monthly": 100000,
      "social_media_followers": 15000,
      "content_engagement_score": 75,
      "has_modern_website": true,
      "uses_marketing_automation": true,
      "has_mobile_app": false,
      "ecommerce_enabled": true
    },
    "update_salesforce": false
  }'

# Check statistics
curl https://your-service.railway.app/api/v1/lead-scoring/stats
```

### 6. Monitoring

Monitor system performance:

- **Railway Logs**: Check deployment logs in Railway dashboard
- **Health Endpoint**: `GET /health`
- **Statistics**: `GET /api/v1/lead-scoring/stats`
- **Salesforce Dashboard**: Monitor lead tier distribution

### 7. Troubleshooting

**Common Issues**:

1. **Salesforce Connection Error**:
   - Verify all Salesforce credentials
   - Check security token is current
   - Ensure Connected App is configured

2. **Helios Connection Error**:
   - Verify HELIOS_API_URL is correct
   - Check Helios service is running
   - Verify API key is valid

3. **Deployment Fails**:
   - Check Railway logs
   - Verify all dependencies in requirements.txt
   - Ensure Python version compatibility (3.9+)

## API Endpoints

Once deployed, the following endpoints are available:

- `GET /health` - Health check
- `GET /docs` - Interactive API documentation (Swagger UI)
- `POST /api/v1/lead-scoring/calculate` - Calculate NBRS for a lead
- `POST /api/v1/lead-scoring/enrich-and-score` - Enrich via Helios + score
- `GET /api/v1/lead-scoring/top-leads?n=10` - Get top N leads
- `GET /api/v1/lead-scoring/by-tier/{tier}` - Get leads by tier
- `GET /api/v1/lead-scoring/pipeline-value` - Pipeline value breakdown
- `GET /api/v1/lead-scoring/stats` - Scoring statistics

## Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│  Salesforce │◄────►│  NERDX       │◄────►│   Helios    │
│   CRM       │      │  API Server  │      │   Model     │
└─────────────┘      └──────────────┘      └─────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │  NBRS Engine │
                     │  (Scoring)   │
                     └──────────────┘
```

## System Goal

**Objective**: Increase MRR to 500M KRW by identifying the top 10% highest-value warm leads using NBRS (NERD Brand Resonance Score).

**Tier Classification**:
- TIER1 (80-100): Top priority - immediate sales engagement
- TIER2 (60-79): High priority - strategic outreach
- TIER3 (40-59): Medium priority - nurturing campaigns
- TIER4 (0-39): Low priority - long-term nurturing

## Support

For issues or questions:
- Slack: #nerdx-warm-leads
- Email: sean@koreafnbpartners.com
- Documentation: See README.md and SALESFORCE_SETUP.md
