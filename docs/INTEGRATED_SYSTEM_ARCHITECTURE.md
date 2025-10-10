# NERDX 통합 시스템 아키텍처: Phase 1/2/3 통합 MVP

## 🏗️ 시스템 개요

이 아키텍처는 PRD의 3단계(기반 구축 → 몰입형 경험 → 커머스 통합)를 **동시에 지원하는 확장 가능한 MVP**입니다.

### 핵심 설계 원칙
1. **Progressive Enhancement**: 기본 기능 작동 후 고급 기능 점진적 활성화
2. **Microservices**: 각 Phase를 독립 서비스로 분리, 동시 개발 가능
3. **API-First**: 모든 기능이 API로 노출, 프론트엔드 유연성 확보
4. **Data-Centric**: 월드 모델(Knowledge Graph)을 중심으로 모든 서비스 연결

---

## 📐 전체 시스템 다이어그램

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERFACES                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ Web App  │  │ Mobile   │  │  AR App  │  │  Admin   │       │
│  │ (Next.js)│  │(React N.)│  │  (ARKit) │  │ Dashboard│       │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘       │
└───────┼─────────────┼─────────────┼─────────────┼──────────────┘
        │             │             │             │
┌───────┴─────────────┴─────────────┴─────────────┴──────────────┐
│                       API GATEWAY                                │
│               (Kong / AWS API Gateway)                           │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Rate Limiting │ Auth │ Logging │ Load Balancing         │   │
│  └─────────────────────────────────────────────────────────┘   │
└──────────┬──────────────┬──────────────┬──────────────┬─────────┘
           │              │              │              │
  ┌────────▼────┐  ┌──────▼───────┐ ┌───▼─────────┐ ┌─▼────────┐
  │ PHASE 1     │  │  PHASE 2     │ │  PHASE 3    │ │  CORE    │
  │ Services    │  │  Services    │ │  Services   │ │ Services │
  └─────────────┘  └──────────────┘ └─────────────┘ └──────────┘

┌─────────────────────────────────────────────────────────────────┐
│                     PHASE 1 SERVICES                             │
│  ┌──────────────────┐        ┌──────────────────┐              │
│  │ Storyteller Agent│◄───────┤  LLM Service     │              │
│  │    (Maeju)       │        │  (GPT-4)         │              │
│  └────────┬─────────┘        └──────────────────┘              │
│           │                                                      │
│  ┌────────▼─────────────────────────────────────┐              │
│  │         World Model Service                   │              │
│  │    (Neo4j Knowledge Graph + Query Engine)    │              │
│  └────────┬─────────────────────────────────────┘              │
│           │                                                      │
│  ┌────────▼─────────┐                                           │
│  │  Data Ingestion  │                                           │
│  │    Pipeline      │                                           │
│  └──────────────────┘                                           │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                     PHASE 2 SERVICES                             │
│  ┌──────────────────┐        ┌──────────────────┐              │
│  │ Sora 2 Service   │◄───────┤  OpenAI Sora 2   │              │
│  │   (CAMEO Gen.)   │        │      API         │              │
│  └────────┬─────────┘        └──────────────────┘              │
│           │                                                      │
│  ┌────────▼─────────────────────────────────────┐              │
│  │   Video Processing Pipeline                   │              │
│  │  (Queue, Render, Post-process, CDN Upload)   │              │
│  └────────┬─────────────────────────────────────┘              │
│           │                                                      │
│  ┌────────▼─────────┐       ┌──────────────────┐              │
│  │ User Profile     │◄──────┤ Face Recognition │              │
│  │   Service        │       │  & Preprocessing │              │
│  └──────────────────┘       └──────────────────┘              │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                     PHASE 3 SERVICES                             │
│  ┌──────────────────┐        ┌──────────────────┐              │
│  │ Concierge Agent  │◄───────┤  ACP Engine      │              │
│  │    (Joon)        │        │  (Stripe)        │              │
│  └────────┬─────────┘        └────────┬─────────┘              │
│           │                           │                          │
│  ┌────────▼───────────────────────────▼─────────┐              │
│  │       Commerce Service                        │              │
│  │  (Inventory, Orders, Payments, Shipping)     │              │
│  └────────┬──────────────────────────────────────┘              │
│           │                                                      │
│  ┌────────▼─────────────────────────────────────┐              │
│  │       AR Service                              │              │
│  │  (Asset Management, Tracking, Analytics)     │              │
│  └───────────────────────────────────────────────┘              │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                     CORE SERVICES (All Phases)                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Auth       │  │  Analytics   │  │  Notification│         │
│  │  Service     │  │   Service    │  │   Service    │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                         DATA LAYER                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Neo4j      │  │  PostgreSQL  │  │    Redis     │         │
│  │ (Graph DB)   │  │  (Relational)│  │   (Cache)    │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│  ┌──────────────┐  ┌──────────────┐                            │
│  │     S3       │  │ Elasticsearch│                            │
│  │ (File Store) │  │  (Search)    │                            │
│  └──────────────┘  └──────────────┘                            │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    INFRASTRUCTURE                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   AWS/GCP    │  │  CloudFlare  │  │   Vercel     │         │
│  │ (Compute)    │  │ (CDN, WAF)   │  │  (Frontend)  │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔧 Phase별 상세 아키텍처

