"""
Gemini Agent - Creative and rapid prototyping

Gemini excels at:
- Fast code generation (40% faster)
- Creative content generation
- Large context processing (1M+ tokens)
- Rapid prototyping
- Data analysis with big contexts

Use for: Content creation, prototyping, data analysis, creative tools
"""
import google.generativeai as genai
from typing import List, Dict, Any, Optional, Literal
from config import settings
import logging
import json

logger = logging.getLogger(__name__)


class GeminiAgent:
    """Gemini AI Agent for creative, rapid tasks"""

    def __init__(self, model: Optional[str] = None):
        """
        Initialize Gemini agent

        Args:
            model: Gemini model to use (defaults to settings)
        """
        if not settings.google_api_key:
            raise ValueError("GOOGLE_API_KEY not configured")

        genai.configure(api_key=settings.google_api_key)
        self.model_name = model or settings.gemini_model
        self.model = genai.GenerativeModel(self.model_name)
        logger.info(f"Initialized Gemini agent with model: {self.model_name}")

    async def generate(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        max_tokens: int = 8192,
        temperature: float = 0.7,
        response_format: Literal["text", "json"] = "text"
    ) -> Dict[str, Any]:
        """
        Generate response from Gemini

        Args:
            prompt: User prompt
            system_instruction: System instructions
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0-2.0)
            response_format: Output format

        Returns:
            Response dict with content, usage, model info
        """
        try:
            # Add JSON formatting instruction if needed
            if response_format == "json":
                if system_instruction:
                    system_instruction += "\n\nIMPORTANT: Respond only with valid JSON. No markdown, no explanations outside JSON."
                else:
                    system_instruction = "Respond only with valid JSON. No markdown, no explanations outside JSON."
                prompt += "\n\nReturn your response as valid JSON only."

            # Create model with system instruction if provided
            if system_instruction:
                model = genai.GenerativeModel(
                    self.model_name,
                    system_instruction=system_instruction
                )
            else:
                model = self.model

            # Configure generation
            generation_config = genai.GenerationConfig(
                max_output_tokens=max_tokens,
                temperature=temperature,
            )

            # Generate
            response = model.generate_content(
                prompt,
                generation_config=generation_config
            )

            # Extract content
            content = response.text

            # Parse JSON if requested
            if response_format == "json":
                try:
                    # Clean up markdown code blocks if present
                    if "```json" in content:
                        content = content.split("```json")[1].split("```")[0].strip()
                    elif "```" in content:
                        content = content.split("```")[1].split("```")[0].strip()

                    parsed_content = json.loads(content)
                    content = parsed_content
                except json.JSONDecodeError as e:
                    logger.error(f"Gemini returned invalid JSON: {content}")
                    raise ValueError(f"Invalid JSON from Gemini: {e}")

            # Extract usage info
            try:
                usage = {
                    "input_tokens": response.usage_metadata.prompt_token_count,
                    "output_tokens": response.usage_metadata.candidates_token_count,
                    "total_tokens": response.usage_metadata.total_token_count
                }
            except Exception:
                usage = {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}

            return {
                "content": content,
                "model": self.model_name,
                "usage": usage,
                "agent": "gemini"
            }

        except Exception as e:
            logger.error(f"Gemini generation error: {e}")
            raise

    async def generate_video_script(
        self,
        product: Dict[str, Any],
        duration_seconds: int = 60,
        target_audience: str = "general",
        style: str = "engaging"
    ) -> Dict[str, Any]:
        """
        Generate video script for content creators

        Gemini is excellent at creative content generation

        Args:
            product: Product information
            duration_seconds: Target video duration
            target_audience: Target audience description
            style: Video style (engaging, educational, entertaining)

        Returns:
            Structured video script
        """
        system_instruction = f"""You are a creative content strategist specializing in {style} video scripts for social media.
Create scripts that:
- Hook viewers in first 3 seconds
- Tell compelling stories
- Include clear calls-to-action
- Match platform best practices (TikTok, Instagram Reels, YouTube Shorts)
"""

        prompt = f"""Create a {duration_seconds}-second video script for this product:

Product: {product.get('name', 'Unknown')}
Type: {product.get('product_type', 'Korean craft alcohol')}
Description: {product.get('description', '')}
Key Features: {json.dumps(product.get('features', []))}

Target Audience: {target_audience}
Style: {style}

Return as JSON:
{{
    "title": "catchy title",
    "hook": "first 3 seconds (text + visual suggestion)",
    "scenes": [
        {{
            "timestamp": "0:00-0:03",
            "narration": "what to say",
            "visual": "what to show",
            "text_overlay": "on-screen text (optional)"
        }}
    ],
    "cta": "call to action",
    "hashtags": ["tag1", "tag2"],
    "music_suggestion": "music mood/genre",
    "estimated_duration": {duration_seconds}
}}
"""

        response = await self.generate(
            prompt=prompt,
            system_instruction=system_instruction,
            temperature=0.9,  # High for creativity
            response_format="json"
        )

        return response["content"]

    async def variate_recipe(
        self,
        base_recipe: Dict[str, Any],
        variations_count: int = 3,
        dietary_restrictions: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate recipe variations

        Gemini excels at creative culinary variations

        Args:
            base_recipe: Original recipe
            variations_count: Number of variations to generate
            dietary_restrictions: Dietary constraints (vegan, gluten-free, etc.)

        Returns:
            Recipe variations
        """
        system_instruction = """You are a creative chef specializing in Korean cuisine and craft alcohol pairings.
Generate authentic, creative variations that:
- Respect traditional techniques
- Offer interesting twists
- Consider ingredient availability
- Maintain cultural authenticity
"""

        restrictions_text = ""
        if dietary_restrictions:
            restrictions_text = f"\nDietary restrictions to accommodate: {', '.join(dietary_restrictions)}"

        prompt = f"""Create {variations_count} variations of this recipe:

Base Recipe:
{json.dumps(base_recipe, indent=2)}
{restrictions_text}

Return as JSON:
{{
    "variations": [
        {{
            "variation_name": "name",
            "theme": "what makes this unique",
            "ingredients": [
                {{
                    "item": "ingredient",
                    "amount": "quantity",
                    "substitution_from": "original ingredient (if substituted)"
                }}
            ],
            "instructions": ["step1", "step2"],
            "flavor_profile": "how it tastes different",
            "difficulty_change": "easier|same|harder"
        }}
    ]
}}
"""

        response = await self.generate(
            prompt=prompt,
            system_instruction=system_instruction,
            temperature=0.8,
            response_format="json"
        )

        return response["content"]

    async def generate_product_descriptions(
        self,
        product: Dict[str, Any],
        variants: List[str] = ["short", "long", "seo"],
        languages: List[str] = ["en"]
    ) -> Dict[str, Any]:
        """
        Generate multiple product description variants

        Gemini is fast at generating many variations

        Args:
            product: Product information
            variants: Types of descriptions (short, long, seo, social)
            languages: Languages to generate (en, ko, ja, zh)

        Returns:
            Multiple description variants
        """
        system_instruction = """You are a skilled copywriter specializing in premium alcohol brands.
Write descriptions that:
- Evoke sensory experiences
- Highlight craftsmanship
- Create emotional connections
- Are SEO-optimized when needed
- Respect cultural heritage
"""

        prompt = f"""Generate product descriptions for:

Product: {json.dumps(product, indent=2)}

Variants needed: {', '.join(variants)}
Languages: {', '.join(languages)}

Return as JSON:
{{
    "descriptions": {{
        "variant_type": {{
            "language_code": "description text"
        }}
    }}
}}

Example:
{{
    "descriptions": {{
        "short": {{
            "en": "45-character product tagline",
            "ko": "Korean tagline"
        }},
        "long": {{
            "en": "Full 2-3 paragraph description",
            "ko": "Korean full description"
        }},
        "seo": {{
            "en": "SEO-optimized 155-character meta description"
        }}
    }}
}}
"""

        response = await self.generate(
            prompt=prompt,
            system_instruction=system_instruction,
            temperature=0.7,
            response_format="json"
        )

        return response["content"]

    async def atomize_content(
        self,
        pillar_content: str,
        content_type: str = "blog_post",
        output_formats: List[str] = ["short_video", "carousel", "social_post"]
    ) -> Dict[str, Any]:
        """
        "Turkey Slice" - Atomize long-form content into derivative formats

        Gemini's large context window excels at this

        Args:
            pillar_content: Original long-form content
            content_type: Type of pillar content
            output_formats: Desired output formats

        Returns:
            Atomized content in multiple formats
        """
        system_instruction = """You are a content strategist specializing in "content atomization" -
taking one piece of pillar content and creating multiple derivative pieces optimized for different platforms.

For each format:
- Maintain key message and brand voice
- Optimize for platform (TikTok, Instagram, Twitter, etc.)
- Include hooks and CTAs
- Suggest visual elements
"""

        prompt = f"""Atomize this {content_type} into {len(output_formats)} formats:

Pillar Content:
{pillar_content}

Desired Output Formats: {', '.join(output_formats)}

Return as JSON:
{{
    "format_name": {{
        "content": "adapted content",
        "platform": "best platform for this",
        "hook": "attention grabber",
        "cta": "call to action",
        "visual_suggestions": ["visual1", "visual2"],
        "hashtags": ["tag1", "tag2"],
        "estimated_engagement": "high|medium|low",
        "best_posting_time": "time suggestion"
    }}
}}
"""

        response = await self.generate(
            prompt=prompt,
            system_instruction=system_instruction,
            temperature=0.75,
            max_tokens=16000,  # Larger for comprehensive atomization
            response_format="json"
        )

        return response["content"]

    async def analyze_data_patterns(
        self,
        data: Dict[str, Any],
        analysis_type: str = "general"
    ) -> Dict[str, Any]:
        """
        Analyze large datasets with Gemini's large context window

        Gemini can process 1M+ tokens for comprehensive analysis

        Args:
            data: Data to analyze (can be very large)
            analysis_type: Type of analysis (trends, anomalies, insights)

        Returns:
            Analysis results
        """
        system_instruction = """You are a data analyst specializing in e-commerce and content platform analytics.
Provide:
- Clear insights
- Actionable recommendations
- Visual data representation suggestions
- Statistical significance notes
"""

        prompt = f"""Analyze this data for {analysis_type}:

Data:
{json.dumps(data, indent=2)}

Return as JSON:
{{
    "key_insights": [
        {{
            "insight": "what you found",
            "confidence": "high|medium|low",
            "supporting_data": "data points that support this",
            "recommendation": "what to do about it"
        }}
    ],
    "trends": [...],
    "anomalies": [...],
    "predictions": [...],
    "visualization_suggestions": [...]
}}
"""

        response = await self.generate(
            prompt=prompt,
            system_instruction=system_instruction,
            temperature=0.4,  # Lower for analytical precision
            max_tokens=8192,
            response_format="json"
        )

        return response["content"]


# Singleton instance
_gemini_agent: Optional[GeminiAgent] = None


def get_gemini_agent() -> GeminiAgent:
    """Get Gemini agent singleton"""
    global _gemini_agent
    if _gemini_agent is None:
        _gemini_agent = GeminiAgent()
    return _gemini_agent
