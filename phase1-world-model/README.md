# Phase 1: World Model

Knowledge graph and AI storytelling API for NERDX APEC MVP.

## Features

- **Neo4j Graph Database**: Product catalog, ingredients, lore, user relationships
- **Maeju AI Agent**: Conversational storytelling agent powered by GPT-4
- **Product Discovery**: Search, recommendations, and similar product suggestions
- **User Personalization**: Taste preferences and interaction tracking
- **FastAPI Backend**: RESTful API with OpenAPI documentation

## Quick Start

### 1. Setup Environment

```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your credentials
# - OPENAI_API_KEY
# - NEO4J credentials
```

### 2. Start Neo4j

```bash
# Using Docker
docker run \
    --name neo4j \
    -p 7474:7474 -p 7687:7687 \
    -e NEO4J_AUTH=neo4j/your_password \
    neo4j:latest
```

### 3. Run API

```bash
python main.py
```

API will be available at:
- API: http://localhost:8001
- Docs: http://localhost:8001/docs
- Health: http://localhost:8001/health

## API Endpoints

### Products
- `GET /api/v1/products` - List/search products
- `GET /api/v1/products/{id}` - Get product details
- `GET /api/v1/products/{id}/similar` - Get similar products

### Chat (Maeju AI)
- `POST /api/v1/chat` - Chat with Maeju AI agent
- `POST /api/v1/chat/analyze-preferences` - Analyze taste preferences

### Users
- `GET /api/v1/users/{id}` - Get user profile
- `PUT /api/v1/users/{id}/preferences` - Update preferences
- `POST /api/v1/users/{id}/interactions` - Track interactions

### Recommendations
- `GET /api/v1/recommendations/{user_id}` - Personalized recommendations

## Architecture

```
phase1-world-model/
├── main.py                 # FastAPI app
├── config.py               # Configuration
├── models/                 # Data models
│   ├── graph_models.py     # Neo4j models
│   └── api_models.py       # Pydantic models
├── services/               # Business logic
│   └── neo4j_service.py    # Neo4j operations
├── agents/                 # AI agents
│   └── maeju_agent.py      # Storytelling agent
└── routers/                # API routes
    ├── products.py
    ├── chat.py
    ├── users.py
    └── recommendations.py
```

## Testing

```bash
pytest tests/
```

## Docker

```bash
docker build -t nerdx-phase1 .
docker run -p 8001:8001 --env-file .env nerdx-phase1
```
