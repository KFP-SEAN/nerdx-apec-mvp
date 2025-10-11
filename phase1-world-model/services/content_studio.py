"""
Content Studio Service
Phase 2D: Content Studio

AI-powered content generation platform for creators:
- Video script generation (Sora-style)
- Content atomization ("Turkey Slice" method)
- Multi-format content generation
- Recipe variations
- Product descriptions
- Social media content
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

from agents.gemini_agent import GeminiAgent
from agents.claude_agent import ClaudeAgent
from services.neo4j_service import get_neo4j_service

logger = logging.getLogger(__name__)


class ContentFormat(str, Enum):
    """Content output formats"""
    VIDEO_SCRIPT = "video_script"
    BLOG_POST = "blog_post"
    SOCIAL_POST = "social_post"
    EMAIL = "email"
    PRODUCT_DESC = "product_description"
    RECIPE = "recipe"
    LORE = "lore"
    SHORT_FORM = "short_form"  # TikTok, Reels, Shorts


class VideoStyle(str, Enum):
    """Video script styles"""
    CINEMATIC = "cinematic"  # Sora-style, artistic
    EDUCATIONAL = "educational"  # Tutorial, how-to
    DOCUMENTARY = "documentary"  # Storytelling, history
    ENERGETIC = "energetic"  # Fast-paced, engaging
    MINIMALIST = "minimalist"  # Simple, clean
    AUTHENTIC = "authentic"  # Raw, genuine


class ToneOfVoice(str, Enum):
    """Content tone"""
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    FRIENDLY = "friendly"
    ENTHUSIASTIC = "enthusiastic"
    EDUCATIONAL = "educational"
    INSPIRATIONAL = "inspirational"
    HUMOROUS = "humorous"


class ContentPiece:
    """Generated content piece"""
    def __init__(
        self,
        content_id: str,
        format: ContentFormat,
        title: str,
        content: str,
        metadata: Dict[str, Any] = None,
        created_at: datetime = None
    ):
        self.content_id = content_id
        self.format = format
        self.title = title
        self.content = content
        self.metadata = metadata or {}
        self.created_at = created_at or datetime.utcnow()

    def to_dict(self):
        return {
            "content_id": self.content_id,
            "format": self.format,
            "title": self.title,
            "content": self.content,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat()
        }


class ContentStudio:
    """
    AI-Powered Content Studio

    Key Features:
    - Video script generation (Sora-style cinematography)
    - Content atomization ("Turkey Slice" method)
    - Multi-format content generation
    - Brand voice consistency
    - SEO optimization
    - Localization (Korean, English, Chinese, Japanese)
    """

    def __init__(self):
        self.gemini = GeminiAgent()
        self.claude = ClaudeAgent()
        self.neo4j = get_neo4j_service()

        # Brand voice guidelines
        self.brand_voice = {
            "nerdx": {
                "personality": "Passionate about Korean culture, knowledgeable, accessible",
                "tone": ["friendly", "educational", "enthusiastic"],
                "avoid": ["overly formal", "condescending", "pushy sales"],
                "keywords": ["authentic", "traditional", "craft", "heritage", "innovation"]
            }
        }

    async def generate_video_script(
        self,
        product_id: Optional[str] = None,
        topic: Optional[str] = None,
        duration_seconds: int = 60,
        style: VideoStyle = VideoStyle.CINEMATIC,
        target_audience: str = "general",
        language: str = "en"
    ) -> ContentPiece:
        """
        Generate video script (Sora-style)

        Args:
            product_id: Product to feature
            topic: Video topic
            duration_seconds: Target duration
            style: Visual/narrative style
            target_audience: Target demographic
            language: Output language

        Returns:
            Video script with shot descriptions
        """
        try:
            # Get product details if provided
            product_context = ""
            if product_id:
                product = await self._get_product_details(product_id)
                product_context = f"""
