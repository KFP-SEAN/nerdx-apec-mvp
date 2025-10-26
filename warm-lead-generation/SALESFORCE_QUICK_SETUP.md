# Salesforce Quick Setup Guide
# 5분 안에 NBRS 통합 설정하기

**Date:** 2025-10-26
**Time Required:** 5-10 minutes

---

## 📋 Quick Setup Checklist

- [ ] Step 1: Custom Fields 생성 (3분)
- [ ] Step 2: Platform Event 생성 (2분)
- [ ] Step 3: Flow 생성 (5분 - 선택사항)
- [ ] Step 4: API 테스트

---

## Step 1: Custom Fields 생성 (3분)

### Salesforce Setup 접속
1. Salesforce에 로그인
2. 우측 상단 ⚙️ (Setup) 클릭
3. Quick Find에 "Object Manager" 입력
4. **Lead** 객체 선택
5. 좌측 메뉴에서 **"Fields & Relationships"** 클릭

### 8개 Custom Fields 생성

**Field 1: NBRS Score**
- Click **"New"** 버튼
- Data Type: **Number**
- Field Label: `NBRS Score`
- Length: `5` | Decimal Places: `2`
- Field Name: `NBRS_Score` (자동생성)
- Description: `Overall NBRS score (0-100)`
- ✓ Required: NO
- ✓ Unique: NO
- Save

**Field 2: NBRS Tier**
- Data Type: **Picklist**
- Field Label: `NBRS Tier`
- Values (한 줄에 하나씩):
  ```
  TIER1
  TIER2
  TIER3
  TIER4
  ```
- Field Name: `NBRS_Tier`
- Description: `Lead tier classification (TIER1=Top, TIER4=Low)`
- Save

**Field 3: Brand Affinity Score**
- Data Type: **Number**
- Field Label: `Brand Affinity Score`
- Length: `5` | Decimal Places: `2`
- Field Name: `Brand_Affinity_Score`
- Description: `Brand affinity component (0-100)`
- Save

**Field 4: Market Positioning Score**
- Data Type: **Number**
- Field Label: `Market Positioning Score`
- Length: `5` | Decimal Places: `2`
- Field Name: `Market_Positioning_Score`
- Description: `Market positioning component (0-100)`
- Save

**Field 5: Digital Presence Score**
- Data Type: **Number**
- Field Label: `Digital Presence Score`
- Length: `5` | Decimal Places: `2`
- Field Name: `Digital_Presence_Score`
- Description: `Digital presence component (0-100)`
- Save

**Field 6: NBRS Calculated Date**
- Data Type: **Date/Time**
- Field Label: `NBRS Calculated Date`
- Field Name: `NBRS_Calculated_Date`
- Description: `When NBRS was last calculated`
- Save

**Field 7: Priority Rank**
- Data Type: **Number**
- Field Label: `Priority Rank`
- Length: `5` | Decimal Places: `0`
- Field Name: `Priority_Rank`
- Description: `Ranking among all leads (#1 = highest priority)`
- Save

**Field 8: Next Action**
- Data Type: **Text**
- Field Label: `Next Action`
- Length: `255`
- Field Name: `Next_Action`
- Description: `Recommended next action for this lead`
- Save

---

## Step 2: Platform Event 생성 (2분)

### Platform Event 생성
1. Setup → Quick Find: `Platform Events`
2. Click **"New Platform Event"**

**Event Details:**
- Label: `NBRS Calculation`
- Plural Label: `NBRS Calculations`
- Object Name: `NBRS_Calculation` (자동으로 `__e` 추가됨)
- Description: `Triggered when NBRS is calculated for a lead`
- Save

### Event Fields 생성

**Field 1: Lead ID**
- Data Type: **Text**
- Field Label: `Lead ID`
- Length: `18`
- Field Name: `Lead_ID`
- Required: Yes
- Save

**Field 2: Company Name**
- Data Type: **Text**
- Field Label: `Company Name`
- Length: `255`
- Field Name: `Company_Name`
- Save

**Field 3-7: NBRS Scores** (각각 동일한 방식으로 생성)
- `NBRS_Score__c` - Number(5,2)
- `NBRS_Tier__c` - Text(10)
- `Brand_Affinity_Score__c` - Number(5,2)
- `Market_Positioning_Score__c` - Number(5,2)
- `Digital_Presence_Score__c` - Number(5,2)

**Field 8: Priority Rank**
- Data Type: **Number**
- Length: `5` | Decimal Places: `0`
- Field Name: `Priority_Rank`

**Field 9: Calculated At**
- Data Type: **Date/Time**
- Field Name: `Calculated_At`

---

## Step 3: Auto-Assignment Flow 생성 (선택사항)

### Flow 생성
1. Setup → Quick Find: `Flows`
2. Click **"New Flow"**
3. Flow Type: **Record-Triggered Flow**

**Trigger Configuration:**
- Object: `NBRS Calculation Event` (`NBRS_Calculation__e`)
- Trigger: **A record is created**
- Entry Conditions: None (process all events)

### Flow Logic

