"""
Sentiment Analyzer Service for UGC (User Generated Content)
Phase 2C: Analytical Core

Analyzes sentiment from:
- Product reviews
- Social media comments
- Chat messages
- UGC content (CAMEO videos, etc.)

Uses Gemini for multi-lingual sentiment analysis (Korean, English, Chinese, Japanese)
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from enum import Enum

from agents.gemini_agent import GeminiAgent
from services.neo4j_service import get_neo4j_service

logger = logging.getLogger(__name__)


class SentimentLabel(str, Enum):
    """Sentiment classification labels"""
    VERY_POSITIVE = "very_positive"
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    VERY_NEGATIVE = "very_negative"


class SentimentScore:
    """Sentiment analysis result"""
    def __init__(
        self,
        label: SentimentLabel,
        score: float,
        confidence: float,
        emotions: Dict[str, float] = None,
        key_phrases: List[str] = None,
        language: str = "en"
    ):
        self.label = label
        self.score = score  # -1.0 (very negative) to 1.0 (very positive)
        self.confidence = confidence  # 0.0 to 1.0
        self.emotions = emotions or {}  # {"joy": 0.8, "surprise": 0.3, ...}
        self.key_phrases = key_phrases or []
        self.language = language
        self.timestamp = datetime.utcnow()

    def to_dict(self):
        return {
            "label": self.label,
            "score": self.score,
            "confidence": self.confidence,
            "emotions": self.emotions,
            "key_phrases": self.key_phrases,
            "language": self.language,
            "timestamp": self.timestamp.isoformat()
        }


class SentimentAnalyzer:
    """
    Sentiment Analyzer using Gemini for multi-lingual analysis

    Key Features:
    - Multi-lingual support (Korean, English, Chinese, Japanese)
    - Emotion detection (joy, anger, surprise, etc.)
    - Key phrase extraction
    - Trend analysis over time
    - Product-specific sentiment aggregation
    """

    def __init__(self):
        self.gemini = GeminiAgent()
        self.neo4j = get_neo4j_service()

        # Sentiment analysis prompt template
        self.analysis_prompt = """
Analyze the sentiment of the following text and provide a detailed analysis.

Text: {text}

Please provide:
1. Overall sentiment label: very_positive, positive, neutral, negative, or very_negative
2. Sentiment score: A number from -1.0 (very negative) to 1.0 (very positive)
3. Confidence: How confident are you in this analysis? (0.0 to 1.0)
4. Emotions: Detect specific emotions with their intensity (0.0 to 1.0):
   - joy, sadness, anger, fear, surprise, disgust, trust, anticipation
5. Key phrases: Extract 3-5 key phrases that represent the main points
6. Language: Detected language (ko, en, zh, ja)