Product: {product.get('name')}
Type: {product.get('product_type')}
Description: {product.get('description')}
Flavor Profile: {product.get('flavor_profile')}
"""

            # Build prompt for Gemini
            prompt = f"""
Generate a video script for a {duration_seconds}-second video about Korean traditional alcohol.

Style: {style.value}
Target Audience: {target_audience}
Language: {language}

{product_context if product_context else f"Topic: {topic}"}

IMPORTANT: This should be a **Sora-style** cinematic video script with:
1. Vivid visual descriptions (cinematography, lighting, movement)
2. Emotional storytelling (not just facts)
3. Cultural context and heritage
4. Authentic, engaging narrative
5. Shot-by-shot breakdown

Script Structure:
- Opening Hook (5 seconds): Captivating visual + question/statement
- Main Content (45 seconds): Story, process, or experience
- Call to Action (10 seconds): What to do next

For each shot, provide:
- **Timecode**: [00:00-00:05]
- **Visual**: Detailed description of what we see
- **Audio**: Voiceover narration
- **Music/SFX**: Mood and sound design

Brand Voice:
- Passionate about Korean culture
- Educational but accessible
- Authentic and genuine
- NOT overly promotional

Return JSON format:
{{
  "title": "Video title",
  "duration": {duration_seconds},
  "hook": "Opening hook text",
  "shots": [
    {{
      "timecode": "[00:00-00:05]",
      "visual": "Detailed visual description...",
      "voiceover": "Narration text...",
      "music": "Mood/music notes..."
    }}
  ],
  "call_to_action": "CTA text",
  "hashtags": ["#tag1", "#tag2"],
  "seo_keywords": ["keyword1", "keyword2"]
}}
"""

            result = await self.gemini.generate(
                prompt=prompt,
                temperature=0.8  # Higher for creativity
            )

            # Parse response
            import json
            response_text = result.get("text", "")
            if "```json" in response_text:
                json_str = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                json_str = response_text.split("```")[1].split("```")[0].strip()
            else:
                json_str = response_text

            script_data = json.loads(json_str)

            # Create content piece
            content = ContentPiece(
                content_id=f"video_script_{datetime.utcnow().timestamp()}",
                format=ContentFormat.VIDEO_SCRIPT,
                title=script_data["title"],
                content=json.dumps(script_data, indent=2),
                metadata={
                    "duration": duration_seconds,
                    "style": style.value,
                    "language": language,
                    "product_id": product_id,
                    "shots_count": len(script_data.get("shots", []))
                }
            )

            logger.info(f"Video script generated: {content.title}")
            return content

        except Exception as e:
            logger.error(f"Video script generation error: {e}")
            raise

    async def atomize_content(
        self,
        pillar_content: str,
        pillar_title: str,
        output_formats: List[ContentFormat],
        count_per_format: int = 3
    ) -> List[ContentPiece]:
        """
        Content atomization - "Turkey Slice" method

        Takes one pillar content piece (long-form) and atomizes it into
        multiple micro-content pieces for different platforms.

        Example: 1 blog post → 5 social posts + 3 short videos + 2 emails

        Args:
            pillar_content: Source content (blog, video script, etc.)
            pillar_title: Title of pillar content
            output_formats: Formats to generate
            count_per_format: How many pieces per format

        Returns:
            List of atomized content pieces
        """
        try:
            atomized = []

            for format in output_formats:
                # Generate content for each format
                prompt = f"""
You are a content strategist using the "Turkey Slice" method to atomize content.

**Pillar Content**: "{pillar_title}"

{pillar_content[:2000]}  # First 2000 chars

Task: Create {count_per_format} pieces of **{format.value}** content by atomizing the pillar content.

Requirements:
1. Each piece should stand alone (complete thought)
2. Highlight ONE key insight/idea from pillar content
3. Optimize for platform: {self._get_format_guidelines(format)}
4. Maintain brand voice (friendly, educational, authentic)
5. Include relevant calls-to-action
6. Add appropriate hashtags/keywords

