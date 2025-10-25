# Salesforce Setup Guide
# NERDX Warm Lead Generation System - Salesforce 설정 가이드

This document describes the Salesforce custom fields and Platform Events required for the NERD12 Warm Lead Generation System.

## Custom Fields for Lead Object

Add the following custom fields to the Salesforce Lead object:

### NBRS Score Fields

| Field Name | API Name | Type | Description |
|------------|----------|------|-------------|
| NBRS Score | `NBRS_Score__c` | Number(5,2) | Overall NBRS score (0-100) |
| NBRS Tier | `NBRS_Tier__c` | Picklist | Lead tier classification |
| Brand Affinity Score | `Brand_Affinity_Score__c` | Number(5,2) | Brand affinity component (0-100) |
| Market Positioning Score | `Market_Positioning_Score__c` | Number(5,2) | Market positioning component (0-100) |
| Digital Presence Score | `Digital_Presence_Score__c` | Number(5,2) | Digital presence component (0-100) |
| NBRS Calculated Date | `NBRS_Calculated_Date__c` | DateTime | When NBRS was last calculated |
| Priority Rank | `Priority_Rank__c` | Number(5,0) | Ranking among all leads |
| Next Action | `Next_Action__c` | Text(255) | Recommended next action |

### NBRS Tier Picklist Values

Create a picklist field `NBRS_Tier__c` with the following values:

- `TIER1` - Top Priority (NBRS 80-100)
- `TIER2` - High Priority (NBRS 60-79)
- `TIER3` - Medium Priority (NBRS 40-59)
- `TIER4` - Low Priority (NBRS 0-39)

## Platform Events

### NBRS Calculation Event

Create a Platform Event named `NBRS_Calculation__e` with the following fields:

| Field Name | API Name | Type | Description |
|------------|----------|------|-------------|
| Lead ID | `Lead_ID__c` | Text(18) | Salesforce Lead ID |
| Company Name | `Company_Name__c` | Text(255) | Company name |
| NBRS Score | `NBRS_Score__c` | Number(5,2) | Calculated NBRS score |
| NBRS Tier | `NBRS_Tier__c` | Text(10) | Tier classification |
| Brand Affinity Score | `Brand_Affinity_Score__c` | Number(5,2) | Brand affinity score |
| Market Positioning Score | `Market_Positioning_Score__c` | Number(5,2) | Market positioning score |
| Digital Presence Score | `Digital_Presence_Score__c` | Number(5,2) | Digital presence score |
| Priority Rank | `Priority_Rank__c` | Number(5,0) | Priority ranking |
| Calculated At | `Calculated_At__c` | DateTime | Calculation timestamp |

## Process Builder / Flow Setup

### Auto-Assignment Flow

Create a Record-Triggered Flow that listens to `NBRS_Calculation__e` Platform Event:

**Trigger:**
- Object: `NBRS_Calculation__e`
- Trigger: After the record is created

**Actions:**

1. **For TIER1 Leads (NBRS >= 80):**
   - Assign to senior sales representative
   - Create high-priority task: "Immediate outreach required"
   - Send email notification to sales manager
   - Update Lead Status to "Hot Lead"

2. **For TIER2 Leads (NBRS 60-79):**
   - Assign to sales representative
   - Create task: "Schedule discovery call"
   - Add to nurturing campaign

3. **For TIER3 Leads (NBRS 40-59):**
   - Add to automated nurturing sequence
   - Create task for follow-up in 30 days

4. **For TIER4 Leads (NBRS < 40):**
   - Add to low-priority lead pool
   - Enroll in long-term nurturing campaign

## Email Templates

Create the following email templates for automated notifications:

### Template 1: TIER1 Alert
**Subject:** High-Value Lead Identified - {!Lead.Company} (NBRS: {!Lead.NBRS_Score__c})

**Body:**
```
A high-value warm lead has been identified:

Company: {!Lead.Company}
NBRS Score: {!Lead.NBRS_Score__c} (TIER1)
Priority Rank: #{!Lead.Priority_Rank__c}

Next Action: {!Lead.Next_Action__c}

This lead requires immediate attention from the sales team.

View Lead: {!Lead.Link}
```

## Reports and Dashboards

### NBRS Dashboard Components

Create the following reports for your NBRS dashboard:

1. **Top 10 Leads by NBRS Score**
   - Type: List View
   - Filter: All Leads
   - Sort: NBRS Score (Descending)
   - Limit: 10

2. **Leads by Tier Distribution**
   - Type: Pie Chart
   - Group by: NBRS Tier
   - Shows distribution across TIER1-4

3. **NBRS Trend Over Time**
   - Type: Line Chart
   - X-axis: NBRS Calculated Date
   - Y-axis: Average NBRS Score
   - Group by: Week

4. **Pipeline Value by Tier**
   - Type: Horizontal Bar Chart
   - Shows expected revenue by tier

## API Integration Setup

### Connected App

1. Go to Setup > Apps > App Manager > New Connected App
2. Configure:
   - Name: NERDX Warm Lead Generation
   - API Name: NERDX_Warm_Lead_Generation
   - Contact Email: [your-email]
   - Enable OAuth Settings: ✓
   - Callback URL: [your-callback-url]
   - Selected OAuth Scopes:
     - Full access (full)
     - Perform requests on your behalf at any time (refresh_token, offline_access)

3. Save and note the Consumer Key and Consumer Secret

### User Permissions

Grant the following permissions to the integration user:

- Read, Create, Edit on Lead object
- Read on Task, Event, EmailMessage objects
- Create on Platform Event objects
- API Enabled

## Testing Checklist

- [ ] All custom fields created on Lead object
- [ ] NBRS_Tier__c picklist values configured
- [ ] Platform Event NBRS_Calculation__e created
- [ ] Flow/Process Builder for auto-assignment configured
- [ ] Email templates created
- [ ] Dashboard and reports set up
- [ ] Connected App configured
- [ ] Integration user permissions granted
- [ ] Test API connection successful
- [ ] Test Platform Event publishing successful

## Support

For questions about Salesforce setup, contact your Salesforce administrator or refer to:
- [Salesforce Custom Fields Documentation](https://help.salesforce.com/s/articleView?id=sf.customize_fields.htm)
- [Platform Events Developer Guide](https://developer.salesforce.com/docs/atlas.en-us.platform_events.meta/platform_events/)
