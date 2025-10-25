# NERDX Warm Lead Generation System
# NERD12 웜리드 발굴 시스템

NBRS (NERD Brand Resonance Score) 기반 웜리드 자동 발굴 및 스코어링 시스템

## Overview

The NERDX Warm Lead Generation System identifies and scores warm leads using the proprietary NBRS (NERD Brand Resonance Score) algorithm. The system integrates with Salesforce for lead management and uses Helios for data enrichment.

**Goal:** Increase MRR from current levels to 500M KRW by identifying the top 10% highest-value warm leads.

## Features

- **NBRS Calculation Engine**: 3-pillar scoring system
  - Brand Affinity (40%): Past interactions and relationship strength
  - Market Positioning (35%): Company size, budget, strategic alignment
  - Digital Presence (25%): Online engagement and digital maturity

- **Salesforce Integration**:
  - Auto-fetch leads from Salesforce
  - Update NBRS scores on Lead records
  - Publish Platform Events for automation
  - Trigger assignment rules based on tier

- **Helios Integration**:
  - Enrich lead data with company intelligence
  - Gather firmographic and technographic data
  - Social media presence analysis

- **Tier-Based Classification**:
  - TIER1 (80-100): Top priority - immediate sales engagement
  - TIER2 (60-79): High priority - strategic outreach
  - TIER3 (40-59): Medium priority - nurturing campaigns
  - TIER4 (0-39): Low priority - long-term nurturing

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

## Installation

### Prerequisites

- Python 3.9+
- Salesforce account with API access
- Helios API instance
- Valid Salesforce custom fields (see SALESFORCE_SETUP.md)

### Setup

1. **Clone the repository:**
```bash
cd nerdx-apec-mvp/warm-lead-generation
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure environment variables:**
```bash
cp .env.example .env
# Edit .env with your credentials
```

4. **Set up Salesforce** (see SALESFORCE_SETUP.md):
   - Create custom fields on Lead object
   - Create NBRS_Calculation__e Platform Event
   - Configure auto-assignment Flow
   - Set up Connected App

## Usage

### Start the API Server

```bash
python main.py
```

The server will start on `http://localhost:8004`

### API Endpoints

#### Health Check
```bash
GET /health
```

#### Calculate NBRS for a Lead
```bash
POST /api/v1/lead-scoring/calculate
Content-Type: application/json

{
  "lead_id": "00Q...",
  "company_name": "Example Corp",
  "brand_affinity": {...},
  "market_positioning": {...},
  "digital_presence": {...},
  "update_salesforce": true
}
```

#### Enrich and Score a Lead
```bash
POST /api/v1/lead-scoring/enrich-and-score
Content-Type: application/json

{
  "lead_id": "00Q...",
  "company_name": "Example Corp",
  "company_domain": "example.com"
}
```

This endpoint:
1. Enriches lead data via Helios
2. Fetches Salesforce activity history
3. Calculates NBRS score
4. Updates Salesforce
5. Publishes Platform Event

#### Get Top 10 Leads
```bash
GET /api/v1/lead-scoring/top-leads?n=10
```

#### Get Leads by Tier
```bash
GET /api/v1/lead-scoring/by-tier/tier1
```

#### Get Pipeline Value
```bash
GET /api/v1/lead-scoring/pipeline-value
```

Returns pipeline value breakdown by tier with expected revenue.

#### Get Scoring Statistics
```bash
GET /api/v1/lead-scoring/stats
```

## NBRS Scoring Model

### Brand Affinity (40%)

- **Past Interaction (15%)**:
  - Salesforce activity score (5%)
  - Email engagement score (5%)
  - Meeting history score (5%)

- **Relationship Depth (15%)**:
  - Relationship duration (5%)
  - Contact frequency (5%)
  - Decision maker access (5%)

- **Brand Perception (10%)**:
  - NPS score (5%)
  - Testimonial provided (2.5%)
  - Reference willing (2.5%)

### Market Positioning (35%)

- **Company Size & Budget (20%)**:
  - Annual revenue (10%)
  - Employee count (5%)
  - Marketing budget (5%)

- **Strategic Alignment (10%)**:
  - Target industry match (4%)
  - Target geography match (3%)
  - Pain point alignment (3%)

- **Growth Potential (5%)**:
  - Revenue growth YoY (2.5%)
  - Expansion plans (2.5%)

### Digital Presence (25%)

- **Online Engagement (15%)**:
  - Website traffic (5%)
  - Social media followers (5%)
  - Content engagement (5%)

- **Digital Maturity (10%)**:
  - Modern website (2.5%)
  - Marketing automation (2.5%)
  - Mobile app (2.5%)
  - E-commerce enabled (2.5%)

## Configuration

### NBRS Weights (config.py)

```python
nbrs_weight_brand_affinity = 0.40  # 40%
nbrs_weight_market_positioning = 0.35  # 35%
nbrs_weight_digital_presence = 0.25  # 25%
```

### Tier Thresholds

```python
nbrs_threshold_tier1 = 80.0  # TIER1: 80-100
nbrs_threshold_tier2 = 60.0  # TIER2: 60-79
nbrs_threshold_tier3 = 40.0  # TIER3: 40-59
```

## Salesforce Setup

See [SALESFORCE_SETUP.md](./SALESFORCE_SETUP.md) for detailed instructions on:
- Custom field creation
- Platform Event configuration
- Auto-assignment Flow setup
- Dashboard and reports

## Project Structure

```
warm-lead-generation/
├── config.py                  # Configuration settings
├── main.py                    # FastAPI application
├── requirements.txt           # Python dependencies
├── models/
│   └── nbrs_models.py        # Pydantic models for NBRS
├── services/
│   └── nbrs_engine.py        # NBRS calculation logic
├── integrations/
│   ├── salesforce_client.py  # Salesforce API client
│   └── helios_client.py      # Helios API client
└── routers/
    └── lead_scoring.py       # API endpoints
```

## Deployment

### Local Development
```bash
python main.py
```

### Production (Railway/Heroku)
```bash
# Set environment variables in platform
# Deploy via git push or CLI
```

## Monitoring

Key metrics to monitor:
- Total leads scored
- Average NBRS score
- Tier distribution
- Pipeline value by tier
- Expected revenue
- Top 10 leads

Access statistics via:
```bash
GET /api/v1/lead-scoring/stats
```

## Troubleshooting

### Salesforce Connection Issues
- Verify credentials in .env
- Check security token
- Ensure Connected App is configured
- Verify API access permissions

### Helios Integration Issues
- Check Helios API URL
- Verify API key
- Check network connectivity
- Review Helios logs

### NBRS Calculation Issues
- Verify all component scores are within 0-100
- Check for null/missing data
- Review scoring weights in config.py

## Contributing

For internal NERDX team members:
1. Create feature branch
2. Implement changes
3. Test thoroughly
4. Submit pull request

## License

Proprietary - NERDX Internal Use Only

## Support

For questions or issues:
- Slack: #nerdx-warm-leads
- Email: sean@koreafnbpartners.com