Return JSON array:
[
  {{
    "title": "Piece title",
    "content": "Main content text...",
    "platform_notes": "Platform-specific notes",
    "hashtags": ["#tag1", "#tag2"],
    "estimated_engagement": "high|medium|low"
  }}
]
"""

                result = await self.gemini.generate(
                    prompt=prompt,
                    temperature=0.7
                )

                # Parse response
                import json
                response_text = result.get("text", "")
                if "```json" in response_text:
                    json_str = response_text.split("```json")[1].split("```")[0].strip()
                elif "```" in response_text:
                    json_str = response_text.split("```")[1].split("```")[0].strip()
                else:
                    json_str = response_text

                pieces_data = json.loads(json_str)

                # Create content pieces
                for i, piece_data in enumerate(pieces_data):
                    content = ContentPiece(
                        content_id=f"atomized_{format.value}_{i}_{datetime.utcnow().timestamp()}",
                        format=format,
                        title=piece_data["title"],
                        content=piece_data["content"],
                        metadata={
                            "pillar_title": pillar_title,
                            "platform_notes": piece_data.get("platform_notes"),
                            "hashtags": piece_data.get("hashtags", []),
                            "estimated_engagement": piece_data.get("estimated_engagement")
                        }
                    )
                    atomized.append(content)

            logger.info(f"Atomized into {len(atomized)} pieces")
            return atomized

        except Exception as e:
            logger.error(f"Content atomization error: {e}")
            return []

    async def generate_product_description(
        self,
        product_id: str,
        length: str = "medium",  # short, medium, long
        tone: ToneOfVoice = ToneOfVoice.FRIENDLY,
        include_storytelling: bool = True,
        language: str = "en"
    ) -> ContentPiece:
        """
        Generate compelling product description

        Args:
            product_id: Product identifier
            length: Description length
            tone: Tone of voice
            include_storytelling: Include origin story/lore
            language: Output language

        Returns:
            Product description
        """
        try:
            # Get product and related lore
            product = await self._get_product_details(product_id)
            lore = await self._get_product_lore(product_id)

            # Use Gemini for creative description
            prompt = f"""
Write a compelling product description for an e-commerce store.

Product: {product.get('name')}
Type: {product.get('product_type')}
ABV: {product.get('abv')}%
Price: ${product.get('price_usd')}

Current Description: {product.get('description')}

{f"Origin Story: {lore}" if lore and include_storytelling else ""}

Requirements:
- Length: {length}
- Tone: {tone.value}
- Language: {language}
- Include sensory details (taste, aroma, texture)
- Highlight unique selling points
- {('Include storytelling/heritage' if include_storytelling else 'Focus on product features')}
- SEO optimized
- Call to action at end