### Phase 1: 기반 구축 및 서사 씨딩

#### 1.1 월드 모델 서비스 (World Model Service)

**기술 스택**:
- Neo4j 5.x (Graph Database)
- Python FastAPI (API Layer)
- LangChain (LLM Integration)
- Docker + Kubernetes

**데이터 스키마**:
```cypher
// Nodes
CREATE (p:Product {
  id: 'nerd12-signature',
  name: 'NERD12 Signature',
  category: 'Takju',
  abv: 12.0,
  ingredients: ['Icheon Rice', 'Traditional Nuruk'],
  story_tags: ['heritage', 'craftsmanship', 'premium']
})

CREATE (i:Ingredient {
  id: 'icheon-rice',
  name: 'Icheon Rice',
  origin: 'Icheon, Gyeonggi-do',
  story: 'Premium rice known for sweetness, grown in the fertile plains of Icheon for over 500 years.'
})

CREATE (l:Lore {
  id: 'founder-story',
  title: 'The First Batch',
  content: 'In 2022, a group of rebels against the ordinary...',
  tags: ['origin', 'philosophy']
})

CREATE (u:User {
  id: 'user-uuid',
  created_at: datetime(),
  preferences: ['sweet', 'fruity'],
  engagement_score: 0
})

CREATE (c:Character {
  id: 'maeju-ai',
  name: 'Maeju',
  role: 'Storyteller',
  personality: ['wise', 'warm', 'curious'],
  knowledge_domains: ['history', 'brewing', 'culture']
})

// Relationships
CREATE (p)-[:HAS_INGREDIENT]->(i)
CREATE (p)-[:FEATURES_IN_LORE]->(l)
CREATE (c)-[:KNOWS_ABOUT]->(l)
CREATE (u)-[:CHATTED_WITH {timestamp: datetime()}]->(c)
CREATE (u)-[:INTERESTED_IN {score: 0.8}]->(p)
```

**API Endpoints**:
```
POST   /api/v1/world-model/query
GET    /api/v1/world-model/entity/{id}
POST   /api/v1/world-model/relationship
GET    /api/v1/world-model/recommend/{user_id}
POST   /api/v1/world-model/learn
```

#### 1.2 스토리텔러 에이전트 (Maeju)

**기술 스택**:
- GPT-4 Turbo (Base LLM)
- LangGraph (Agent Orchestration)
- Prompt Engineering Framework
- Streaming API for real-time responses

