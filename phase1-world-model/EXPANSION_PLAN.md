# NERDX WORLD MODEL - Phase 2 Expansion Plan

**Based on PRD**: [KFP] NERDX WORLD MODEL 구축 협업 방안

## Executive Summary

This document outlines the expansion of the existing phase1-world-model system to implement the complete WORLD MODEL as specified in the PRD. The expansion transforms our basic recommendation system into a comprehensive AI-native platform with three core components: Analytical Core, Generative Partner, and Personalization Engine.

## Current State (Phase 1)

### Architecture
- **Backend**: FastAPI with Neo4j graph database
- **AI**: Single OpenAI GPT-4 agent (Maeju)
- **Data**: Product catalog, ingredients, lore, user interactions
- **Features**: Basic recommendations, storytelling, user preferences

### Limitations
- Single AI model (no orchestration)
- No Shopify integration
- No content generation tools
- Basic collaborative filtering only
- No external data sources

## Target State (Phase 2 - WORLD MODEL)

### 1. AI Orchestration Layer (Polyglot AI)

**Philosophy**: Use the best AI for each task
- **Claude Code**: Core architecture, API design, security, database operations
- **Gemini**: Prototyping, data analysis, creative content generation
- **Vercel AI SDK**: Unified orchestration layer

**Implementation**:
```
agents/
├── orchestrator.py          # Vercel AI SDK integration
├── claude_agent.py          # Claude for structured tasks
├── gemini_agent.py          # Gemini for creative tasks
└── maeju_agent.py          # Enhanced with multi-model support
```

**Task Distribution**:
| Task | Primary AI | Reason |
|------|-----------|--------|
| API schema design | Claude | Code quality, structure |
| Video script generation | Gemini | Creative, fast iteration |
| Security implementation | Claude | Vulnerability detection |
| Product description | Gemini | Creative variation |
| Data analysis | Gemini | Large context window |

### 2. Analytical Core Enhancement

**Current**: Basic interaction tracking
**Target**: Multi-source data intelligence

**New Data Sources**:
1. **Shopify Data Pipeline**
   - Purchase history
   - Cart abandonment
   - Customer segments
   - Product performance metrics

2. **Platform Interactions**
   - Content views (duration, engagement)
   - Community participation (posts, comments)
   - Social shares and virality metrics
   - Session patterns

3. **UGC Sentiment Analysis**
   - Review sentiment classification
   - Comment tone analysis
   - Community mood tracking
   - Brand perception monitoring

4. **External Trends**
   - Social media trend scraping
   - Ingredient popularity tracking
   - Competitor monitoring
   - Seasonal pattern analysis

**Implementation**:
```
services/
├── shopify_connector.py     # Shopify API integration
├── sentiment_analyzer.py    # UGC sentiment analysis
├── trend_tracker.py         # External trend monitoring
└── analytics_engine.py      # Unified analytics
```

**Graph Schema Extensions**:
```cypher
// New nodes
(:Purchase {purchase_id, amount, timestamp, shopify_order_id})
(:Content {content_id, type, views, engagement_score})
(:Trend {trend_id, topic, popularity_score, source})
(:Sentiment {sentiment_id, score, text, analyzed_at})

// New relationships
(:User)-[:MADE_PURCHASE]->(:Purchase)-[:CONTAINS]->(:Product)
(:User)-[:VIEWED]->(:Content)-[:FEATURES]->(:Product)
(:Product)-[:TRENDING_WITH]->(:Trend)
(:Content)-[:HAS_SENTIMENT]->(:Sentiment)
```

### 3. Generative Partner Tools

**Current**: No content generation
**Target**: Comprehensive creator co-pilot

**New Capabilities**:

#### A. Content Studio API
```
routers/
└── content_studio.py
    ├── POST /api/v1/studio/scripts/generate
    ├── POST /api/v1/studio/recipes/variate
    ├── POST /api/v1/studio/descriptions/create
    └── POST /api/v1/studio/visuals/generate
```

**Features**:
1. **Video Script Generation**
   - Input: Product info, target audience, duration
   - Output: Structured video script with scenes
   - Model: Gemini (creative + fast)

2. **Recipe Variations**
   - Input: Base recipe, dietary restrictions
   - Output: N variations with substitutions
   - Model: Claude (precise instructions)

3. **Product Descriptions**
   - Input: Product details, brand voice
   - Output: SEO-optimized, multilingual descriptions
   - Model: Gemini (creative writing)

4. **Visual Asset Generation** (Sora-like)
   - Input: Text description, style guide
   - Output: B-roll clips, product shots
   - Model: Integration with gen-AI video APIs

#### B. "Turkey Slice" Content Atomization

**Concept**: One pillar content → Multiple derivative formats

```python
class ContentAtomizer:
    """
    Takes long-form content and generates:
    - Short-form clips (TikTok/Reels)
    - Instagram carousels
    - Blog posts (SEO)
    - Social media posts
    - Community discussion prompts
    """

    def atomize(self, pillar_content: str) -> Dict[str, List]:
        # Uses Gemini for rapid generation
        # Claude for review and refinement
        pass
```