**Decision 1: Check Tier**
- Outcome 1: TIER1
  - Condition: `{!$Record.NBRS_Tier__c}` Equals `TIER1`
  - Action:
    - **Update Lead Record:**
      - Lead ID: `{!$Record.Lead_ID__c}`
      - Status: `Hot Lead`
      - Owner: `Senior Sales Rep` (assign to queue/user)
    - **Create Task:**
      - Subject: `Immediate outreach - TIER1 Lead`
      - Priority: `High`
      - Due Date: `Today`
      - Assigned To: Lead Owner
    - **Send Email:**
      - To: Sales Manager
      - Template: `TIER1 Alert Email`

- Outcome 2: TIER2
  - Condition: `{!$Record.NBRS_Tier__c}` Equals `TIER2`
  - Action:
    - Update Lead Status: `Warm Lead`
    - Create Task: `Schedule discovery call`
    - Add to nurturing campaign

- Outcome 3: TIER3
  - Condition: `{!$Record.NBRS_Tier__c}` Equals `TIER3`
  - Action:
    - Add to automated nurturing sequence
    - Create task for follow-up in 30 days

- Outcome 4: TIER4
  - Condition: `{!$Record.NBRS_Tier__c}` Equals `TIER4`
  - Action:
    - Add to low-priority lead pool
    - Enroll in long-term nurturing campaign

**Activate Flow** when done

---

## Step 4: API 테스트

### Test NBRS API with Salesforce Update

```bash
curl -X POST "https://warm-lead-generation-production.up.railway.app/api/v1/lead-scoring/calculate" \
  -H "Content-Type: application/json" \
  -d '{
    "lead_id": "YOUR_SALESFORCE_LEAD_ID",
    "company_name": "Test Company",
    "brand_affinity": {
      "past_interaction_score": 85,
      "email_engagement_score": 90,
      "meeting_history_score": 80,
      "relationship_duration_score": 85,
      "contact_frequency_score": 85,
      "decision_maker_access_score": 90,
      "nps_score": 85,
      "testimonial_provided": true,
      "reference_willing": true
    },
    "market_positioning": {
      "annual_revenue_krw": 300000000000,
      "employee_count": 500,
      "marketing_budget_krw": 3000000000,
      "target_industry_match": true,
      "target_geography_match": true,
      "pain_point_alignment_score": 85,
      "revenue_growth_yoy": 30,
      "expansion_plans_score": 80
    },
    "digital_presence": {
      "website_traffic_monthly": 200000,
      "social_media_followers": 50000,
      "content_engagement_score": 85,
      "modern_website": true,
      "marketing_automation": true,
      "mobile_app": true,
      "ecommerce_enabled": true
    },
    "update_salesforce": true
  }'
```

### Verify in Salesforce

1. Go to the Lead record
2. Check that NBRS fields are populated:
   - NBRS Score: ~90
   - NBRS Tier: TIER1
   - Brand Affinity Score: ~90
   - Market Positioning Score: ~85
   - Digital Presence Score: ~95
   - NBRS Calculated Date: (current timestamp)

3. Check if Flow triggered:
   - Lead Status updated
   - Task created
   - Email sent (if configured)

---

## 🎯 Quick Verification Checklist

After setup, verify:

- [ ] All 8 custom fields visible on Lead page layout
- [ ] Platform Event `NBRS_Calculation__e` exists
- [ ] Flow activated and working
- [ ] API test successfully updates Lead
- [ ] Platform Event published
- [ ] Flow triggers and performs actions

---

## 📞 Troubleshooting

### Custom Fields Not Visible
- Add fields to Lead Page Layout:
  - Setup → Object Manager → Lead → Page Layouts
  - Edit layout → Add NBRS fields section

### Platform Event Not Found
- Check API name ends with `__e`
- Verify user has permission to publish Platform Events

### Flow Not Triggering
- Verify Flow is **Activated**
- Check Debug Logs:
  - Setup → Debug Logs
  - Set trace flag for your user
  - Trigger event and check logs

### API Update Failing
- Check Salesforce credentials in Railway Variables
- Verify user has Edit permission on Lead object
- Check API logs for detailed error messages

---

## 🚀 Next Steps After Setup

1. **Test with Real Leads:**
   - Select 5-10 test leads
   - Calculate NBRS scores
   - Verify automation works

2. **Create Dashboard:**
   - Setup → Dashboards → New Dashboard
   - Add NBRS components:
     - Top 10 Leads by NBRS
     - Tier Distribution Chart
     - NBRS Trend Over Time

3. **Train Sales Team:**
   - Explain NBRS scoring
   - Show how to use tier classification
   - Review recommended actions per tier

4. **Monitor and Optimize:**
   - Track conversion rates by tier
   - Adjust tier thresholds if needed
   - Refine automation rules

---

## ✅ Success Criteria

Setup is successful when:

- ✅ Lead records show NBRS scores
- ✅ Leads are automatically classified into tiers
- ✅ High-value leads (TIER1) trigger immediate alerts
- ✅ Sales team receives automatic task assignments
- ✅ NBRS data visible in dashboards and reports

---

**Setup Time:** ~10 minutes
**Maintenance:** Minimal (review tier distribution monthly)
**ROI:** High (better lead prioritization → higher conversion rates)

For detailed documentation, see `SALESFORCE_SETUP.md`