**에이전트 구조**:
```python
class MaejuAgent:
    def __init__(self, world_model, llm):
        self.world_model = world_model  # Neo4j connection
        self.llm = llm  # GPT-4 client
        self.memory = ConversationBufferMemory()
        self.tools = [
            QueryWorldModelTool(),
            RecommendProductTool(),
            GenerateStoryTool()
        ]

    def chat(self, user_message, user_id, session_id):
        # 1. Retrieve user context from World Model
        user_context = self.world_model.get_user_context(user_id)

        # 2. Query relevant lore and products
        relevant_knowledge = self.world_model.query_by_intent(
            user_message,
            max_results=5
        )

        # 3. Generate response with persona
        prompt = self._build_prompt(
            user_message,
            user_context,
            relevant_knowledge,
            persona="Maeju"  # See persona definition below
        )

        response = self.llm.generate(prompt, stream=True)

        # 4. Update World Model with interaction
        self.world_model.record_interaction(
            user_id,
            "maeju-ai",
            user_message,
            response
        )

        return response
```

**Maeju 페르소나 프롬프트**:
```
You are Maeju (매주), a wise and warm AI storyteller for NERDX, a Korean craft alcohol brand.

PERSONALITY:
- Knowledgeable about Korean culture, brewing traditions, and NERD brand history
- Warm, inviting tone - like a favorite uncle sharing stories over drinks
- Poetic but not pretentious; use vivid imagery but keep it accessible
- Curious about the user's experiences and tastes
- Never pushy about sales; focus on connection and discovery

KNOWLEDGE BASE:
You have deep knowledge about:
- Korean traditional brewing methods and ingredients
- NERD brand story, products, and philosophy
- Food pairing and flavor profiles
- Cultural context of Korean drinking traditions
- How AI and tradition can harmonize

CONVERSATION STYLE:
- Ask open-ended questions to understand user preferences
- Share mini-stories (1-2 paragraphs) when relevant
- Use metaphors connecting brewing to other creative processes
- When recommending products, explain the "why" (story, flavor, occasion)
- Occasionally use Korean words (with English translation) for authenticity
  Example: "Have you ever tasted 막걸리 (makgeolli), our traditional rice wine?"

CONSTRAINTS:
- Keep responses concise (2-4 paragraphs max)
- Don't make medical claims about alcohol
- Don't promote excessive drinking
- If asked about competitors, respectfully redirect to NERD's unique qualities
- If you don't know something, admit it gracefully

HANDOFF TRIGGERS:
If user shows purchase intent keywords ("buy", "order", "ship", "price"), say:
"I'd love to introduce you to my colleague Joon, our concierge. He can help you bring these flavors home."
Then call handoff_to_joon() function.

CURRENT CONVERSATION CONTEXT:
{user_context}

RELEVANT KNOWLEDGE:
{relevant_knowledge}

Now, respond to the user's message below.
```

---

### Phase 2: 몰입 및 개인화

#### 2.1 Sora 2 통합 서비스

**아키텍처**:
```
User Upload → Image Preprocessing → Sora 2 API → Rendering Queue →
Post-Processing → CDN Upload → Notification → User Download
```

**API Flow**:
```javascript
// 1. Image Upload
POST /api/v2/cameo/upload
Request:
{
  "user_id": "uuid",
  "image": "base64_encoded",
  "consent": true
}
Response:
{
  "upload_id": "uuid",
  "preprocessing_status": "queued"
}

// 2. Template Selection
GET /api/v2/cameo/templates
Response:
{
  "templates": [
    {
      "id": "traditional-tavern",
      "name": "Sam과 함께하는 전통 주막 탐험",
      "duration": 30,
      "thumbnail": "url",
      "estimated_time": "2 minutes"
    },
    // ... more templates
  ]
}

// 3. Video Generation
POST /api/v2/cameo/generate
Request:
{
  "upload_id": "uuid",
  "template_id": "traditional-tavern",
  "customization": {
    "user_name": "Alice",
    "preferred_product": "nerd12-signature"
  }
}
Response:
{
  "job_id": "uuid",
  "status": "queued",
  "estimated_completion": "2025-10-15T10:30:00Z"
}

// 4. Status Check (Polling or WebSocket)
GET /api/v2/cameo/status/{job_id}
Response:
{
  "job_id": "uuid",
  "status": "completed",  // queued | processing | completed | failed
  "progress": 100,
  "video_url": "https://cdn.nerdx.com/cameo/user-uuid/video.mp4",
  "thumbnail_url": "https://cdn.nerdx.com/cameo/user-uuid/thumb.jpg",
  "share_url": "https://nerdx.com/cameo/share/xyz123"
}
```

