# NBRS Algorithm Analysis and Fix

**Date:** 2025-10-26
**Status:** ⚠️ Critical Issue Identified
**Impact:** All leads scoring TIER4 due to field name mismatch

---

## 🔍 Problem Identified

### Issue Summary
All test leads are being classified as TIER4 (low priority) even when provided with high-quality data.

### Test Results
```
Premium Corp (High-value data):
- Expected: TIER1 (NBRS ≥ 80)
- Actual: TIER4 (NBRS = 15.17)

Test Production Corp (Medium-value data):
- Expected: TIER2 or TIER3
- Actual: TIER4 (NBRS = 12.91)

Startup Inc (Low-value data):
- Expected: TIER4
- Actual: TIER4 (NBRS = 2.05) ✓ Correct
```

---

## 🐛 Root Cause Analysis

### 1. Field Name Mismatch

**Model Definition** (`models/nbrs_models.py`):
```python
class MarketPositioningScore(BaseModel):
    annual_revenue_usd: Optional[int]  # Expects USD
    marketing_budget_usd: Optional[int]  # Expects USD
```

**API Request** (test data):
```json
{
  "market_positioning": {
    "annual_revenue_krw": 100000000000,  # Sending KRW!
    "marketing_budget_krw": 1000000000   # Sending KRW!
  }
}
```

**Result:** Fields don't match → Values default to `None` → Score calculated as 0

### 2. Impact on Scoring

**Market Positioning** (35% weight):
- Company Size & Budget (20%) → **0 points** (fields not matching)
- Strategic Alignment (10%) → Partial points
- Growth Potential (5%) → Partial points
- **Total: ~3-7 points instead of potential 20-35 points**

**Overall NBRS Impact:**
- Brand Affinity: ~20 points (working correctly)
- Market Positioning: ~5 points (should be 20-30)
- Digital Presence: ~15 points (working correctly)
- **Total: ~40 points instead of potential 80+**

---

## 🔧 Solution Options

### Option 1: Update Model to Accept KRW (Recommended)

**Pros:**
- Matches Korean market context
- Aligns with PRD (500M KRW MRR goal)
- More intuitive for Korean users

**Cons:**
- Requires code changes
- Need to update scaling factors

**Changes Required:**
```python
# models/nbrs_models.py

class BrandAffinityScore(BaseModel):
    # Update field names
    past_interaction_score: float  # Rename from salesforce_activity_score
    email_engagement_score: float
    meeting_history_score: float
    relationship_duration_score: float  # Add missing field
    contact_frequency_score: float
    decision_maker_access_score: float  # Add missing field
    nps_score: float
    testimonial_provided: bool
    reference_willing: bool

class MarketPositioningScore(BaseModel):
    # Change USD to KRW
    annual_revenue_krw: Optional[int]  # Changed from USD
    employee_count: Optional[int]
    marketing_budget_krw: Optional[int]  # Changed from USD
    target_industry_match: bool
    target_geography_match: bool
    pain_point_alignment_score: float  # Add missing _score suffix
    revenue_growth_yoy: float  # Rename from revenue_growth_yoy_percent
    expansion_plans_score: float  # Add missing field

    def calculate_total(self) -> float:
        # Update scaling factors for KRW
        revenue_score = min((self.annual_revenue_krw or 0) / 100_000_000_000 * 100, 100)  # 1000억 = 100점
        budget_score = min((self.marketing_budget_krw or 0) / 10_000_000_000 * 100, 100)  # 100억 = 100점
        # ... rest of calculation
```

### Option 2: Add Currency Conversion Layer

**Pros:**
- Supports both KRW and USD
- More flexible for international use

**Cons:**
- More complex
- Exchange rate handling required

### Option 3: Update API Request Format

**Pros:**
- No code changes needed
- Quick fix

**Cons:**
- Doesn't match Korean market
- Confusing for users (USD vs KRW)

---

## 📊 Expected Scores After Fix

### High-Value Lead (Premium Corp)
```
Input:
- Brand Affinity: All scores 90-98
- Market Positioning: Revenue 500B KRW, 1000 employees, Budget 5B KRW
- Digital Presence: Traffic 500K, Followers 100K, all features enabled

Expected NBRS:
- Brand Affinity: ~38 points (40% weight)
- Market Positioning: ~32 points (35% weight)
- Digital Presence: ~23 points (25% weight)
- Total: ~93 points → TIER1 ✓
```

### Medium-Value Lead (Test Production Corp)
```
Input:
- Brand Affinity: Scores 75-90
- Market Positioning: Revenue 100B KRW, 500 employees, Budget 1B KRW
- Digital Presence: Traffic 100K, Followers 25K

Expected NBRS:
- Brand Affinity: ~32 points
- Market Positioning: ~24 points
- Digital Presence: ~18 points
- Total: ~74 points → TIER2 ✓
```

### Low-Value Lead (Startup Inc)
```
Input:
- Brand Affinity: Scores 5-20
- Market Positioning: Revenue 100M KRW, 5 employees, Budget 1M KRW
- Digital Presence: Traffic 100, Followers 50

Expected NBRS:
- Brand Affinity: ~6 points
- Market Positioning: ~2 points
- Digital Presence: ~1 point
- Total: ~9 points → TIER4 ✓ (Already working correctly)
```

---

## 🎯 Recommended Fix

### Step 1: Update Models

Update `models/nbrs_models.py` to:
1. Change `*_usd` fields to `*_krw`
2. Adjust scaling factors for KRW amounts
3. Fix field name mismatches between model and API

### Step 2: Update Tests

Update all test data to ensure field names match:
- `past_interaction_score` → directly provided
- `relationship_duration_months` → calculate from `relationship_duration_score`
- `annual_revenue_krw` → already using this
- `marketing_budget_krw` → already using this

### Step 3: Verify Calculations

Test with known inputs:
```python
# TIER1 Test
Input: Top scores across all pillars
Expected Output: NBRS ≥ 80

# TIER2 Test
Input: Good scores with some weaknesses
Expected Output: 60 ≤ NBRS < 80

# TIER3 Test
Input: Average scores
Expected Output: 40 ≤ NBRS < 60

# TIER4 Test
Input: Low scores
Expected Output: NBRS < 40
```

---

## 📝 Implementation Plan

### Phase 1: Model Updates
1. Update `BrandAffinityScore` field names
2. Update `MarketPositioningScore` to use KRW
3. Update `DigitalPresenceScore` field names
4. Adjust calculation logic and scaling factors

### Phase 2: API Updates
5. Update API request validation
6. Update API documentation
7. Update example requests

### Phase 3: Testing
8. Create comprehensive test suite
9. Test all tier boundaries
10. Verify with realistic Korean market data

### Phase 4: Documentation
11. Update SALESFORCE_SETUP.md
12. Update API documentation
13. Update README with correct field names

---

## 🚨 Priority

**Priority:** HIGH
**Reason:** Core functionality not working as designed
**Impact:** Cannot identify top 10% warm leads (NERD12 goal)
**Timeline:** Should be fixed before production use

---

## 📞 Next Steps

1. **Review and approve** this analysis
2. **Implement Option 1** (Update model to accept KRW)
3. **Test with Korean market data**
4. **Redeploy to Railway**
5. **Verify tier distribution** matches expected 10% / 30% / 40% / 20%

---

**Status:** Awaiting approval to proceed with fixes
**Estimated Fix Time:** 30-60 minutes
**Testing Time:** 15-30 minutes
**Total:** ~1.5 hours to full resolution
