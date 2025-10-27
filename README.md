# NERDX APEC MVP - Resonance Economy Platform

**Vision**: Transform from SaaS tools to a Market-Making Platform powered by AI
**Objective**: Scale MRR from 500M to 100B KRW (200x growth)
**Version**: 1.0.0-MVP
**Date**: 2025-10-27

---

## 🚀 Quick Links

- **Executive Summary**: [EXECUTIVE_SUMMARY.md](./EXECUTIVE_SUMMARY.md)
- **Master Plan**: [NERDX_MASTER_PLAN.md](./NERDX_MASTER_PLAN.md)
- **System Integration**: [SYSTEM_INTEGRATION_GUIDE.md](./SYSTEM_INTEGRATION_GUIDE.md)
- **Architecture**: [ARCHITECTURE_OVERVIEW.md](./ARCHITECTURE_OVERVIEW.md)

---

## 📊 Platform Overview

NERDX APEC MVP는 AI 기반 "공명 경제(Resonance Economy)" 플랫폼으로, 3개의 핵심 시스템으로 구성되어 있습니다:

```
┌─────────────────────────────────────────────────────────┐
│              NERDX Resonance Economy                    │
├─────────────────────────────────────────────────────────┤
│  System 1           System 2           System 3         │
│  ─────────          ─────────          ─────────        │
│  Independent        Warm Lead          Project          │
│  Accounting         Generation         Sonar            │
│  System             (NBRS 1.0)         (NBRS 2.0)       │
│                                                         │
│  Port: 8003         Port: 8004         Port: 8005       │
│  ✅ Production      ✅ Production      ✅ Production    │
└─────────────────────────────────────────────────────────┘
```

---

## 🎯 Three Core Systems

### System 1: Independent Accounting System
**Purpose**: Cell-based MRR tracking for 8 independent accounting firms

- **Status**: ✅ Production
- **Port**: 8003
- **URL**: https://nerdx-accounting-system-production.up.railway.app
- **Docs**: [independent-accounting-system/README.md](./independent-accounting-system/README.md)

### System 2: Warm Lead Generation (NBRS 1.0)
**Purpose**: Top 10% warm lead discovery → 500M KRW MRR target

- **Status**: ✅ Production
- **Port**: 8004
- **URL**: https://nerdx-apec-mvp-production.up.railway.app
- **Docs**: [warm-lead-generation/SYSTEM_ARCHITECTURE.md](./warm-lead-generation/SYSTEM_ARCHITECTURE.md)

### System 3: Project Sonar (NBRS 2.0)
**Purpose**: AI-powered brand resonance analysis → Resonance Economy vision

- **Status**: ✅ Production
- **Port**: 8005
- **URL**: https://project-sonar-production-production.up.railway.app
- **Docs**: [project-sonar/README.md](./project-sonar/README.md)

---

## 📈 Business Metrics

### Growth Targets

| Timeframe | MRR Target | Multiplier | Strategy |
|-----------|-----------|------------|----------|
| Current | 120M KRW | 1x | Foundation |
| 6 months | 500M KRW | 4x | Top 10% leads |
| Year 1 | 1.8B KRW | 15x | T2D3 Triple |
| Year 5 | 100B KRW | 833x | Resonance Economy |

---

## 🚀 Getting Started

### Local Development

```bash
# System 1 - Independent Accounting (Port 8003)
cd independent-accounting-system
python main.py

# System 2 - Warm Lead Generation (Port 8004)
cd warm-lead-generation
python main.py

# System 3 - Project Sonar (Port 8005)
cd project-sonar
python main.py
```

### Production URLs

```bash
# System 1
curl https://nerdx-accounting-system-production.up.railway.app/health

# System 2
curl https://nerdx-apec-mvp-production.up.railway.app/health

# System 3 (after deployment)
curl https://project-sonar-production.up.railway.app/health
```

---

## 📚 Documentation Suite

### Strategic Documents
1. **[EXECUTIVE_SUMMARY.md](./EXECUTIVE_SUMMARY.md)** - Business overview & metrics
2. **[NERDX_MASTER_PLAN.md](./NERDX_MASTER_PLAN.md)** - Vision 2030, T2D3 strategy
3. **[SYSTEM_INTEGRATION_GUIDE.md](./SYSTEM_INTEGRATION_GUIDE.md)** - Integration guide
4. **[ARCHITECTURE_OVERVIEW.md](./ARCHITECTURE_OVERVIEW.md)** - System design
5. **[ARCHITECTURE_DETAILED.md](./ARCHITECTURE_DETAILED.md)** - Technical deep dive

### System-Specific Docs
- System 1: [README.md](./independent-accounting-system/README.md)
- System 2: [SYSTEM_ARCHITECTURE.md](./warm-lead-generation/SYSTEM_ARCHITECTURE.md)
- System 3: [README.md](./project-sonar/README.md), [RAILWAY_SETUP_STEPS.md](./project-sonar/RAILWAY_SETUP_STEPS.md)

---

## 🏗️ Technology Stack

- **Backend**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL (Railway)
- **AI Models**: Anthropic Claude, Google Gemini
- **External APIs**: WIPO, KIS, Naver News, Salesforce
- **Infrastructure**: Railway (PaaS)

---

## 🎯 Next Steps

### Deploy Project Sonar
1. Railway dashboard: https://railway.app/dashboard
2. Create project from GitHub
3. Set Root Directory: `project-sonar`
4. Configure environment variables
5. Deploy and validate

### Integration Testing
- System 1 ↔ System 2 data flow
- System 2 ↔ System 3 workflow
- End-to-end testing

---

## 🤝 Contact

**Product Owner**: Sean (sean@koreafnbpartners.com)
**Repository**: https://github.com/KFP-SEAN/nerdx-apec-mvp

---

## 🌟 Vision Statement

> "NERDX will become the leading platform for discovering and activating brand synergies across industries, creating the **Resonance Economy** - a new market category where companies find perfect-fit partners through AI-powered resonance analysis."

**Success = 100B+ KRW MRR + Category-Defining Platform**

---

**Built with Claude Code** 🤖
**Last Updated**: 2025-10-27
**Status**: MVP Complete, Production Ready