Return JSON:
{{
  "title": "Product title (optimized)",
  "tagline": "One-line hook",
  "description": "Main description...",
  "highlights": ["Bullet point 1", "Bullet point 2"],
  "tasting_notes": "Flavor profile description",
  "pairing_suggestions": "Food pairing recommendations",
  "seo_keywords": ["keyword1", "keyword2"]
}}
"""

            result = await self.gemini.generate(
                prompt=prompt,
                temperature=0.7
            )

            # Parse and create content
            import json
            response_text = result.get("text", "")
            if "```json" in response_text:
                json_str = response_text.split("```json")[1].split("```")[0].strip()
            else:
                json_str = response_text

            desc_data = json.loads(json_str)

            content = ContentPiece(
                content_id=f"product_desc_{product_id}_{datetime.utcnow().timestamp()}",
                format=ContentFormat.PRODUCT_DESC,
                title=desc_data["title"],
                content=json.dumps(desc_data, indent=2),
                metadata={
                    "product_id": product_id,
                    "length": length,
                    "tone": tone.value,
                    "language": language
                }
            )

            return content

        except Exception as e:
            logger.error(f"Product description generation error: {e}")
            raise

    async def variate_recipe(
        self,
        base_recipe: str,
        variation_type: str,  # "seasonal", "fusion", "simplified", "premium"
        count: int = 3
    ) -> List[ContentPiece]:
        """
        Generate recipe variations

        Args:
            base_recipe: Original recipe
            variation_type: Type of variation
            count: Number of variations

        Returns:
            List of recipe variations
        """
        try:
            # Use Gemini's recipe variation capability
            result = await self.gemini.variate_recipe(
                base_recipe=base_recipe,
                variation_type=variation_type,
                count=count
            )

            # Convert to ContentPiece objects
            variations = []
            recipes_data = result.get("variations", [])

            for i, recipe in enumerate(recipes_data):
                content = ContentPiece(
                    content_id=f"recipe_var_{variation_type}_{i}_{datetime.utcnow().timestamp()}",
                    format=ContentFormat.RECIPE,
                    title=recipe.get("name", f"Variation {i+1}"),
                    content=json.dumps(recipe, indent=2),
                    metadata={
                        "variation_type": variation_type,
                        "base_recipe": base_recipe[:100]
                    }
                )
                variations.append(content)

            return variations

        except Exception as e:
            logger.error(f"Recipe variation error: {e}")
            return []

    async def generate_social_content(
        self,
        topic: str,
        platform: str,  # "instagram", "twitter", "tiktok", "facebook"
        count: int = 5,
        include_hashtags: bool = True,
        language: str = "en"
    ) -> List[ContentPiece]:
        """
        Generate platform-optimized social media content

        Args:
            topic: Content topic
            platform: Target platform
            count: Number of posts
            include_hashtags: Add hashtags
            language: Output language

        Returns:
            List of social posts
        """
        try:
            platform_specs = self._get_platform_specs(platform)

            prompt = f"""
Create {count} engaging social media posts for {platform}.

Topic: {topic}
Brand: NERDX (Korean traditional alcohol)
Voice: Friendly, educational, authentic

Platform Specs:
- Character limit: {platform_specs['char_limit']}
- Best practices: {platform_specs['best_practices']}
- Content style: {platform_specs['style']}

Requirements:
- Each post should stand alone
- Hook in first line
- Clear value proposition
- {('Include relevant hashtags' if include_hashtags else 'No hashtags')}
- Language: {language}
- Varied content (not repetitive)

