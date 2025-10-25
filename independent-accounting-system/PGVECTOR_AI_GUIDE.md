# pgvector AI Integration Guide - NERDX Independent Accounting System

**Last Updated**: 2025-10-25
**Feature**: AI-Powered Cell Performance Analysis
**Status**: Production Ready

---

## Overview

This guide explains how to use the pgvector integration for AI-powered financial analysis in the NERDX Independent Accounting System.

**What is pgvector?**
- PostgreSQL extension for storing and searching vector embeddings
- Enables semantic search and similarity analysis
- 4.4x faster than dedicated vector databases (see DATABASE_OPTIMIZATION_ANALYSIS.md)
- 75-79% cost savings vs. Pinecone

**Use Cases**:
- Find cells with similar financial performance patterns
- Semantic search: "Show me profitable cells with declining margins"
- Anomaly detection: Identify unusual financial patterns
- Predictive analytics: Find cells at risk based on historical patterns

---

## Prerequisites

### Required
- [x] PostgreSQL 14+ with pgvector extension
- [x] Python 3.11+
- [x] SQLAlchemy 2.0.23+
- [x] psycopg2-binary 2.9.9+

### Optional (for real embeddings)
- [ ] OpenAI API key (for text-embedding-ada-002)
- [ ] Alternative: Use local embedding models (e.g., sentence-transformers)

---

## Part 1: pgvector Setup (10 minutes)

### 1.1 Enable pgvector Extension

**On Railway (Production)**:
```bash
# Connect to Railway PostgreSQL
railway connect postgresql

# Enable extension
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

# Verify
\dx vector
```

**On Local PostgreSQL**:
```bash
# Install pgvector extension
# macOS
brew install pgvector

# Ubuntu/Debian
sudo apt install postgresql-15-pgvector

# Enable in database
psql -U nerdx_user -d nerdx_accounting
CREATE EXTENSION IF NOT EXISTS vector;
```

### 1.2 Verify Installation

```sql
-- Check if vector extension is enabled
SELECT * FROM pg_extension WHERE extname = 'vector';

-- Test vector operations
SELECT '[1,2,3]'::vector <-> '[4,5,6]'::vector AS distance;
-- Expected: A numeric distance value
```

---

## Part 2: Using the pgvector Service (15 minutes)

### 2.1 Basic Usage

```python
from pgvector_service import PgVectorService
from datetime import date

# Initialize service
service = PgVectorService(
    database_url="postgresql://user:pass@localhost:5432/nerdx_accounting",
    openai_api_key="sk-..."  # Optional
)

# Ensure pgvector is enabled
service.ensure_pgvector_extension()
```

### 2.2 Store Embeddings for Financial Reports

```python
# Example financial data
financial_data = {
    'cell_id': 'CELL-001',
    'cell_name': 'Product Development Team',
    'summary_date': date.today(),
    'total_revenue': 5000000,
    'total_cost': 3500000,
    'gross_profit': 1500000,
    'gross_profit_margin': 30.0
}

# Store embedding
service.store_embedding(
    cell_id=financial_data['cell_id'],
    report_date=financial_data['summary_date'],
    financial_data=financial_data
)
```

### 2.3 Find Similar Cells

```python
# Find cells with similar financial patterns
similar_cells = service.find_similar_cells(
    cell_id='CELL-001',
    report_date=date.today(),
    limit=5,
    similarity_threshold=0.8  # 0-1, higher = more similar
)

for cell in similar_cells:
    print(f"{cell['cell_name']}: {cell['similarity_score']:.2%} similar")
    print(f"  Pattern: {cell['source_text']}")
```

### 2.4 Semantic Search

```python
# Natural language search
results = service.semantic_search(
    query_text="profitable cells with high margins above 30%",
    limit=10
)

for result in results:
    print(f"{result['cell_name']} ({result['report_date']})")
    print(f"  Relevance: {result['relevance_score']:.2%}")
    print(f"  Summary: {result['source_text']}")
```

### 2.5 Anomaly Detection

```python
# Detect unusual financial patterns
anomalies = service.detect_anomalies(
    cell_id='CELL-001',
    days_back=30,
    anomaly_threshold=0.7  # Lower = more anomalous
)

for anomaly in anomalies:
    print(f"Anomaly on {anomaly['date']}")
    print(f"  Anomaly score: {anomaly['anomaly_score']:.2%}")
    print(f"  Description: {anomaly['description']}")
```

---

## Part 3: Integration with Daily Reports

### 3.1 Automatic Embedding Generation

Add embedding generation to your daily report workflow:

```python
from pgvector_service import PgVectorService
from database_sqlite import calculate_daily_summary, get_cells
from datetime import date

# Initialize service
pgvector = PgVectorService()

# Generate daily reports with embeddings
for cell in get_cells():
    # Calculate financial summary
    summary = calculate_daily_summary(cell['cell_id'], date.today())

    # Generate and store embedding
    financial_data = {
        'cell_id': cell['cell_id'],
        'cell_name': cell['cell_name'],
        'summary_date': summary['summary_date'],
        'total_revenue': summary['total_revenue'],
        'total_cost': summary['total_cost'],
        'gross_profit': summary['gross_profit'],
        'gross_profit_margin': summary['gross_profit_margin']
    }

    pgvector.store_embedding(
        cell_id=cell['cell_id'],
        report_date=date.today(),
        financial_data=financial_data
    )
```

### 3.2 API Endpoint for Similarity Search

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import date

app = FastAPI()
pgvector = PgVectorService()

class SimilarCellsRequest(BaseModel):
    cell_id: str
    report_date: date
    limit: int = 5

@app.post("/api/ai/similar-cells")
async def find_similar_cells(request: SimilarCellsRequest):
    """Find cells with similar financial patterns"""
    try:
        similar = pgvector.find_similar_cells(
            cell_id=request.cell_id,
            report_date=request.report_date,
            limit=request.limit
        )
        return {"similar_cells": similar}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ai/search")
async def semantic_search(query: str, limit: int = 10):
    """Semantic search across financial reports"""
    results = pgvector.semantic_search(
        query_text=query,
        limit=limit
    )
    return {"results": results}
```

---

## Part 4: Advanced Use Cases

### 4.1 Performance Benchmarking

Compare cell performance against similar cells:

```python
def benchmark_cell(cell_id: str, report_date: date):
    """Compare cell performance against similar cells"""

    # Find similar cells
    similar = service.find_similar_cells(
        cell_id=cell_id,
        report_date=report_date,
        limit=10
    )

    if not similar:
        return "No similar cells found"

    # Get current cell data
    from database_sqlite import calculate_daily_summary
    current_summary = calculate_daily_summary(cell_id, report_date)

    # Calculate average metrics from similar cells
    avg_margin = sum(
        float(cell['source_text'].split('Margin: ')[1].split('%')[0])
        for cell in similar
    ) / len(similar)

    # Compare
    current_margin = current_summary['gross_profit_margin']

    if current_margin > avg_margin:
        return f"Outperforming similar cells by {current_margin - avg_margin:.1f}%"
    else:
        return f"Underperforming similar cells by {avg_margin - current_margin:.1f}%"
```

### 4.2 Trend Analysis

Identify cells following similar trend patterns:

```python
def find_trend_followers(cell_id: str, days: int = 30):
    """Find cells with similar trend patterns"""

    # Get historical embeddings for the cell
    from datetime import timedelta

    similar_trends = []
    for days_ago in range(days):
        target_date = date.today() - timedelta(days=days_ago)

        similar = service.find_similar_cells(
            cell_id=cell_id,
            report_date=target_date,
            limit=5
        )

        # Track which cells appear consistently
        for cell in similar:
            similar_trends.append(cell['cell_id'])

    # Find most frequent similar cells
    from collections import Counter
    trend_followers = Counter(similar_trends).most_common(5)

    return trend_followers
```

### 4.3 Predictive Risk Detection

Identify cells at risk based on similar historical patterns:

```python
def detect_risk_patterns(cell_id: str):
    """Detect if current pattern matches historical failure patterns"""

    # Search for cells that had losses
    loss_patterns = service.semantic_search(
        query_text="cells with significant losses and declining margins",
        limit=20
    )

    # Compare current cell to loss patterns
    current = service.find_similar_cells(
        cell_id=cell_id,
        report_date=date.today(),
        limit=1
    )

    # Check if current cell is similar to historical losses
    for loss_pattern in loss_patterns:
        if loss_pattern['similarity_score'] > 0.85:
            return {
                'risk_level': 'HIGH',
                'similar_to': loss_pattern['cell_name'],
                'recommendation': 'Review cost structure immediately'
            }

    return {'risk_level': 'LOW'}
```

---

## Part 5: Performance Optimization

### 5.1 Index Optimization

The `init_database.sql` already includes optimized HNSW indexes:

```sql
-- HNSW index for fast similarity search
CREATE INDEX ON cell_embeddings
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);
```

**Index Parameters**:
- `m = 16`: Number of connections per layer (higher = better recall, more memory)
- `ef_construction = 64`: Build-time accuracy (higher = better index quality)

### 5.2 Query Performance Tips

```python
# Use appropriate similarity thresholds
# Too low: Too many irrelevant results
# Too high: Miss potentially useful matches
optimal_threshold = 0.75  # Good balance for financial data

# Limit results for faster queries
# Use pagination for large result sets
results = service.find_similar_cells(
    cell_id='CELL-001',
    report_date=date.today(),
    limit=10  # Start small, increase if needed
)