### 4. Personalization Engine 2.0

**Current**: Collaborative filtering only
**Target**: Netflix-style multi-signal personalization

**Algorithm Layers**:

1. **Collaborative Filtering** (Enhanced)
   ```cypher
   // Similar users → Similar purchases
   MATCH (u:User)-[:PURCHASED]->(p:Product)
   MATCH (p)<-[:PURCHASED]-(other:User)
   MATCH (other)-[:PURCHASED]->(rec:Product)
   WHERE NOT (u)-[:PURCHASED]->(rec)
   ```

2. **Content-Based Filtering**
   ```cypher
   // User preferences → Product attributes
   MATCH (u:User)
   WHERE u.taste_preferences.sweetness > 3
   MATCH (p:Product)
   WHERE p.flavor_profile.sweetness > 3
   ```

3. **Contextual Signals**
   - Time of day (morning → lighter products)
   - Season (summer → refreshing products)
   - User location (regional preferences)
   - Current trends (trending → boost score)

4. **Engagement Prediction**
   - ML model: Predict engagement probability
   - Features: User history, product attributes, context
   - Training: PyTorch model on historical data

**Implementation**:
```
services/
├── recommendation_engine.py  # Main engine
├── collaborative_filter.py   # CF algorithms
├── content_filter.py         # Content-based
├── context_analyzer.py       # Contextual signals
└── engagement_predictor.py   # ML model
```

**Recommendation API**:
```python
@router.get("/api/v1/recommendations/{user_id}/feed")
async def get_personalized_feed(
    user_id: str,
    content_types: List[str] = ["product", "lore", "community"],
    limit: int = 20
):
    """
    Returns hyper-personalized feed mixing:
    - Product recommendations
    - Lore/content to read
    - Community discussions
    - Creator profiles to follow
    """
    pass
```

### 5. Shopify Closed-Loop Integration

**Architecture**: Bidirectional sync

#### A. Shopify → NERDX (Data Ingestion)

**Webhooks**:
```python
@router.post("/api/v1/webhooks/shopify/orders/paid")
async def handle_order_paid(order: ShopifyOrder):
    """
    When customer purchases:
    1. Record in Neo4j graph
    2. Update user profile
    3. Trigger recommendation update
    4. Update product popularity
    """
    pass

@router.post("/api/v1/webhooks/shopify/customers/updated")
async def handle_customer_updated(customer: ShopifyCustomer):
    """Sync customer data changes"""
    pass
```

**Batch Sync**:
```python
class ShopifyDataPipeline:
    """
    Daily sync of:
    - Product catalog updates
    - Customer segments
    - Analytics data (ShopifyQL)
    """

    def sync_products(self):
        # GraphQL Admin API
        pass

    def sync_analytics(self):
        # ShopifyQL queries
        pass
```

#### B. NERDX → Shopify (Product Management)

```python
class ShopifyProductManager:
    """
    Manage products on behalf of creators:
    - Create product listings
    - Update inventory
    - Manage collections
    - Handle metafields
    """

    def create_creator_store(self, creator_id: str):
        # Use Admin API to create storefront
        pass
```

#### C. Closed-Loop Learning

```
User Journey:
1. View content in NERDX → (track engagement)
2. AI recommends product → (track impression)
3. Click product → (track click)
4. Purchase on Shopify → (webhook: track conversion)
5. Data flows back → (update WORLD MODEL)
6. Improved recommendations → (feedback loop closes)
```

**Metrics Tracked**:
- Impression → Click Rate (ICR)
- Click → Purchase Rate (CPR)
- Content → Commerce Conversion
- Recommendation Accuracy
- Customer Lifetime Value Impact

### 6. Future-Ready: Agentic Commerce Protocol (ACP)

**Vision**: AI agents can make purchases

**Preparation**:
```python
@router.post("/api/v1/commerce/agentic/purchase")
async def agentic_purchase(request: ACPRequest):
    """
    ACP-compatible endpoint:
    - Authenticate AI agent
    - Verify user intent
    - Complete purchase programmatically
    - Return structured confirmation
    """
    pass
```

**Benefits**:
- "Find and buy this creator's natural wine"
- Conversational commerce
- Reduced friction
- Future-proof architecture

## Implementation Phases

### Phase 2A: AI Orchestration (Weeks 1-2)
- [ ] Set up Vercel AI SDK integration
- [ ] Implement Claude agent wrapper
- [ ] Implement Gemini agent wrapper
- [ ] Create orchestrator with task routing
- [ ] Update Maeju to use multi-model approach
- [ ] Add model performance monitoring

### Phase 2B: Shopify Integration (Weeks 3-4)
- [ ] Implement Shopify connector service
- [ ] Set up webhook receivers
- [ ] Create data sync pipelines
- [ ] Extend graph schema for purchases
- [ ] Build closed-loop analytics
- [ ] Add privacy compliance (GDPR/CCPA)

### Phase 2C: Analytical Core (Weeks 5-6)
- [ ] Implement sentiment analyzer
- [ ] Build trend tracker
- [ ] Create unified analytics engine
- [ ] Add external data sources
- [ ] Build data warehouse
- [ ] Create analytics dashboard

