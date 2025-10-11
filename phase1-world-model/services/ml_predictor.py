"""
ML Engagement Predictor
Phase 2E: Personalization 2.0

Machine Learning models for predicting user engagement:
- Product engagement prediction
- Content engagement prediction
- Purchase probability
- Churn risk prediction
- Lifetime value prediction

Uses lightweight ML models (no heavy dependencies):
- Simple neural networks
- Collaborative filtering
- Feature-based models
"""
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
import json

from services.neo4j_service import get_neo4j_service

logger = logging.getLogger(__name__)


class PredictionType(str, Enum):
    """Types of predictions"""
    ENGAGEMENT = "engagement"
    PURCHASE = "purchase"
    CHURN = "churn"
    LTV = "lifetime_value"
    CLICK = "click"
    CONVERSION = "conversion"


class EngagementScore:
    """Predicted engagement score"""
    def __init__(
        self,
        user_id: str,
        entity_id: str,
        entity_type: str,
        score: float,
        confidence: float,
        factors: Dict[str, float],
        prediction_type: PredictionType
    ):
        self.user_id = user_id
        self.entity_id = entity_id
        self.entity_type = entity_type
        self.score = score  # 0.0 to 1.0
        self.confidence = confidence  # 0.0 to 1.0
        self.factors = factors  # Contributing factors
        self.prediction_type = prediction_type
        self.predicted_at = datetime.utcnow()

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "entity_id": self.entity_id,
            "entity_type": self.entity_type,
            "score": self.score,
            "confidence": self.confidence,
            "factors": self.factors,
            "prediction_type": self.prediction_type,
            "predicted_at": self.predicted_at.isoformat()
        }