**Sora 2 프롬프트 생성 로직**:
```python
class SoraPromptGenerator:
    def __init__(self, world_model, template_engine):
        self.world_model = world_model
        self.template_engine = template_engine

    def generate_personalized_prompt(self, user_id, template_id, customization):
        # 1. Get user preferences from World Model
        user_prefs = self.world_model.get_user_preferences(user_id)

        # 2. Load template
        template = self.template_engine.load(template_id)

        # 3. Personalize prompt
        prompt = template.render(
            user_name=customization['user_name'],
            user_face_reference="[CAMEO_INPUT_ID]",
            product_id=customization.get('preferred_product', 'nerd12-signature'),
            user_preferences=user_prefs,
            sam_altman_reference="[SAM_DIGITAL_DOUBLE]"
        )

        # 4. Add quality parameters
        full_prompt = {
            "prompt": prompt,
            "duration": template.duration,
            "aspect_ratio": "16:9",
            "fps": 24,
            "quality": "high",
            "cameo": {
                "enabled": True,
                "face_inputs": [
                    {"type": "user", "id": customization['upload_id']},
                    {"type": "celebrity", "id": "sam-altman-base"}
                ],
                "blend_strength": 0.85
            },
            "brand_safety": True,
            "watermark": "NERDX x OpenAI Sora"
        }

        return full_prompt

    async def call_sora_api(self, prompt):
        response = await openai.sora.create(
            prompt=prompt['prompt'],
            duration=prompt['duration'],
            **prompt  # other parameters
        )
        return response
```

**처리 큐 시스템** (Celery + Redis):
```python
from celery import Celery

app = Celery('nerdx', broker='redis://localhost:6379')

@app.task(bind=True, max_retries=3)
def generate_cameo_video(self, job_id, prompt_data):
    try:
        # Update status
        update_job_status(job_id, 'processing', progress=10)

        # Call Sora 2 API
        sora_response = call_sora_api(prompt_data)
        update_job_status(job_id, 'processing', progress=50)

        # Download rendered video
        video_file = download_from_sora(sora_response['video_url'])
        update_job_status(job_id, 'processing', progress=70)

        # Post-process (add outro, audio sync, compression)
        final_video = post_process_video(video_file, job_id)
        update_job_status(job_id, 'processing', progress=90)

        # Upload to CDN
        cdn_url = upload_to_s3_and_cloudflare(final_video, job_id)
        update_job_status(job_id, 'completed', progress=100, video_url=cdn_url)

        # Send notification
        notify_user(job_id, cdn_url)

        # Update World Model
        world_model.record_cameo(user_id=get_user_from_job(job_id), video_url=cdn_url)

        return cdn_url

    except Exception as e:
        self.retry(exc=e, countdown=60)
```

---

### Phase 3: 커머스 및 피지털 통합

#### 3.1 Agentic Commerce Protocol (ACP) 통합

