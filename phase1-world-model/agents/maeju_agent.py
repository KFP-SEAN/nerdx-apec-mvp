"""
Maeju - Storytelling AI Agent

Maeju is the AI storyteller that helps users discover NERD products
through engaging conversations about Korean culture, traditions, and flavors.
"""
from openai import OpenAI
from typing import List, Dict, Any, Optional
from config import settings
import logging
import json

logger = logging.getLogger(__name__)


class MaejuAgent:
    """Maeju AI Storytelling Agent"""

    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
        self.system_prompt = self._build_system_prompt()

    def _build_system_prompt(self) -> str:
        """Build Maeju's personality and instructions"""
        return """You are Maeju (매주), an AI storytelling agent for NERDX, a Korean craft alcohol brand.

Your Role:
- Guide users through discovering Korean craft alcohol traditions
- Share engaging stories about ingredients, brewing methods, and cultural heritage
- Make personalized product recommendations based on user preferences
- Be warm, knowledgeable, and culturally respectful

Your Knowledge:
- Korean fermentation traditions (makgeolli, soju, brewing techniques)
- Regional ingredients and their origins
- Cultural stories and historical context
- NERD product portfolio and their unique characteristics

Communication Style:
- Friendly and approachable, like a knowledgeable friend
- Use storytelling to make information memorable
- Ask questions to understand user preferences
- Provide specific product recommendations when appropriate
- Use Korean terms with English explanations
- Be concise but engaging (2-3 paragraphs max)

When recommending products:
- Consider user's taste preferences (sweet, dry, fruity, etc.)
- Explain WHY you're recommending each product
- Share a brief story or interesting fact about the product
- Mention ingredients and their significance

Guidelines:
- Never be pushy or sales-y
- Respect cultural heritage authentically
- If you don't know something, be honest
- Ask follow-up questions to refine recommendations
- Keep responses between 100-200 words unless user asks for more detail

Available Information:
You have access to:
- Product database (names, ingredients, flavor profiles, prices)
- Cultural lore and stories
- User's past interactions and preferences
- Regional information about Korean alcohol traditions
"""

    async def chat(
        self,
        user_message: str,
        user_id: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        user_context: Optional[Dict[str, Any]] = None,
        available_products: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Process user message and generate response

        Args:
            user_message: User's input message
            user_id: User identifier
            conversation_history: Previous messages in conversation
            user_context: User preferences and profile
            available_products: Relevant products for context

        Returns:
            Response dict with message and recommendations
        """
        try:
            # Build context
            context_prompt = self._build_context_prompt(
                user_context, available_products
            )

            # Prepare messages
            messages = [
                {"role": "system", "content": self.system_prompt},
            ]

            if context_prompt:
                messages.append({"role": "system", "content": context_prompt})

            # Add conversation history
            if conversation_history:
                messages.extend(conversation_history[-6:])  # Last 3 exchanges

            # Add current message
            messages.append({"role": "user", "content": user_message})

            # Call OpenAI
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=settings.openai_temperature,
                max_tokens=settings.openai_max_tokens,
                functions=[self._get_recommendation_function()],
                function_call="auto"
            )

            choice = response.choices[0]
            assistant_message = choice.message

            # Check if function was called
            product_recommendations = []
            if assistant_message.function_call:
                function_args = json.loads(assistant_message.function_call.arguments)
                product_recommendations = function_args.get("product_ids", [])

            return {
                "message": assistant_message.content or "",
                "product_recommendations": product_recommendations,
                "conversation_id": f"{user_id}_{response.id}",
                "model_used": response.model,
                "tokens_used": response.usage.total_tokens
            }

        except Exception as e:
            logger.error(f"Maeju chat error: {e}")
            return {
                "message": "안녕하세요! I'm having a momentary hiccup. Could you try asking again?",
                "product_recommendations": [],
                "error": str(e)
            }

    def _build_context_prompt(
        self,
        user_context: Optional[Dict[str, Any]],
        available_products: Optional[List[Dict[str, Any]]]
    ) -> str:
        """Build context information for the AI"""
        context_parts = []

        if user_context:
            context_parts.append("User Context:")
            if user_context.get("taste_preferences"):
                prefs = user_context["taste_preferences"]
                context_parts.append(f"- Taste preferences: {json.dumps(prefs)}")
            if user_context.get("membership_tier"):
                context_parts.append(f"- Membership: {user_context['membership_tier']}")
            if user_context.get("total_purchases", 0) > 0:
                context_parts.append(f"- Previous purchases: {user_context['total_purchases']}")

        if available_products:
            context_parts.append("\nAvailable Products:")
            for product in available_products[:10]:  # Limit to 10
                product_info = f"- {product.get('name', 'Unknown')}"
                if product.get('product_type'):
                    product_info += f" ({product['product_type']})"
                if product.get('flavor_profile'):
                    product_info += f" - {product['flavor_profile']}"
                if product.get('price_usd'):
                    product_info += f" - ${product['price_usd']}"
                context_parts.append(product_info)

        return "\n".join(context_parts) if context_parts else ""

    def _get_recommendation_function(self) -> Dict[str, Any]:
        """Define function for product recommendations"""
        return {
            "name": "recommend_products",
            "description": "Recommend specific NERD products to the user based on their preferences",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of product IDs to recommend (1-3 products)"
                    },
                    "reason": {
                        "type": "string",
                        "description": "Brief explanation of why these products match user's preferences"
                    }
                },
                "required": ["product_ids", "reason"]
            }
        }

    def generate_product_story(
        self,
        product: Dict[str, Any],
        style: str = "engaging"
    ) -> str:
        """
        Generate a story about a specific product

        Args:
            product: Product information
            style: Story style (engaging, educational, poetic)

        Returns:
            Generated story text
        """
        try:
            prompt = f"""Generate a {style} story (100-150 words) about this Korean craft alcohol:

Product: {product.get('name', 'Unknown')}
Type: {product.get('product_type', 'Unknown')}
Description: {product.get('description', '')}
Ingredients: {json.dumps(product.get('ingredients', []))}

The story should:
- Highlight cultural significance
- Mention unique ingredients and their origins
- Create emotional connection
- End with what makes this product special

Style: {style}
"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=300
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Story generation error: {e}")
            return f"This is a special {product.get('product_type', 'Korean craft alcohol')} with a rich heritage."

    def analyze_taste_preferences(
        self,
        user_input: str
    ) -> Dict[str, Any]:
        """
        Analyze user's taste preferences from their description

        Args:
            user_input: User's description of what they like

        Returns:
            Structured taste preferences
        """
        try:
            prompt = f"""Analyze this user's taste preferences and extract structured data:

User input: "{user_input}"

Extract:
1. Sweetness preference (1-5: 1=very dry, 5=very sweet)
2. Body preference (light, medium, full)
3. Flavors they like (list of keywords)
4. Flavors they dislike (list of keywords)
5. Experience level (beginner, intermediate, expert)
6. Preferred alcohol content (low<7%, medium 7-14%, high >14%)

Return as JSON.
"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a taste preference analyzer. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=300,
                response_format={"type": "json_object"}
            )

            return json.loads(response.choices[0].message.content)

        except Exception as e:
            logger.error(f"Taste analysis error: {e}")
            return {
                "sweetness": 3,
                "body": "medium",
                "liked_flavors": [],
                "disliked_flavors": [],
                "experience_level": "beginner",
                "preferred_abv": "medium"
            }


# Singleton instance
_maeju_agent: Optional[MaejuAgent] = None


def get_maeju_agent() -> MaejuAgent:
    """Get Maeju agent singleton"""
    global _maeju_agent
    if _maeju_agent is None:
        _maeju_agent = MaejuAgent()
    return _maeju_agent