### Phase 2D: Generative Tools (Weeks 7-8)
- [ ] Build Content Studio API
- [ ] Implement script generator
- [ ] Add recipe variation tool
- [ ] Create description generator
- [ ] Integrate visual gen-AI APIs
- [ ] Build content atomizer

### Phase 2E: Personalization 2.0 (Weeks 9-10)
- [ ] Enhance recommendation engine
- [ ] Add contextual signals
- [ ] Build ML engagement predictor
- [ ] Create personalized feed API
- [ ] A/B test framework
- [ ] Performance optimization

### Phase 2F: ACP Readiness (Weeks 11-12)
- [ ] Design ACP-compatible APIs
- [ ] Implement agentic purchase flow
- [ ] Add AI agent authentication
- [ ] Create product catalog API
- [ ] Build intent verification system
- [ ] Documentation and testing

## Technical Stack Additions

### New Dependencies
```txt
# AI Orchestration
anthropic>=0.25.0         # Claude API
google-generativeai>=0.8.0  # Gemini API
ai-sdk-python>=0.1.0      # Vercel AI SDK (if available)

# Shopify Integration
shopify-python-api>=12.0.0
graphql-core>=3.2.0

# Sentiment Analysis
transformers>=4.40.0
torch>=2.0.0
sentence-transformers>=2.6.0

# Trend Tracking
tweepy>=4.14.0           # Twitter API
praw>=7.7.0              # Reddit API
beautifulsoup4>=4.12.0   # Web scraping

# ML/Analytics
scikit-learn>=1.4.0
pandas>=2.2.0
numpy>=1.26.0

# Monitoring
prometheus-client>=0.20.0
sentry-sdk>=2.0.0
```

### Infrastructure Updates
```yaml
# docker-compose.yml additions
services:
  redis:
    image: redis:7-alpine
    # For caching and rate limiting

  postgres:
    image: postgres:16-alpine
    # For analytics warehouse

  prometheus:
    image: prom/prometheus:latest
    # Metrics collection

  grafana:
    image: grafana/grafana:latest
    # Metrics visualization
```

## Configuration Updates

```python
# config.py additions
class Settings(BaseSettings):
    # ... existing settings ...

    # Claude Configuration
    anthropic_api_key: str
    claude_model: str = "claude-sonnet-4.5"
    claude_max_tokens: int = 4096

    # Gemini Configuration
    google_api_key: str
    gemini_model: str = "gemini-2.0-flash"
    gemini_max_tokens: int = 8192

    # Shopify Configuration
    shopify_shop_url: str
    shopify_access_token: str
    shopify_api_version: str = "2025-01"
    shopify_webhook_secret: str

    # Sentiment Analysis
    sentiment_model: str = "distilbert-base-uncased"
    sentiment_batch_size: int = 32

    # Recommendation Engine
    rec_collab_weight: float = 0.4
    rec_content_weight: float = 0.3
    rec_context_weight: float = 0.2
    rec_ml_weight: float = 0.1

    # ACP Configuration
    acp_enabled: bool = False
    acp_agent_auth_issuer: str = "openai"
```

## API Versioning Strategy

### Version 1 (Current)
- Basic product catalog
- Simple recommendations
- Maeju chat

### Version 2 (Phase 2)
- All WORLD MODEL features
- Shopify integration
- Content studio
- Advanced personalization

**Migration Path**:
```
/api/v1/*  → Maintains backward compatibility
/api/v2/*  → New WORLD MODEL endpoints
```

## Success Metrics

### Performance
- API response time < 200ms (p95)
- Recommendation generation < 500ms
- Content generation < 3s
- 99.9% uptime SLA

### Business
- Recommendation CTR: 5% → 15%
- Content-to-commerce conversion: 2% → 8%
- Creator retention: 60% → 85%
- User session length: +50%

### AI Quality
- Sentiment accuracy > 85%
- Recommendation relevance score > 0.7
- Generated content approval rate > 80%
- Multi-model cost optimization: -30%

## Risk Mitigation

### Technical Risks
1. **Multi-model latency**: Implement aggressive caching
2. **API costs**: Rate limiting + request batching
3. **Data sync delays**: Event-driven architecture
4. **Schema migrations**: Blue-green deployment

### Business Risks
1. **Creator adoption**: Phased rollout with training
2. **User privacy**: GDPR/CCPA compliance first
3. **Shopify dependency**: Abstraction layer
4. **AI quality**: Human-in-the-loop review

## Conclusion

This expansion transforms phase1-world-model from a basic recommendation system into a comprehensive AI-native platform that:

1. **Understands** users deeply through multi-source analytics
2. **Generates** content for creators to reduce burnout
3. **Recommends** with Netflix-level personalization
4. **Integrates** seamlessly with commerce
5. **Prepares** for the agentic commerce future

The "polyglot AI" approach ensures we use the best tool for each job while maintaining a unified, orchestrated experience.

**Next Steps**: Begin Phase 2A implementation with AI orchestration layer.