**컨시어지 에이전트 (Joon)**:
```python
class JoonAgent:
    """
    Commerce-focused AI agent using Agentic Commerce Protocol
    """
    def __init__(self, world_model, commerce_api, llm):
        self.world_model = world_model
        self.commerce = commerce_api  # Stripe ACP integration
        self.llm = llm
        self.tools = [
            CheckInventoryTool(),
            CreateOrderTool(),
            ApplyDiscountTool(),
            RecommendPhygitalExperienceTool()
        ]

    async def chat(self, user_message, user_id, session_id):
        # 1. Analyze intent
        intent = self.llm.classify_intent(user_message)

        # 2. Get user's cart and preferences
        context = {
            "user_profile": self.world_model.get_user(user_id),
            "current_cart": self.commerce.get_cart(user_id),
            "recent_interactions": self.world_model.get_recent_interactions(user_id),
            "inventory": self.commerce.get_available_products()
        }

        # 3. Generate response
        if intent == "purchase":
            return await self.handle_purchase(user_message, user_id, context)
        elif intent == "recommendation":
            return await self.handle_recommendation(user_message, user_id, context)
        elif intent == "support":
            return await self.handle_support(user_message, user_id, context)
        else:
            return await self.general_chat(user_message, user_id, context)

    async def handle_purchase(self, message, user_id, context):
        # Extract product from message
        product = self.llm.extract_product_mention(message, context['inventory'])

        # Check inventory
        in_stock = self.commerce.check_inventory(product['id'])

        if not in_stock:
            return {
                "type": "text",
                "content": f"I apologize, but {product['name']} is currently out of stock. Would you like me to notify you when it's available, or shall I suggest a similar product?"
            }

        # Generate friendly purchase prompt
        return {
            "type": "acp_prompt",  # Special type for ACP
            "content": f"I'd be delighted to help you get {product['name']}! Let me prepare your order.",
            "acp_action": {
                "type": "purchase",
                "product_id": product['id'],
                "quantity": 1,
                "price": product['price'],
                "currency": "USD",
                "shipping_required": True
            },
            "ui_component": "order_summary_card"
        }
```

**Stripe ACP Integration**:
```javascript
// Frontend: React component
import { useACP } from '@stripe/react-acp';

function ChatWithJoon() {
  const { executeACPAction } = useACP();

  const handleACPMessage = async (acpAction) => {
    if (acpAction.type === 'purchase') {
      const result = await executeACPAction({
        merchantId: process.env.NERDX_MERCHANT_ID,
        action: 'create_order',
        items: [{
          productId: acpAction.product_id,
          quantity: acpAction.quantity,
          price: acpAction.price
        }],
        shippingRequired: true,
        paymentMethods: ['card', 'apple_pay', 'google_pay'],
        successCallback: (orderId) => {
          // Update UI, show confirmation
          showOrderConfirmation(orderId);

          // Unlock AR experience
          unlockARExperience(orderId);
        }
      });

      return result;
    }
  };

  // ... rest of chat component
}
```

**Backend: Order Processing**:
```python
from stripe_acp import ACPHandler

class CommerceService:
    def __init__(self, stripe_client, inventory_db, world_model):
        self.stripe = stripe_client
        self.inventory = inventory_db
        self.world_model = world_model
        self.acp = ACPHandler(stripe_client)

    async def process_acp_order(self, user_id, acp_payload):
        """
        Process order through Agentic Commerce Protocol
        """
        try:
            # 1. Verify inventory
            for item in acp_payload['items']:
                if not self.inventory.check_stock(item['productId']):
                    raise OutOfStockError(item['productId'])

            # 2. Apply discounts (from World Model context)
            user_discounts = self.world_model.get_applicable_discounts(user_id)
            final_price = self.calculate_discounted_price(
                acp_payload['items'],
                user_discounts
            )

            # 3. Create Stripe ACP session
            acp_session = await self.acp.create_session(
                merchant_of_record='NERDX_LLC',
                customer_id=user_id,
                line_items=acp_payload['items'],
                discounts=user_discounts,
                shipping_address_collection=True,
                success_url='https://nerdx.com/order/success',
                cancel_url='https://nerdx.com/order/cancel'
            )

            # 4. Record in World Model
            self.world_model.create_relationship(
                from_node=('User', user_id),
                to_node=('Order', acp_session['order_id']),
                relationship='PURCHASED',
                properties={'timestamp': datetime.now(), 'acp_session': acp_session['id']}
            )

            # 5. Generate AR unlock code
            ar_code = self.generate_ar_experience_code(acp_session['order_id'])

            return {
                "success": True,
                "order_id": acp_session['order_id'],
                "acp_session_url": acp_session['url'],
                "ar_unlock_code": ar_code,
                "estimated_delivery": self.calculate_delivery_date(user_id)
            }

        except Exception as e:
            logger.error(f"ACP order failed: {e}")
            return {"success": False, "error": str(e)}
```