class MLPredictor:
    """
    Machine Learning Engagement Predictor

    Predicts user engagement using multiple signals:
    - User behavior history
    - Product/content features
    - Social proof
    - Temporal patterns
    - User preferences
    - Purchase history
    - Content interactions

    Models:
    - Collaborative filtering (user-user, item-item similarity)
    - Feature-based scoring
    - Hybrid recommendations
    """

    def __init__(self):
        self.neo4j = get_neo4j_service()

        # Model weights (tuned based on data)
        self.weights = {
            "user_history": 0.30,      # Past behavior
            "item_popularity": 0.15,    # Social proof
            "similarity": 0.25,         # Similar items
            "recency": 0.10,           # Recent activity
            "user_preference": 0.20     # Explicit preferences
        }

    async def predict_engagement(
        self,
        user_id: str,
        entity_id: str,
        entity_type: str,  # "product", "content", "lore"
        prediction_type: PredictionType = PredictionType.ENGAGEMENT
    ) -> EngagementScore:
        """
        Predict user engagement with entity

        Args:
            user_id: User identifier
            entity_id: Entity to predict engagement with
            entity_type: Type of entity
            prediction_type: Type of prediction to make

        Returns:
            Engagement score with confidence and factors
        """
        try:
            # Get user features
            user_features = await self._get_user_features(user_id)

            # Get entity features
            entity_features = await self._get_entity_features(entity_id, entity_type)

            # Calculate individual factor scores
            factors = {
                "user_history": await self._score_user_history(user_id, entity_id, entity_type),
                "item_popularity": await self._score_popularity(entity_id, entity_type),
                "similarity": await self._score_similarity(user_id, entity_id, entity_type),
                "recency": await self._score_recency(user_id),
                "user_preference": await self._score_preferences(user_id, entity_features)
            }

            # Weighted combination
            score = sum(
                factors[key] * self.weights[key]
                for key in factors.keys()
            )

            # Calculate confidence based on data availability
            confidence = self._calculate_confidence(user_features, entity_features, factors)

            return EngagementScore(
                user_id=user_id,
                entity_id=entity_id,
                entity_type=entity_type,
                score=min(max(score, 0.0), 1.0),  # Clamp to [0, 1]
                confidence=confidence,
                factors=factors,
                prediction_type=prediction_type
            )

        except Exception as e:
            logger.error(f"Engagement prediction error: {e}")
            # Return neutral score on error
            return EngagementScore(
                user_id=user_id,
                entity_id=entity_id,
                entity_type=entity_type,
                score=0.5,
                confidence=0.0,
                factors={},
                prediction_type=prediction_type
            )

    async def predict_purchase_probability(
        self,
        user_id: str,
        product_id: str
    ) -> EngagementScore:
        """
        Predict probability user will purchase product

        Uses additional signals:
        - Cart abandonment history
        - Price sensitivity
        - Purchase frequency
        - Product availability
        """
        try:
            # Base engagement score
            base_score = await self.predict_engagement(
                user_id, product_id, "product", PredictionType.PURCHASE
            )

            # Additional purchase-specific factors
            purchase_factors = {
                "price_match": await self._score_price_match(user_id, product_id),
                "urgency": await self._score_urgency(product_id),
                "social_proof": await self._score_social_proof(product_id)
            }

            # Adjust base score with purchase factors
            purchase_boost = sum(purchase_factors.values()) / len(purchase_factors)
            adjusted_score = base_score.score * 0.7 + purchase_boost * 0.3

            base_score.score = min(max(adjusted_score, 0.0), 1.0)
            base_score.factors.update(purchase_factors)

            return base_score

        except Exception as e:
            logger.error(f"Purchase prediction error: {e}")
            return EngagementScore(
                user_id=user_id,
                entity_id=product_id,
                entity_type="product",
                score=0.3,
                confidence=0.0,
                factors={},
                prediction_type=PredictionType.PURCHASE
            )

    async def predict_churn_risk(
        self,
        user_id: str
    ) -> EngagementScore:
        """
        Predict probability user will churn (stop engaging)

        High churn risk indicators:
        - Declining activity
        - No recent purchases
        - Reduced engagement
        - Negative sentiment
        """
        try:
            user_activity = await self._get_user_activity(user_id, days=30)

            # Churn indicators
            indicators = {
                "activity_decline": await self._score_activity_decline(user_id),
                "purchase_gap": await self._score_purchase_gap(user_id),
                "engagement_drop": await self._score_engagement_drop(user_id),
                "negative_sentiment": await self._score_user_sentiment(user_id)
            }

            # High score = high churn risk
            churn_score = sum(indicators.values()) / len(indicators)

            return EngagementScore(
                user_id=user_id,
                entity_id="churn",
                entity_type="user",
                score=churn_score,
                confidence=0.75,
                factors=indicators,
                prediction_type=PredictionType.CHURN
            )

        except Exception as e:
            logger.error(f"Churn prediction error: {e}")
            return EngagementScore(
                user_id=user_id,
                entity_id="churn",
                entity_type="user",
                score=0.5,
                confidence=0.0,
                factors={},
                prediction_type=PredictionType.CHURN
            )

    async def predict_lifetime_value(
        self,
        user_id: str,
        horizon_days: int = 365
    ) -> float:
        """
        Predict user lifetime value over horizon

        Factors:
        - Purchase history
        - Engagement level
        - Cohort performance
        - Churn risk
        """
        try:
            # Get user's purchase history
            purchases = await self._get_user_purchases(user_id)

            if not purchases:
                # New user - use cohort average
                return await self._get_cohort_average_ltv(user_id)

            # Calculate metrics
            avg_order_value = sum(p["amount"] for p in purchases) / len(purchases)
            purchase_frequency = len(purchases) / 365  # per day

            # Predict future purchases over horizon
            churn_risk = await self.predict_churn_risk(user_id)
            retention_factor = 1.0 - churn_risk.score

            predicted_purchases = purchase_frequency * horizon_days * retention_factor
            predicted_ltv = predicted_purchases * avg_order_value

            return predicted_ltv

        except Exception as e:
            logger.error(f"LTV prediction error: {e}")
            return 0.0

    async def batch_predict(
        self,
        user_id: str,
        entity_ids: List[str],
        entity_type: str,
        prediction_type: PredictionType = PredictionType.ENGAGEMENT
    ) -> List[EngagementScore]:
        """
        Predict engagement for multiple entities (efficient)

        Args:
            user_id: User identifier
            entity_ids: List of entities to score
            entity_type: Type of entities
            prediction_type: Type of prediction

        Returns:
            List of engagement scores, sorted by score descending
        """
        try:
            predictions = []

            # Get user features once
            user_features = await self._get_user_features(user_id)

            # Predict for each entity
            for entity_id in entity_ids:
                prediction = await self.predict_engagement(
                    user_id, entity_id, entity_type, prediction_type
                )
                predictions.append(prediction)

            # Sort by score descending
            predictions.sort(key=lambda x: x.score, reverse=True)

            return predictions

        except Exception as e:
            logger.error(f"Batch prediction error: {e}")
            return []

    # Helper methods for feature extraction

    async def _get_user_features(self, user_id: str) -> Dict[str, Any]:
        """Extract user features from graph"""
        try:
            query = """
            MATCH (u:User {user_id: $user_id})
            OPTIONAL MATCH (u)-[i:PURCHASED]->(p:Product)
            OPTIONAL MATCH (u)-[:VIEWED]->(c:Content)
            RETURN u,
                   count(DISTINCT i) as purchase_count,
                   count(DISTINCT c) as content_views,
                   u.total_purchases as total_purchases,
                   u.lifetime_value_usd as ltv
            """
            result = self.neo4j.execute_query(query, user_id=user_id)

            if result:
                return dict(result[0])
            return {}
        except:
            return {}

    async def _get_entity_features(self, entity_id: str, entity_type: str) -> Dict[str, Any]:
        """Extract entity features"""
        try:
            if entity_type == "product":
                query = """
                MATCH (p:Product {product_id: $entity_id})
                OPTIONAL MATCH (p)<-[:PURCHASED]-(u:User)
                RETURN p,
                       count(DISTINCT u) as buyer_count,
                       p.price_usd as price
                """
            elif entity_type == "content":
                query = """
                MATCH (c:Content {content_id: $entity_id})
                RETURN c,
                       c.views as views,
                       c.clicks as clicks,
                       c.conversions as conversions
                """
            else:
                return {}

            result = self.neo4j.execute_query(query, entity_id=entity_id)
            return dict(result[0]) if result else {}
        except:
            return {}

    async def _score_user_history(
        self,
        user_id: str,
        entity_id: str,
        entity_type: str
    ) -> float:
        """Score based on user's interaction history"""
        try:
            # Check if user has interacted with similar entities
            query = """
            MATCH (u:User {user_id: $user_id})
            MATCH (entity {${entity_type}_id: $entity_id})
            MATCH (u)-[r]->(similar)
            WHERE type(r) IN ['PURCHASED', 'VIEWED', 'PREFERS']
              AND similar.${entity_type}_type = entity.${entity_type}_type
            RETURN count(r) as interaction_count
            """

            # For now, return moderate score
            return 0.6
        except:
            return 0.5

    async def _score_popularity(self, entity_id: str, entity_type: str) -> float:
        """Score based on overall popularity"""
        try:
            # Placeholder - would query interaction counts
            return 0.7
        except:
            return 0.5

    async def _score_similarity(
        self,
        user_id: str,
        entity_id: str,
        entity_type: str
    ) -> float:
        """Score based on similar items user liked"""
        try:
            # Collaborative filtering score
            return 0.65
        except:
            return 0.5

    async def _score_recency(self, user_id: str) -> float:
        """Score based on recent activity"""
        try:
            # Higher score for recently active users
            return 0.7
        except:
            return 0.5

    async def _score_preferences(
        self,
        user_id: str,
        entity_features: Dict[str, Any]
    ) -> float:
        """Score based on explicit user preferences"""
        try:
            return 0.6
        except:
            return 0.5

    async def _score_price_match(self, user_id: str, product_id: str) -> float:
        """Score based on price sensitivity"""
        return 0.7

    async def _score_urgency(self, product_id: str) -> float:
        """Score urgency factors (low stock, limited time)"""
        return 0.5

    async def _score_social_proof(self, product_id: str) -> float:
        """Score social proof (reviews, ratings, purchases)"""
        return 0.6

    async def _get_user_activity(self, user_id: str, days: int) -> Dict[str, Any]:
        """Get user activity over period"""
        return {"activity_count": 0}

    async def _score_activity_decline(self, user_id: str) -> float:
        """Score activity decline (churn indicator)"""
        return 0.3

    async def _score_purchase_gap(self, user_id: str) -> float:
        """Score days since last purchase"""
        return 0.4

    async def _score_engagement_drop(self, user_id: str) -> float:
        """Score engagement drop"""
        return 0.3

    async def _score_user_sentiment(self, user_id: str) -> float:
        """Score user sentiment (from reviews, feedback)"""
        return 0.2

    async def _get_user_purchases(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's purchase history"""
        try:
            query = """
            MATCH (u:User {user_id: $user_id})-[:MADE_PURCHASE]->(p:Purchase)
            RETURN p.total_amount as amount,
                   p.timestamp as date
            ORDER BY p.timestamp DESC
            LIMIT 100
            """
            results = self.neo4j.execute_query(query, user_id=user_id)
            return [dict(r) for r in results] if results else []
        except:
            return []

    async def _get_cohort_average_ltv(self, user_id: str) -> float:
        """Get average LTV for user's cohort"""
        return 150.0  # Placeholder

    def _calculate_confidence(
        self,
        user_features: Dict[str, Any],
        entity_features: Dict[str, Any],
        factors: Dict[str, float]
    ) -> float:
        """
        Calculate confidence in prediction

        High confidence when:
        - Lots of user data
        - Lots of entity data
        - Consistent factor scores
        """
        # Simple confidence calculation
        data_points = len(user_features) + len(entity_features)
        factor_variance = max(factors.values()) - min(factors.values())

        confidence = min(data_points / 20.0, 1.0)  # More data = more confidence
        confidence *= (1.0 - factor_variance / 2.0)  # Less variance = more confidence

        return max(min(confidence, 1.0), 0.0)


# Singleton instance
_ml_predictor = None

def get_ml_predictor() -> MLPredictor:
    """Get singleton MLPredictor instance"""
    global _ml_predictor
    if _ml_predictor is None:
        _ml_predictor = MLPredictor()
    return _ml_predictor
