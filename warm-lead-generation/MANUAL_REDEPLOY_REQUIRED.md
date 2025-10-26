# ⚠️ Manual Railway Redeploy Required

**Date:** 2025-10-26
**Status:** Code fixed & committed ✅ | Railway redeploy needed ⏳

---

## 🎯 Issue

NBRS calculation logic has been **completely fixed** and all local tests pass, but Railway production is still running the **old buggy version**.

### Current Production Status
- ❌ NBRS Score: 15.17 (should be ~99 for premium leads)
- ❌ Tier: TIER4 (should be TIER1)
- ❌ Using old USD-based model with field mismatches

### Expected After Redeploy
- ✅ NBRS Score: 99.25 for premium leads
- ✅ Tier: TIER1 for premium leads
- ✅ Using new KRW-based model with correct calculations

---

## 🚀 How to Fix: Manual Redeploy via Railway Dashboard

### Step 1: Access Railway Dashboard

Open this URL in your browser:
```
https://railway.app/project/53c2f700-32ca-491f-b525-8552114b6fd6
```

### Step 2: Navigate to Service

1. Click on **"warm-lead-generation"** service (in the services list)

### Step 3: Trigger Redeploy

**Option A: Quick Redeploy**
1. Look for the **"Deployments"** tab at the top
2. Click on it
3. Find the latest deployment entry
4. Click the **"⋮"** (three dots menu) on the right
5. Select **"Redeploy"**
6. Confirm the redeploy

**Option B: New Deployment**
1. Click the **"Deploy"** button (usually at top right)
2. Wait for deployment to start

### Step 4: Monitor Deployment

1. Watch the deployment logs in the "Deployments" tab
2. Wait for status to change to **"SUCCESS"** (usually 1-2 minutes)
3. Look for message like: `Application startup complete`

### Step 5: Verify Fix

Run this test command:

```bash
curl -X POST "https://warm-lead-generation-production.up.railway.app/api/v1/lead-scoring/calculate" \
  -H "Content-Type: application/json" \
  -d '{
    "lead_id": "verification-after-redeploy",
    "company_name": "Premium Verification Corp",
    "brand_affinity": {
      "past_interaction_score": 95,
      "email_engagement_score": 98,
      "meeting_history_score": 92,
      "relationship_duration_score": 95,
      "contact_frequency_score": 94,
      "decision_maker_access_score": 98,
      "nps_score": 95,
      "testimonial_provided": true,
      "reference_willing": true
    },
    "market_positioning": {
      "annual_revenue_krw": 500000000000,
      "employee_count": 1000,
      "marketing_budget_krw": 5000000000,
      "target_industry_match": true,
      "target_geography_match": true,
      "pain_point_alignment_score": 95,
      "revenue_growth_yoy": 50,
      "expansion_plans_score": 95
    },
    "digital_presence": {
      "website_traffic_monthly": 500000,
      "social_media_followers": 100000,
      "content_engagement_score": 95,
      "modern_website": true,
      "marketing_automation": true,
      "mobile_app": true,
      "ecommerce_enabled": true
    },
    "update_salesforce": false
  }'
```

**Expected Response:**
```json
{
  "nbrs_score": 99.25,  // ← Should be ~99, NOT 15.17!
  "tier": "tier1",      // ← Should be tier1, NOT tier4!
  "brand_affinity_score": 100.0,
  "market_positioning_score": 98.75,
  "digital_presence_score": 98.75
}
```

---

## ✅ Verification Checklist

After redeployment, verify these:

- [ ] NBRS score for premium leads is 95-100 (not 15-20)
- [ ] Tier classification is TIER1 (not TIER4)
- [ ] Brand Affinity Score is ~100 (not ~20)
- [ ] Market Positioning Score is ~99 (not ~7)
- [ ] Digital Presence Score is ~99 (not ~17)

---

## 📊 What Was Fixed

### Before (Current Production - Buggy)
```
Premium Lead Input:
- Brand Affinity: All scores 95-98
- Market Positioning: Revenue 500B KRW, 1000 employees, Budget 5B KRW
- Digital Presence: Traffic 500K, Followers 100K, all features enabled

Output: ❌
- NBRS: 15.17
- Tier: TIER4
- Brand Affinity: 20.57
- Market Positioning: 7.5
- Digital Presence: 17.25
```

### After (Local Testing - Fixed)
```
Same Premium Lead Input

Output: ✅
- NBRS: 99.25
- Tier: TIER1
- Brand Affinity: 100.0
- Market Positioning: 98.75
- Digital Presence: 98.75
```

---

## 🔧 Technical Details

### Commits Applied
1. **f2cfc90** - Fix NBRS calculation logic for accurate lead scoring
2. **3627182** - Trigger Railway redeploy with fixed NBRS model
3. **a0394a1** - Trigger Railway redeploy for NBRS fix (empty commit)

### Files Changed
- `models/nbrs_models.py` - Complete rewrite with KRW support
- `test_fixed_nbrs.py` - Updated test data

### GitHub Repo Status
- ✅ All changes committed and pushed
- ✅ Repository: KFP-SEAN/nerdx-apec-mvp
- ✅ Branch: main
- ✅ Latest commit: a0394a1

---

## 🆘 Troubleshooting

### If Auto-Deploy Isn't Working

Railway may need GitHub webhook configuration:

1. Go to Railway Dashboard → warm-lead-generation service
2. Click **"Settings"** tab
3. Under **"Source"** section:
   - Verify repo: `KFP-SEAN/nerdx-apec-mvp`
   - Verify branch: `main`
   - Verify root directory: `warm-lead-generation`
4. Under **"Deploy"** section:
   - Enable **"Auto Deploy"** toggle
   - Check **"Deploy on Push"** is enabled
5. Save settings
6. Trigger manual redeploy

### If Deployment Fails

Check deployment logs for errors:
1. Go to Deployments tab
2. Click on the failed deployment
3. View logs
4. Common issues:
   - Missing dependencies: Check `requirements.txt`
   - Port binding: Check `main.py` uses `PORT` env var
   - Environment variables: Verify all 17 vars are set

---

## 📞 Support

**Railway Dashboard:**
https://railway.app/project/53c2f700-32ca-491f-b525-8552114b6fd6

**Service ID:**
31e0581c-9ec4-4805-a9e2-abf4c7ad907e

**Production URL:**
https://warm-lead-generation-production.up.railway.app

**GitHub Repo:**
https://github.com/KFP-SEAN/nerdx-apec-mvp

---

## ⏱️ Next Steps

1. **Manual redeploy on Railway** (2-3 minutes)
2. **Run verification test** (above)
3. **Confirm NBRS scores are correct**
4. **Test with real production data**
5. **Monitor tier distribution via `/api/v1/lead-scoring/stats`**

---

**Status:** Awaiting manual Railway redeploy
**Priority:** HIGH - Production using incorrect NBRS calculations
**Impact:** All leads incorrectly classified as TIER4
**ETA:** 3-5 minutes after manual redeploy