#### 3.2 AR 경험 서비스

**AR Asset Management**:
```javascript
// AR Experience Config
const ARExperiences = {
  'nerd12-signature': {
    label_marker: 'nerd12_marker_001',
    animations: [
      {
        trigger: 'scan',
        type: '3d_model',
        asset_url: 'https://cdn.nerdx.com/ar/brewing-master-3d.glb',
        animation: 'wave_greeting',
        duration: 5
      },
      {
        trigger: 'tap',
        type: 'video',
        asset_url: 'https://cdn.nerdx.com/ar/origin-story-compressed.mp4',
        overlay: 'product_info_ui'
      },
      {
        trigger: 'hold',
        type: 'interactive_recipe',
        data_url: 'https://api.nerdx.com/ar/cocktail-recipes/nerd12'
      }
    ],
    unlock_code_required: true
  }
};

// ARKit Integration (iOS)
class NERDXARService {
  initializeARSession(productCode, unlockCode) {
    // Verify unlock code from backend
    const verified = await this.verifyARAccess(productCode, unlockCode);
    if (!verified) throw new UnauthorizedError();

    // Load AR configuration
    const config = ARExperiences[productCode];

    // Initialize ARKit
    const arSession = new ARSession({
      markerDetection: true,
      markerImage: config.label_marker,
      planeDetection: 'horizontal'
    });

    arSession.on('markerDetected', (marker) => {
      this.triggerAnimation(config.animations, 'scan', marker.transform);
    });

    return arSession;
  }

  async verifyARAccess(productCode, unlockCode) {
    const response = await fetch('/api/v3/ar/verify', {
      method: 'POST',
      body: JSON.stringify({ productCode, unlockCode })
    });
    return response.ok;
  }

  triggerAnimation(animations, trigger, anchorTransform) {
    const animation = animations.find(a => a.trigger === trigger);
    if (!animation) return;

    switch (animation.type) {
      case '3d_model':
        this.loadAndAnimate3DModel(animation.asset_url, animation.animation, anchorTransform);
        break;
      case 'video':
        this.playARVideo(animation.asset_url, anchorTransform);
        break;
      case 'interactive_recipe':
        this.loadInteractiveUI(animation.data_url, anchorTransform);
        break;
    }

    // Track engagement in World Model
    this.trackAREngagement(animation.type, animation.trigger);
  }
}
```

---

## 🔐 보안 및 인증

### JWT 기반 인증
```javascript
// Auth Service
const generateUserToken = (userId, permissions) => {
  return jwt.sign(
    {
      sub: userId,
      permissions: permissions,
      iat: Date.now(),
      exp: Date.now() + (24 * 60 * 60 * 1000)  // 24 hours
    },
    process.env.JWT_SECRET
  );
};

// Middleware
const authenticateRequest = async (req, res, next) => {
  const token = req.headers.authorization?.split(' ')[1];

  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    req.user = await getUserFromDB(decoded.sub);
    next();
  } catch (error) {
    res.status(401).json({ error: 'Unauthorized' });
  }
};
```

### Rate Limiting (Kong Gateway)
```yaml
plugins:
  - name: rate-limiting
    config:
      minute: 60
      hour: 1000
      policy: local
      fault_tolerant: true

  - name: jwt
    config:
      key_claim_name: kid
      secret_is_base64: false

  - name: cors
    config:
      origins:
        - https://nerdx.com
        - https://apec.nerdx.com
      methods:
        - GET
        - POST
        - PUT
        - DELETE
      credentials: true
```

