# NERDX APEC MVP - Final Deployment Instructions

**Date**: 2025-10-27
**Status**: Ready for Production Deployment

---

## 📊 Current Status

### Systems Overview

| System | Status | URL | Port |
|--------|--------|-----|------|
| **System 1** - Independent Accounting | ✅ Production | https://nerdx-accounting-system-production.up.railway.app | 8003 |
| **System 2** - Warm Lead Generation | ✅ Production | https://nerdx-apec-mvp-production.up.railway.app | 8004 |
| **System 3** - Project Sonar | 🔄 Local Ready | http://localhost:8005 | 8005 |

### Local Testing Results

**Project Sonar (System 3)** - All Tests Passed ✅

```
✓ Health check: OK
✓ Multi-Agent System: 4 agents operational
✓ NBRS 2.0 calculation: Working
✓ Workflow execution: Success (50 brands → 5 top picks)
✓ Collaboration briefs: 5 generated
✓ All API endpoints: Functional
```

**Logs Summary**:
- OrchestratorAgent: ✅ Active
- MarketIntelAgent: ✅ Active
- ResonanceModelingAgent: ✅ Active (50 brands analyzed)
- ContentStrategyAgent: ✅ Active (5 briefs generated)

---

## 🚀 Railway Deployment - Step by Step

### Step 1: Access Railway Dashboard

Open your browser and navigate to:
```
https://railway.app/dashboard
```

Login with your GitHub account.

### Step 2: Create New Project

1. Click **"New Project"** button (top right)
2. Select **"Deploy from GitHub repo"**
3. Choose repository: **`KFP-SEAN/nerdx-apec-mvp`**
4. Grant repository access if prompted

### Step 3: Configure Root Directory

**IMPORTANT**: Project Sonar is in a subdirectory

1. After project creation, go to **Settings** (left sidebar)
2. Click **"General"** tab
3. Find **"Root Directory"** field
4. Enter: `project-sonar`
5. Click **"Save"**

### Step 4: Set Environment Variables

Go to **Settings → Variables** and add the following:

#### Required Variables

```bash
# API Configuration
API_ENVIRONMENT=production
API_HOST=0.0.0.0
PORT=${{PORT}}

# NBRS Model
NBRS_MODEL_VERSION=2.0.0
NBRS_UPDATE_FREQUENCY=daily
```

#### API Keys (Required for Full Functionality)

```bash
# WIPO API (World Intellectual Property Organization)
WIPO_API_URL=https://www.wipo.int/branddb/en/
WIPO_API_KEY=your_actual_wipo_api_key

# KIS API (Korea Information Service - Enterprise Data)
KIS_API_URL=https://api.kis.co.kr
KIS_API_KEY=your_actual_kis_api_key
KIS_API_SECRET=your_actual_kis_api_secret

# Naver News API (Real-time News Data)
NEWS_API_URL=https://openapi.naver.com/v1/search/news.json
NEWS_API_CLIENT_ID=your_actual_naver_client_id
NEWS_API_CLIENT_SECRET=your_actual_naver_client_secret

# Anthropic Claude (AI Brief Generation)
ANTHROPIC_API_KEY=your_actual_anthropic_key
```

#### Optional Variables (Phase 2)

```bash
# OpenAI (Alternative AI Model)
OPENAI_API_KEY=your_openai_key

# Google Gemini (Alternative AI Model)
GEMINI_API_KEY=your_gemini_key

# Google Cloud (NotebookLM Integration)
GOOGLE_CREDENTIALS_PATH=/path/to/credentials.json
GOOGLE_PROJECT_ID=your_project_id
```

**Note**: MVP will run with mock data if API keys are not provided, but for production use, you need real API keys.

### Step 5: Deploy

1. Railway will automatically start deploying after you save environment variables
2. Monitor deployment in **"Deployments"** tab
3. Watch logs in real-time by clicking on the latest deployment

**Expected Deploy Time**: 3-5 minutes

### Step 6: Verify Deployment

Once deployment is complete:

1. Go to **Settings → Domains**
2. Copy the Railway-generated URL (e.g., `project-sonar-production.up.railway.app`)
3. Test the health endpoint:

```bash
curl https://your-project-name.up.railway.app/health
```

**Expected Response**:
```json
{
  "status": "healthy",
  "environment": "production",
  "agents": {
    "orchestrator": {...},
    "market_intel": {...},
    "resonance_modeling": {...},
    "content_strategy": {...}
  },
  "mas_operational": true
}
```

### Step 7: Test Key Endpoints

```bash
# 1. Test KPI Dashboard
curl https://your-app.up.railway.app/api/v1/dashboard/kpis

# 2. Test Agent Status
curl https://your-app.up.railway.app/api/v1/dashboard/agents-status

# 3. Test NBRS 2.0 Calculation
curl -X POST "https://your-app.up.railway.app/api/v1/resonance/calculate" \
  -H "Content-Type: application/json" \
  -d '{
    "anchor_brand": {
      "brand_name": "NERD",
      "company_name": "NERDX",
      "nice_classification": ["35", "41", "43"],
      "country": "KR"
    },
    "target_brand": {
      "brand_name": "TestBrand",
      "company_name": "Test Corp",
      "nice_classification": ["30", "43"],
      "country": "KR"
    }
  }'

# 4. Test Find Top Brands Workflow
curl -X POST "https://your-app.up.railway.app/api/v1/workflows/find-top-brands" \
  -H "Content-Type: application/json" \
  -d '{
    "anchor_brand": {
      "brand_name": "NERD",
      "company_name": "NERDX",
      "nice_classification": ["35", "41", "43"],
      "country": "KR"
    },
    "target_country": "KR"
  }'
```