Return JSON format:
{{
  "label": "positive",
  "score": 0.7,
  "confidence": 0.85,
  "emotions": {{
    "joy": 0.8,
    "trust": 0.6,
    "anticipation": 0.4
  }},
  "key_phrases": ["amazing taste", "would buy again", "perfect for summer"],
  "language": "en"
}}
"""

    async def analyze_text(
        self,
        text: str,
        context: Optional[Dict[str, Any]] = None
    ) -> SentimentScore:
        """
        Analyze sentiment of a single text

        Args:
            text: Text to analyze
            context: Optional context (product_id, user_id, etc.)

        Returns:
            SentimentScore object
        """
        try:
            # Add context to prompt if provided
            prompt = self.analysis_prompt.format(text=text)
            if context:
                prompt += f"\n\nContext: {context}"

            # Use Gemini for analysis
            result = await self.gemini.generate(
                prompt=prompt,
                temperature=0.3  # Lower temperature for consistent analysis
            )

            # Parse response (expecting JSON)
            import json
            # Extract JSON from markdown code block if present
            response_text = result.get("text", "")
            if "```json" in response_text:
                json_str = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                json_str = response_text.split("```")[1].split("```")[0].strip()
            else:
                json_str = response_text

            data = json.loads(json_str)

            # Create SentimentScore
            sentiment = SentimentScore(
                label=SentimentLabel(data["label"]),
                score=data["score"],
                confidence=data["confidence"],
                emotions=data.get("emotions", {}),
                key_phrases=data.get("key_phrases", []),
                language=data.get("language", "en")
            )

            logger.info(f"Sentiment analyzed: {sentiment.label} (score: {sentiment.score})")
            return sentiment

        except Exception as e:
            logger.error(f"Sentiment analysis error: {e}")
            # Return neutral sentiment on error
            return SentimentScore(
                label=SentimentLabel.NEUTRAL,
                score=0.0,
                confidence=0.0
            )

    async def analyze_batch(
        self,
        texts: List[str],
        context: Optional[Dict[str, Any]] = None
    ) -> List[SentimentScore]:
        """
        Analyze sentiment of multiple texts

        Args:
            texts: List of texts to analyze
            context: Optional shared context

        Returns:
            List of SentimentScore objects
        """
        results = []
        for text in texts:
            sentiment = await self.analyze_text(text, context)
            results.append(sentiment)

        return results

    async def analyze_product_sentiment(
        self,
        product_id: str,
        days_back: int = 30,
        min_samples: int = 5
    ) -> Dict[str, Any]:
        """
        Aggregate sentiment analysis for a product

        Analyzes:
        - Product reviews
        - Comments mentioning the product
        - Chat messages about the product

        Args:
            product_id: Product identifier
            days_back: Look back N days
            min_samples: Minimum samples for reliable analysis

        Returns:
            Aggregated sentiment report
        """
        try:
            # Query Neo4j for all UGC related to product
            since = datetime.utcnow() - timedelta(days=days_back)

            # This is a placeholder - in production you'd query actual UGC
            # For now, we'll simulate with interaction data
            query = """
            MATCH (p:Product {product_id: $product_id})
            MATCH (u:User)-[i:PURCHASED]->(p)
            WHERE i.timestamp > $since
            RETURN count(i) as interaction_count
            """

            result = self.neo4j.execute_query(
                query,
                product_id=product_id,
                since=since
            )

            # In production, you'd analyze actual UGC texts here
            # For now, return structure
            return {
                "product_id": product_id,
                "period_days": days_back,
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "sample_count": result[0]["interaction_count"] if result else 0,
                "overall_sentiment": {
                    "label": "positive",
                    "score": 0.0,
                    "confidence": 0.0
                },
                "sentiment_distribution": {
                    "very_positive": 0,
                    "positive": 0,
                    "neutral": 0,
                    "negative": 0,
                    "very_negative": 0
                },
                "top_emotions": {},
                "key_themes": [],
                "trend": "stable"  # increasing, decreasing, stable
            }

        except Exception as e:
            logger.error(f"Product sentiment analysis error: {e}")
            return {
                "product_id": product_id,
                "error": str(e)
            }

    async def detect_sentiment_shift(
        self,
        entity_type: str,
        entity_id: str,
        threshold: float = 0.3
    ) -> Optional[Dict[str, Any]]:
        """
        Detect significant sentiment shifts

        Compares recent sentiment vs historical baseline
        Useful for:
        - Product quality issues
        - PR crises
        - Viral positive feedback

        Args:
            entity_type: "product", "creator", "brand"
            entity_id: Entity identifier
            threshold: Alert threshold (e.g., 0.3 = 30% shift)

        Returns:
            Alert data if shift detected, None otherwise
        """
        try:
            # Compare last 7 days vs previous 30 days
            recent_sentiment = await self._get_average_sentiment(
                entity_type, entity_id, days_back=7
            )
            baseline_sentiment = await self._get_average_sentiment(
                entity_type, entity_id, days_back=30, skip_days=7
            )

            if recent_sentiment and baseline_sentiment:
                shift = recent_sentiment["score"] - baseline_sentiment["score"]

                if abs(shift) >= threshold:
                    return {
                        "entity_type": entity_type,
                        "entity_id": entity_id,
                        "shift_magnitude": shift,
                        "direction": "positive" if shift > 0 else "negative",
                        "recent_sentiment": recent_sentiment,
                        "baseline_sentiment": baseline_sentiment,
                        "alert_level": "critical" if abs(shift) >= 0.5 else "warning",
                        "detected_at": datetime.utcnow().isoformat()
                    }

            return None

        except Exception as e:
            logger.error(f"Sentiment shift detection error: {e}")
            return None

    async def _get_average_sentiment(
        self,
        entity_type: str,
        entity_id: str,
        days_back: int = 30,
        skip_days: int = 0
    ) -> Optional[Dict[str, float]]:
        """
        Get average sentiment for entity over time period

        Args:
            entity_type: Type of entity
            entity_id: Entity ID
            days_back: Days to look back
            skip_days: Skip N most recent days

        Returns:
            Average sentiment scores
        """
        # Placeholder - in production, query actual sentiment data
        return {
            "score": 0.0,
            "confidence": 0.0,
            "sample_count": 0
        }

    async def get_trending_topics(
        self,
        days_back: int = 7,
        min_mentions: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Extract trending topics from UGC

        Args:
            days_back: Look back N days
            min_mentions: Minimum mentions to be considered trending

        Returns:
            List of trending topics with sentiment
        """
        # Placeholder for trending topics extraction
        # In production, this would analyze all UGC and extract topics
        return []


# Singleton instance
_sentiment_analyzer = None

def get_sentiment_analyzer() -> SentimentAnalyzer:
    """Get singleton SentimentAnalyzer instance"""
    global _sentiment_analyzer
    if _sentiment_analyzer is None:
        _sentiment_analyzer = SentimentAnalyzer()
    return _sentiment_analyzer