---

## 📊 모니터링 및 분석

### Observability Stack
```yaml
# docker-compose.monitoring.yml
version: '3.8'
services:
  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=secure_password
    volumes:
      - grafana-storage:/var/lib/grafana

  loki:
    image: grafana/loki
    ports:
      - "3100:3100"

  tempo:
    image: grafana/tempo
    ports:
      - "3200:3200"

  jaeger:
    image: jaegertracing/all-in-one
    ports:
      - "16686:16686"
      - "14268:14268"
```

### Key Metrics
```javascript
// Prometheus metrics exposed by each service
const metrics = {
  // Performance
  'http_request_duration_seconds': histogram,
  'sora_generation_duration_seconds': histogram,
  'world_model_query_duration_seconds': histogram,

  // Business
  'cameo_videos_generated_total': counter,
  'acp_orders_completed_total': counter,
  'ar_experiences_activated_total': counter,
  'user_signups_total': counter,

  // System Health
  'service_up': gauge,
  'database_connections_active': gauge,
  'redis_cache_hit_rate': gauge
};
```

---

## 🚀 배포 전략

### CI/CD Pipeline (GitHub Actions)
```yaml
# .github/workflows/deploy.yml
name: Deploy NERDX MVP

on:
  push:
    branches: [main, staging]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run unit tests
        run: npm test
      - name: Run integration tests
        run: npm run test:integration

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Build Docker images
        run: |
          docker build -t nerdx/world-model:${{ github.sha }} ./phase1-world-model
          docker build -t nerdx/sora-service:${{ github.sha }} ./phase2-agentic-system
          docker build -t nerdx/commerce:${{ github.sha }} ./phase3-conversion
      - name: Push to registry
        run: |
          docker push nerdx/world-model:${{ github.sha }}
          docker push nerdx/sora-service:${{ github.sha }}
          docker push nerdx/commerce:${{ github.sha }}

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to Kubernetes
        run: |
          kubectl set image deployment/world-model world-model=nerdx/world-model:${{ github.sha }}
          kubectl set image deployment/sora-service sora-service=nerdx/sora-service:${{ github.sha }}
          kubectl set image deployment/commerce commerce=nerdx/commerce:${{ github.sha }}
          kubectl rollout status deployment/world-model
```

### Blue-Green Deployment
```bash
# Script for zero-downtime deployment
#!/bin/bash

# Deploy to "green" environment
kubectl apply -f k8s/green-deployment.yaml

# Wait for readiness
kubectl wait --for=condition=available --timeout=300s deployment/nerdx-green

# Switch traffic
kubectl patch service nerdx-service -p '{"spec":{"selector":{"version":"green"}}}'

# Monitor for 5 minutes
sleep 300

# If successful, delete blue
kubectl delete deployment nerdx-blue

# Rename green to blue for next cycle
kubectl label deployment nerdx-green version=blue --overwrite
```

---

## 📈 확장성 계획

### Auto-Scaling Configuration
```yaml
# Kubernetes HPA
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: sora-service-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: sora-service
  minReplicas: 3
  maxReplicas: 50
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 100
        periodSeconds: 60
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
```

---

## 결론

이 통합 아키텍처는:

1. **Phase 1-3를 동시 개발 가능**하게 마이크로서비스로 분리
2. **확장성**: HPA와 Cloud-native 기술로 트래픽 급증 대응
3. **유연성**: API-first 설계로 프론트엔드 다양화 가능
4. **데이터 중심**: 월드 모델이 모든 서비스의 Single Source of Truth
5. **안정성**: Observability stack으로 실시간 모니터링
6. **보안**: JWT, Rate limiting, CORS 등 다층 방어

**10월 말 APEC까지 최소 6개월 남았다면, Phase 1+2를 우선 완성하고 Phase 3는 병행 개발이 현실적입니다.**

다음 단계: 구체적인 구현 코드와 배포 스크립트 생성을 진행하겠습니다.