---

## 📋 Post-Deployment Checklist

### Immediate (Within 1 Hour)

- [ ] Health check passes
- [ ] All 4 agents show as operational
- [ ] API documentation accessible at `/docs`
- [ ] At least 3 endpoint tests successful
- [ ] Logs show no critical errors
- [ ] Response time < 2 seconds (p95)

### Within 24 Hours

- [ ] Document production URL in README
- [ ] Update SYSTEM_INTEGRATION_GUIDE.md with production URL
- [ ] Test integration with System 1 & System 2
- [ ] Set up monitoring alerts
- [ ] Configure backup schedule

### Within 1 Week

- [ ] Obtain real API keys (WIPO, KIS, Naver)
- [ ] Test with real brand data
- [ ] Validate NBRS 2.0 calculations with real data
- [ ] Generate first AI collaboration briefs
- [ ] Stakeholder demo

---

## 🔧 Troubleshooting

### Issue 1: Deployment Fails

**Symptoms**: Build error or deployment stuck

**Solutions**:
1. Check `requirements.txt` is the Railway version (simplified)
2. Verify Root Directory is set to `project-sonar`
3. Check build logs for specific errors
4. Ensure Python version is 3.11+ (set in `runtime.txt` if needed)

### Issue 2: Health Check Fails

**Symptoms**: `/health` returns 500 or connection refused

**Solutions**:
1. Check environment variable `PORT` is set to `${{PORT}}`
2. Verify `API_HOST` is `0.0.0.0` not `localhost`
3. Check Railway logs for startup errors
4. Ensure all required dependencies are in `requirements.txt`

### Issue 3: Agents Not Operational

**Symptoms**: `mas_operational: false` in health check

**Solutions**:
1. Check agent initialization logs
2. Verify config.py has correct settings
3. Restart deployment from Railway dashboard
4. Check memory limits (may need to upgrade Railway plan)

### Issue 4: API Endpoints Return Errors

**Symptoms**: 404 or 500 errors on API calls

**Solutions**:
1. Verify URL includes `/api/v1/` prefix
2. Check request body matches expected schema
3. Review Railway logs for stack traces
4. Test endpoints locally first

---

## 📞 Support Contacts

### Railway Issues
- Documentation: https://docs.railway.app/
- Discord: https://discord.gg/railway
- Support: support@railway.app

### NERDX Support
- Product Owner: sean@koreafnbpartners.com
- GitHub Issues: https://github.com/KFP-SEAN/nerdx-apec-mvp/issues

---

## 📈 Success Metrics

### Technical Metrics

| Metric | Target | How to Check |
|--------|--------|--------------|
| Uptime | 99.9% | Railway dashboard → Metrics |
| Response Time (p95) | < 500ms | Test endpoints with curl + time |
| Error Rate | < 1% | Railway logs → Error count |
| Agent Availability | 100% | `/health` endpoint → agents |

### Business Metrics (Week 1)

| Metric | Target | Status |
|--------|--------|--------|
| Successful API Calls | 1,000+ | TBD |
| Brands Analyzed | 100+ | TBD |
| Collaboration Briefs Generated | 20+ | TBD |
| Top 10% Brands Identified | 10+ | TBD |

---

## 🎯 Next Steps After Deployment

### Phase 1: Validation (Week 1)
1. Deploy to Railway ✅
2. Verify all endpoints
3. Test with mock data
4. Demo to stakeholders

### Phase 2: Real Data Integration (Week 2-3)
1. Acquire API keys (WIPO, KIS, Naver)
2. Test with real brand data
3. Validate NBRS 2.0 accuracy
4. Fine-tune model weights

### Phase 3: System Integration (Week 4)
1. Connect System 2 → System 3 workflow
2. Test end-to-end: Lead discovery → Resonance analysis
3. Generate first real collaboration briefs
4. Iterate based on feedback

### Phase 4: Scale (Month 2)
1. Add Phase 2 features (Neo4j, Redis, MLflow)
2. Implement continual learning
3. Add multi-armed bandits optimization
4. Launch to customers

---

## 📚 Reference Documentation

**Deployment Guides**:
- [RAILWAY_SETUP_STEPS.md](./project-sonar/RAILWAY_SETUP_STEPS.md) - Detailed web UI guide
- [RAILWAY_DEPLOYMENT.md](./project-sonar/RAILWAY_DEPLOYMENT.md) - Technical deployment guide

**System Documentation**:
- [README.md](./README.md) - Project overview
- [EXECUTIVE_SUMMARY.md](./EXECUTIVE_SUMMARY.md) - Business summary
- [SYSTEM_INTEGRATION_GUIDE.md](./SYSTEM_INTEGRATION_GUIDE.md) - Integration guide
- [project-sonar/README.md](./project-sonar/README.md) - Project Sonar details

**API Documentation** (after deployment):
- Swagger UI: `https://your-app.up.railway.app/docs`
- ReDoc: `https://your-app.up.railway.app/redoc`

---

## ✅ Final Checklist

Before considering deployment complete:

- [ ] All 3 systems (1, 2, 3) are in production or ready
- [ ] Health checks passing on all systems
- [ ] Environment variables configured
- [ ] Production URLs documented
- [ ] Basic smoke tests passed
- [ ] Team notified of new deployment
- [ ] Monitoring set up
- [ ] Backup plan in place

---

**Deployment Prepared by**: Claude Code
**Date**: 2025-10-27
**Version**: 1.0.0-MVP
**Status**: Ready for Railway Deployment

🚀 **Let's deploy Project Sonar and complete the NERDX Resonance Economy Platform!**