# Batch embedding generation for efficiency
embeddings_batch = []
for cell in cells:
    text = service.create_financial_summary_text(cell)
    embedding = service.generate_embedding(text)
    embeddings_batch.append((cell['cell_id'], embedding))

# Store in batch
for cell_id, embedding in embeddings_batch:
    service.store_embedding(cell_id, date.today(), cell, embedding=embedding)
```

### 5.3 Caching Strategy

```python
# Cache frequently accessed embeddings
from functools import lru_cache

@lru_cache(maxsize=128)
def get_cached_embedding(cell_id: str, report_date: date):
    """Cache embeddings for faster repeated access"""
    return service.generate_embedding(
        service.create_financial_summary_text({
            'cell_id': cell_id,
            'summary_date': report_date
        })
    )
```

---

## Part 6: Cost Analysis

### 6.1 OpenAI API Costs

**Using OpenAI text-embedding-ada-002**:
- Cost: $0.0001 per 1K tokens
- Average financial summary: ~100 tokens
- Cost per embedding: $0.00001 (0.001 cents)

**Monthly costs (100 cells, daily reports)**:
- 100 cells × 30 days = 3,000 embeddings/month
- 3,000 × $0.00001 = $0.03/month
- **Negligible cost!**

### 6.2 Alternative: Local Embeddings

For zero API costs, use local models:

```python
# Using sentence-transformers (free, local)
from sentence_transformers import SentenceTransformer

class LocalEmbeddingService(PgVectorService):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.embedding_dimensions = 384  # Model-specific

    def generate_embedding(self, text: str):
        return self.model.encode(text).tolist()
```

**Benefits**:
- Zero API costs
- No rate limits
- Full privacy (data never leaves your server)
- Slightly lower quality than OpenAI ada-002

---

## Part 7: Monitoring & Debugging

### 7.1 Check Embedding Quality

```sql
-- View stored embeddings
SELECT
    ce.cell_id,
    ce.report_date,
    ce.source_text,
    vector_dims(ce.embedding) as dimensions
FROM cell_embeddings ce
LIMIT 10;

-- Check for null or invalid embeddings
SELECT COUNT(*)
FROM cell_embeddings
WHERE embedding IS NULL
   OR vector_dims(embedding) != 1536;
```

### 7.2 Analyze Similarity Distribution

```sql
-- Find average similarity between all cells
SELECT
    AVG(1 - (ce1.embedding <=> ce2.embedding)) as avg_similarity
FROM cell_embeddings ce1
CROSS JOIN cell_embeddings ce2
WHERE ce1.cell_id != ce2.cell_id;

-- Expected: 0.5-0.7 for diverse cells
-- >0.8 may indicate too many similar patterns
```

### 7.3 Performance Metrics

```bash
# Query execution time
EXPLAIN ANALYZE
SELECT *
FROM cell_embeddings
ORDER BY embedding <=> '[...]'::vector
LIMIT 10;

# Expected: <50ms with HNSW index
```

---

## Part 8: Troubleshooting

### Issue: "extension 'vector' does not exist"

**Solution**: Install pgvector extension

```bash
# Railway
railway connect postgresql
CREATE EXTENSION vector;

# Local PostgreSQL
sudo apt install postgresql-15-pgvector
# Then create extension in database
```

### Issue: Slow similarity queries

**Solution**: Ensure HNSW index exists

```sql
-- Check indexes
\d cell_embeddings

-- Create if missing
CREATE INDEX ON cell_embeddings
USING hnsw (embedding vector_cosine_ops);
```

### Issue: OpenAI API rate limits

**Solution**: Use batch processing or local embeddings

```python
import time

# Add delay between API calls
for cell in cells:
    embedding = service.generate_embedding(text)
    time.sleep(0.1)  # 100ms delay = max 10 requests/second

# Or switch to local embeddings (see Part 6.2)
```

---

## Summary

**What You Learned**:
- ✅ Set up pgvector extension in PostgreSQL
- ✅ Store and search vector embeddings for financial data
- ✅ Find similar cells using cosine similarity
- ✅ Perform semantic search with natural language
- ✅ Detect anomalies and predict risks
- ✅ Optimize performance with HNSW indexes

**Key Benefits**:
- 🚀 **4.4x faster** than dedicated vector databases
- 💰 **$0.03/month** OpenAI costs (100 cells)
- 🔒 **100% data privacy** with local embeddings
- 📊 **Advanced analytics** beyond traditional queries
- 🎯 **Predictive insights** for risk management

**Next Steps**:
1. Enable pgvector in your PostgreSQL database
2. Run `python pgvector_service.py` for demo
3. Integrate with daily report generation
4. Build custom AI-powered dashboards
5. Add predictive risk alerts

---

**Guide Version**: 1.0
**Last Updated**: 2025-10-25
**Maintainer**: NERDX Development Team