Return JSON array:
[
  {{
    "post_text": "Post content...",
    "hashtags": ["#tag1", "#tag2"],
    "call_to_action": "CTA",
    "estimated_reach": "high|medium|low",
    "best_time_to_post": "morning|afternoon|evening"
  }}
]
"""

            result = await self.gemini.generate(
                prompt=prompt,
                temperature=0.8
            )

            # Parse and create content pieces
            import json
            response_text = result.get("text", "")
            if "```json" in response_text:
                json_str = response_text.split("```json")[1].split("```")[0].strip()
            else:
                json_str = response_text

            posts_data = json.loads(json_str)

            posts = []
            for i, post_data in enumerate(posts_data):
                content = ContentPiece(
                    content_id=f"social_{platform}_{i}_{datetime.utcnow().timestamp()}",
                    format=ContentFormat.SOCIAL_POST,
                    title=f"{platform.capitalize()} Post {i+1}",
                    content=post_data["post_text"],
                    metadata={
                        "platform": platform,
                        "hashtags": post_data.get("hashtags", []),
                        "call_to_action": post_data.get("call_to_action"),
                        "estimated_reach": post_data.get("estimated_reach"),
                        "best_time": post_data.get("best_time_to_post")
                    }
                )
                posts.append(content)

            return posts

        except Exception as e:
            logger.error(f"Social content generation error: {e}")
            return []

    async def generate_content_batch(
        self,
        content_brief: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate multiple content pieces from a brief

        Content brief format:
        {
            "campaign_name": "Summer Makgeolli",
            "product_ids": ["product_1", "product_2"],
            "formats": ["video_script", "blog_post", "social_post"],
            "target_audience": "millennials",
            "key_messages": ["refreshing", "authentic", "craft"],
            "language": "en"
        }

        Returns:
            Complete content package
        """
        try:
            content_package = {
                "campaign_name": content_brief["campaign_name"],
                "generated_at": datetime.utcnow().isoformat(),
                "content": []
            }

            formats = content_brief.get("formats", [])

            # Generate for each format
            for format_str in formats:
                format = ContentFormat(format_str)

                if format == ContentFormat.VIDEO_SCRIPT:
                    for product_id in content_brief.get("product_ids", []):
                        script = await self.generate_video_script(
                            product_id=product_id,
                            target_audience=content_brief.get("target_audience", "general"),
                            language=content_brief.get("language", "en")
                        )
                        content_package["content"].append(script.to_dict())

                elif format == ContentFormat.SOCIAL_POST:
                    posts = await self.generate_social_content(
                        topic=content_brief["campaign_name"],
                        platform="instagram",
                        count=5,
                        language=content_brief.get("language", "en")
                    )
                    content_package["content"].extend([p.to_dict() for p in posts])

                # Add more formats as needed

            logger.info(f"Content batch generated: {len(content_package['content'])} pieces")
            return content_package

        except Exception as e:
            logger.error(f"Batch generation error: {e}")
            return {"error": str(e)}

    # Helper methods

    async def _get_product_details(self, product_id: str) -> Dict[str, Any]:
        """Get product from Neo4j"""
        try:
            query = "MATCH (p:Product {product_id: $product_id}) RETURN p"
            result = self.neo4j.execute_query(query, product_id=product_id)
            return dict(result[0]["p"]) if result else {}
        except:
            return {}

    async def _get_product_lore(self, product_id: str) -> Optional[str]:
        """Get product lore/story"""
        try:
            query = """
            MATCH (p:Product {product_id: $product_id})-[:HAS_STORY]->(l:Lore)
            RETURN l.story_text as story
            LIMIT 1
            """
            result = self.neo4j.execute_query(query, product_id=product_id)
            return result[0]["story"] if result else None
        except:
            return None

    def _get_format_guidelines(self, format: ContentFormat) -> str:
        """Get platform-specific guidelines"""
        guidelines = {
            ContentFormat.SOCIAL_POST: "Short, punchy, hashtag-friendly, visual-first",
            ContentFormat.BLOG_POST: "Long-form, SEO-optimized, educational, storytelling",
            ContentFormat.EMAIL: "Scannable, personal, clear CTA, mobile-friendly",
            ContentFormat.SHORT_FORM: "15-60 seconds, hook in 3 seconds, trending audio",
            ContentFormat.VIDEO_SCRIPT: "Visual storytelling, emotional arc, clear structure"
        }
        return guidelines.get(format, "Platform-appropriate content")

    def _get_platform_specs(self, platform: str) -> Dict[str, Any]:
        """Get platform specifications"""
        specs = {
            "instagram": {
                "char_limit": 2200,
                "best_practices": "Visual-first, hashtags (5-10), emojis, stories",
                "style": "Aspirational, authentic, visually appealing"
            },
            "twitter": {
                "char_limit": 280,
                "best_practices": "Concise, hashtags (1-2), threads, engagement",
                "style": "Conversational, witty, timely"
            },
            "tiktok": {
                "char_limit": 150,
                "best_practices": "Video-first, trending sounds, fast-paced",
                "style": "Entertaining, authentic, trend-riding"
            },
            "facebook": {
                "char_limit": 63206,
                "best_practices": "Community-building, longer posts OK, groups",
                "style": "Conversational, community-focused"
            }
        }
        return specs.get(platform, specs["instagram"])


# Singleton instance
_content_studio = None

def get_content_studio() -> ContentStudio:
    """Get singleton ContentStudio instance"""
    global _content_studio
    if _content_studio is None:
        _content_studio = ContentStudio()
    return _content_studio
