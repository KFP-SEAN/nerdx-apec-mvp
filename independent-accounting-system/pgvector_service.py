"""
NERDX Independent Accounting System - pgvector AI Integration Service
Provides semantic search and similarity analysis for Cell performance patterns
"""

import os
from typing import List, Dict, Any, Optional
from datetime import date, datetime
import json

# PostgreSQL with pgvector
try:
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker
    POSTGRESQL_AVAILABLE = True
except ImportError:
    POSTGRESQL_AVAILABLE = False
    print("[WARNING] PostgreSQL dependencies not available. Install: pip install sqlalchemy psycopg2-binary")

# OpenAI for embeddings (optional)
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("[WARNING] OpenAI not available. Install: pip install openai")


class PgVectorService:
    """
    pgvector Integration Service for AI-powered Cell analysis

    Features:
    - Store embeddings of daily financial reports
    - Find similar Cell performance patterns
    - Semantic search across financial summaries
    - Anomaly detection using vector similarity
    """

    def __init__(self, database_url: Optional[str] = None, openai_api_key: Optional[str] = None):
        """
        Initialize pgvector service

        Args:
            database_url: PostgreSQL connection string (with pgvector enabled)
            openai_api_key: OpenAI API key for generating embeddings
        """
        if not POSTGRESQL_AVAILABLE:
            raise ImportError("PostgreSQL dependencies required. Install: pip install sqlalchemy psycopg2-binary")

        self.database_url = database_url or os.getenv('DATABASE_URL')
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')

        if not self.database_url:
            raise ValueError("DATABASE_URL must be provided or set in environment")

        # Initialize database connection
        self.engine = create_engine(self.database_url)
        self.Session = sessionmaker(bind=self.engine)

        # Initialize OpenAI client if available
        if OPENAI_AVAILABLE and self.openai_api_key:
            openai.api_key = self.openai_api_key
            self.embedding_model = "text-embedding-ada-002"
            self.embedding_dimensions = 1536
        else:
            print("[INFO] OpenAI not configured. Embeddings will use mock data.")
            self.embedding_model = None
            self.embedding_dimensions = 1536

    def ensure_pgvector_extension(self):
        """Ensure pgvector extension is enabled in PostgreSQL"""
        with self.engine.connect() as conn:
            try:
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                conn.commit()
                print("[OK] pgvector extension enabled")
            except Exception as e:
                print(f"[WARNING] Could not enable pgvector: {e}")

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector for text using OpenAI API

        Args:
            text: Text to embed

        Returns:
            List of floats representing the embedding vector (1536 dimensions)
        """
        if not OPENAI_AVAILABLE or not self.openai_api_key:
            # Return mock embedding for demo purposes
            import hashlib
            import numpy as np

            # Generate deterministic mock embedding based on text hash
            hash_val = int(hashlib.md5(text.encode()).hexdigest(), 16)
            np.random.seed(hash_val % (2**32))
            embedding = np.random.rand(self.embedding_dimensions).tolist()
            return embedding

        try:
            response = openai.Embedding.create(
                model=self.embedding_model,
                input=text
            )
            return response['data'][0]['embedding']
        except Exception as e:
            print(f"[ERROR] Failed to generate embedding: {e}")
            # Fallback to mock embedding
            import numpy as np
            return np.random.rand(self.embedding_dimensions).tolist()

    def create_financial_summary_text(self, cell_data: Dict[str, Any]) -> str:
        """
        Create a text summary of financial data for embedding

        Args:
            cell_data: Dictionary containing cell financial information

        Returns:
            Formatted text summary
        """
        summary_parts = [
            f"Cell: {cell_data.get('cell_name', 'Unknown')}",
            f"Date: {cell_data.get('summary_date', date.today())}",
            f"Revenue: {cell_data.get('total_revenue', 0):,.0f} KRW",
            f"Cost: {cell_data.get('total_cost', 0):,.0f} KRW",
            f"Profit: {cell_data.get('gross_profit', 0):+,.0f} KRW",
            f"Margin: {cell_data.get('gross_profit_margin', 0):.1f}%",
        ]

        # Add status
        if cell_data.get('gross_profit', 0) > 0:
            summary_parts.append("Status: Profitable")
        elif cell_data.get('gross_profit', 0) < 0:
            summary_parts.append("Status: Loss")
        else:
            summary_parts.append("Status: Break-even")

        # Add performance indicator
        margin = cell_data.get('gross_profit_margin', 0)
        if margin >= 30:
            summary_parts.append("Performance: Above target (30%)")
        elif margin >= 20:
            summary_parts.append("Performance: Near target")
        else:
            summary_parts.append("Performance: Below target")

        return ". ".join(summary_parts) + "."

    def store_embedding(
        self,
        cell_id: str,
        report_date: date,
        financial_data: Dict[str, Any],
        embedding: Optional[List[float]] = None
    ):
        """
        Store embedding for a financial summary

        Args:
            cell_id: Cell identifier
            report_date: Date of the report
            financial_data: Financial data dictionary
            embedding: Pre-computed embedding (if None, will generate)
        """
        # Generate text summary
        summary_text = self.create_financial_summary_text(financial_data)

        # Generate embedding if not provided
        if embedding is None:
            embedding = self.generate_embedding(summary_text)

        # Store in database
        with self.Session() as session:
            import uuid

            embedding_id = str(uuid.uuid4())
            embedding_str = json.dumps(embedding)

            query = text("""
                INSERT INTO cell_embeddings
                (embedding_id, cell_id, report_date, embedding, source_type, source_text, created_at)
                VALUES (:embedding_id, :cell_id, :report_date, :embedding::vector, :source_type, :source_text, :created_at)
                ON CONFLICT (cell_id, report_date, source_type)
                DO UPDATE SET
                    embedding = EXCLUDED.embedding,
                    source_text = EXCLUDED.source_text
            """)

            session.execute(query, {
                'embedding_id': embedding_id,
                'cell_id': cell_id,
                'report_date': report_date,
                'embedding': embedding_str,
                'source_type': 'daily_report',
                'source_text': summary_text,
                'created_at': datetime.now()
            })
            session.commit()

        print(f"[OK] Stored embedding for {cell_id} on {report_date}")

    def find_similar_cells(
        self,
        cell_id: str,
        report_date: date,
        limit: int = 5,
        similarity_threshold: float = 0.8
    ) -> List[Dict[str, Any]]:
        """
        Find cells with similar financial patterns

        Args:
            cell_id: Cell to compare
            report_date: Date of the report to compare
            limit: Maximum number of similar cells to return
            similarity_threshold: Minimum similarity score (0-1)

        Returns:
            List of similar cells with similarity scores
        """
        with self.Session() as session:
            # Get embedding for reference cell
            query = text("""
                SELECT embedding
                FROM cell_embeddings
                WHERE cell_id = :cell_id AND report_date = :report_date
                LIMIT 1
            """)

            result = session.execute(query, {
                'cell_id': cell_id,
                'report_date': report_date
            }).fetchone()

            if not result:
                print(f"[WARNING] No embedding found for {cell_id} on {report_date}")
                return []

            # Find similar cells using cosine similarity
            similarity_query = text("""
                SELECT
                    ce.cell_id,
                    ce.report_date,
                    ce.source_text,
                    c.cell_name,
                    1 - (ce.embedding <=> :reference_embedding) AS similarity
                FROM cell_embeddings ce
                JOIN cells c ON ce.cell_id = c.cell_id
                WHERE ce.cell_id != :cell_id
                    AND 1 - (ce.embedding <=> :reference_embedding) >= :threshold
                ORDER BY ce.embedding <=> :reference_embedding
                LIMIT :limit
            """)

            reference_embedding = result[0]

            results = session.execute(similarity_query, {
                'reference_embedding': str(reference_embedding),
                'cell_id': cell_id,
                'threshold': similarity_threshold,
                'limit': limit
            }).fetchall()

            similar_cells = []
            for row in results:
                similar_cells.append({
                    'cell_id': row[0],
                    'report_date': row[1],
                    'source_text': row[2],
                    'cell_name': row[3],
                    'similarity_score': float(row[4])
                })

            return similar_cells

    def semantic_search(
        self,
        query_text: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Semantic search across all financial reports

        Args:
            query_text: Natural language query
            limit: Maximum number of results

        Returns:
            List of matching reports with relevance scores
        """
        # Generate embedding for query
        query_embedding = self.generate_embedding(query_text)

        with self.Session() as session:
            search_query = text("""
                SELECT
                    ce.cell_id,
                    ce.report_date,
                    ce.source_text,
                    c.cell_name,
                    1 - (ce.embedding <=> :query_embedding) AS relevance
                FROM cell_embeddings ce
                JOIN cells c ON ce.cell_id = c.cell_id
                ORDER BY ce.embedding <=> :query_embedding
                LIMIT :limit
            """)

            results = session.execute(search_query, {
                'query_embedding': json.dumps(query_embedding),
                'limit': limit
            }).fetchall()

            search_results = []
            for row in results:
                search_results.append({
                    'cell_id': row[0],
                    'report_date': row[1],
                    'source_text': row[2],
                    'cell_name': row[3],
                    'relevance_score': float(row[4])
                })

            return search_results

    def detect_anomalies(
        self,
        cell_id: str,
        days_back: int = 30,
        anomaly_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Detect anomalous financial patterns for a cell

        Args:
            cell_id: Cell to analyze
            days_back: Number of days to analyze
            anomaly_threshold: Similarity threshold (lower = more anomalous)

        Returns:
            List of anomalous reports
        """
        with self.Session() as session:
            # Get all embeddings for the cell in the time period
            query = text("""
                SELECT
                    ce1.report_date as date1,
                    ce2.report_date as date2,
                    ce1.source_text,
                    1 - (ce1.embedding <=> ce2.embedding) AS similarity
                FROM cell_embeddings ce1
                CROSS JOIN cell_embeddings ce2
                WHERE ce1.cell_id = :cell_id
                    AND ce2.cell_id = :cell_id
                    AND ce1.report_date > ce2.report_date
                    AND ce1.report_date >= CURRENT_DATE - INTERVAL ':days_back days'
                    AND 1 - (ce1.embedding <=> ce2.embedding) < :threshold
                ORDER BY ce1.report_date DESC
            """)

            results = session.execute(query, {
                'cell_id': cell_id,
                'days_back': days_back,
                'threshold': anomaly_threshold
            }).fetchall()

            anomalies = []
            for row in results:
                anomalies.append({
                    'date': row[0],
                    'compared_to': row[1],
                    'description': row[2],
                    'similarity': float(row[3]),
                    'anomaly_score': 1 - float(row[3])
                })

            return anomalies


# Example usage and demo
if __name__ == "__main__":
    print("=" * 60)
    print("NERDX pgvector Service - Demo")
    print("=" * 60)
    print()

    # Note: This requires a PostgreSQL database with pgvector extension
    # Set DATABASE_URL environment variable to test

    database_url = os.getenv('DATABASE_URL')

    if not database_url:
        print("[INFO] DATABASE_URL not set. Using mock demo mode.")
        print()
        print("To use with real PostgreSQL + pgvector:")
        print("1. Install pgvector: https://github.com/pgvector/pgvector")
        print("2. Set DATABASE_URL environment variable")
        print("3. Optionally set OPENAI_API_KEY for real embeddings")
        print()
        print("Mock demo capabilities:")
        print("- Generate deterministic embeddings (hash-based)")
        print("- Store/retrieve embeddings (requires PostgreSQL)")
        print("- Find similar cells (cosine similarity)")
        print("- Semantic search")
        print("- Anomaly detection")
    else:
        try:
            service = PgVectorService(database_url)
            service.ensure_pgvector_extension()

            # Example: Store embedding for a financial summary
            sample_data = {
                'cell_id': 'CELL-001',
                'cell_name': 'Product Development Team',
                'summary_date': date.today(),
                'total_revenue': 5000000,
                'total_cost': 3500000,
                'gross_profit': 1500000,
                'gross_profit_margin': 30.0
            }

            print("[DEMO] Storing embedding for sample data...")
            service.store_embedding(
                cell_id=sample_data['cell_id'],
                report_date=sample_data['summary_date'],
                financial_data=sample_data
            )

            print()
            print("[DEMO] Finding similar cells...")
            similar = service.find_similar_cells(
                cell_id=sample_data['cell_id'],
                report_date=sample_data['summary_date'],
                limit=5
            )

            for cell in similar:
                print(f"  - {cell['cell_name']} (similarity: {cell['similarity_score']:.2%})")

            print()
            print("[DEMO] Semantic search: 'profitable cells with high margin'...")
            results = service.semantic_search(
                query_text="profitable cells with high margin",
                limit=5
            )

            for result in results:
                print(f"  - {result['cell_name']} on {result['report_date']} (relevance: {result['relevance_score']:.2%})")

            print()
            print("=" * 60)
            print("pgvector Service Demo Complete!")
            print("=" * 60)

        except Exception as e:
            print(f"[ERROR] Demo failed: {e}")
            import traceback
            traceback.print_exc()
