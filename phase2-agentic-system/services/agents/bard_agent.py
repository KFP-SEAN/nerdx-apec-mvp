"""
Bard Agent (음유시인 에이전트) - Creative Director
Phase 3A: Brand Storytelling & Content Generation

Capabilities:
- Luxury brand narrative creation (Mo

ët Hennessy style)
- Campaign concept development
- Multi-platform content generation
- Content atomization ("Turkey Slice")
- Influencer collaboration guidelines
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
from pydantic import BaseModel
import json

from .base_agent import BaseAgent, AgentCapability, AgentResponse

logger = logging.getLogger(__name__)


class ContentFormat(str, Enum):
    """Content output formats"""
    VIDEO_SCRIPT = "video_script"
    SOCIAL_POST = "social_post"
    EMAIL = "email"
    BLOG_POST = "blog_post"
    PRODUCT_DESCRIPTION = "product_description"
    AD_COPY = "ad_copy"
    INFLUENCER_BRIEF = "influencer_brief"


class StorytellingStyle(str, Enum):
    """Brand storytelling styles"""
    LUXURY = "luxury"              # Moët Hennessy - heritage, craftsmanship
    PLAYFUL = "playful"            # Pop Mart - fun, collectible
    AUTHENTIC = "authentic"        # Craft brewery - genuine, transparent
    ASPIRATIONAL = "aspirational"  # Premium positioning
    EDUCATIONAL = "educational"    # Teach & inform


class BrandNarrative(BaseModel):
    """Brand story/narrative"""
    narrative_id: str
    title: str
    product_name: str
    core_message: str
    storytelling_style: StorytellingStyle
    full_narrative: str  # Complete story
    key_themes: List[str]
    emotional_hooks: List[str]
    target_audience: str
    heritage_elements: List[str]  # Korean cultural elements
    craftsmanship_details: List[str]
    confidence: float = 0.8


class CampaignContent(BaseModel):
    """Marketing campaign content"""
    campaign_id: str
    campaign_name: str
    product_name: str
    tagline: str
    core_concept: str
    content_pieces: List[Dict[str, Any]]  # Format-specific content
    target_channels: List[str]
    timeline: str
    kpis: List[str]
    budget_recommendation: str


class ContentPiece(BaseModel):
    """Individual content piece"""
    content_id: str
    format: ContentFormat
    platform: str  # Instagram, TikTok, YouTube, etc.
    title: str
    content: str
    duration_seconds: Optional[int] = None  # For video
    hashtags: List[str] = []
    cta: Optional[str] = None  # Call to action
    metadata: Dict[str, Any] = {}


class BardAgent(BaseAgent):
    """
    Bard Agent - Creative Director & Brand Storyteller

    The "음유시인" agent that crafts compelling narratives by:
    - Creating luxury brand stories (Moët Hennessy playbook)
    - Generating multi-platform marketing content
    - Atomizing pillar content into micro-content ("Turkey Slice")
    - Designing influencer collaboration strategies
    - Maintaining brand voice consistency

    Output: High-quality creative assets for NERD brand marketing
    """

    def __init__(self, agent_id: str = "bard-001", world_model_url: Optional[str] = None):
        super().__init__(
            agent_id=agent_id,
            agent_type="bard",
            capabilities=[
                AgentCapability.GENERATION,
                AgentCapability.OPTIMIZATION
            ],
            world_model_url=world_model_url
        )

        # Storytelling templates
        self.luxury_templates = self._load_luxury_templates()

    async def execute_task(
        self,
        task_id: str,
        task_type: str,
        parameters: Dict[str, Any]
    ) -> AgentResponse:
        """
        Execute Bard task

        Task Types:
        - generate_brand_story: Create brand narrative
        - create_campaign: Full campaign planning
        - atomize_content: Turkey Slice content atomization
        - generate_content_piece: Single content piece
        - influencer_brief: Collaboration guidelines
        """
        start_time = datetime.utcnow()

        try:
            if task_type == "generate_brand_story":
                result = await self.generate_brand_story(parameters)
            elif task_type == "create_campaign":
                result = await self.create_campaign(parameters)
            elif task_type == "atomize_content":
                result = await self.atomize_content(parameters)
            elif task_type == "generate_content_piece":
                result = await self.generate_content_piece(parameters)
            elif task_type == "influencer_brief":
                result = await self.generate_influencer_brief(parameters)
            else:
                raise ValueError(f"Unknown task type: {task_type}")

            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000

            return self.create_response(
                task_id=task_id,
                status="success",
                confidence=result.get("confidence", 0.85),
                result=result,
                processing_time_ms=int(processing_time)
            )

        except Exception as e:
            logger.error(f"Bard task {task_id} failed: {e}")
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000

            return self.create_response(
                task_id=task_id,
                status="failed",
                confidence=0.0,
                result={},
                error_message=str(e),
                processing_time_ms=int(processing_time)
            )

    async def generate_brand_story(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate luxury brand narrative

        Parameters:
            - product_name: Name of the product
            - product_description: Product details
            - key_ingredients: Main ingredients/materials
            - origin_story: How it was created
            - storytelling_style: Luxury, playful, etc.
            - target_audience: Who is this for

        Returns:
            Complete brand narrative with themes and hooks
        """
        self.validate_capability(AgentCapability.GENERATION)

        product_name = parameters.get("product_name", "NERD Product")
        product_description = parameters.get("product_description", "")
        key_ingredients = parameters.get("key_ingredients", [])
        origin_story = parameters.get("origin_story", "")
        storytelling_style = parameters.get("storytelling_style", StorytellingStyle.LUXURY)
        target_audience = parameters.get("target_audience", "Sophisticated millennials")

        logger.info(f"Generating brand story for '{product_name}' in {storytelling_style} style")

        # Generate narrative using Gemini (better for creative writing)
        narrative = await self._generate_luxury_narrative(
            product_name,
            product_description,
            key_ingredients,
            origin_story,
            storytelling_style,
            target_audience
        )

        # Extract themes and hooks using Claude (better for structured analysis)
        themes_and_hooks = await self._extract_themes_and_hooks(narrative)

        brand_narrative = BrandNarrative(
            narrative_id=f"narrative-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}",
            title=themes_and_hooks.get("title", f"The Story of {product_name}"),
            product_name=product_name,
            core_message=themes_and_hooks.get("core_message", ""),
            storytelling_style=storytelling_style,
            full_narrative=narrative,
            key_themes=themes_and_hooks.get("themes", []),
            emotional_hooks=themes_and_hooks.get("hooks", []),
            target_audience=target_audience,
            heritage_elements=themes_and_hooks.get("heritage", []),
            craftsmanship_details=themes_and_hooks.get("craftsmanship", []),
            confidence=0.88
        )

        return {
            "narrative": brand_narrative.model_dump(),
            "confidence": 0.88,
            "storytelling_style": storytelling_style
        }

    async def create_campaign(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create comprehensive marketing campaign

        Parameters:
            - product_name: Product name
            - campaign_objective: Launch, awareness, sales, etc.
            - target_channels: Instagram, TikTok, YouTube, etc.
            - budget_range: Budget tier (low, medium, high)
            - timeline: Campaign duration
            - brand_narrative: Existing narrative (optional)

        Returns:
            Full campaign plan with content across channels
        """
        self.validate_capability(AgentCapability.GENERATION)

        product_name = parameters.get("product_name", "NERD Product")
        objective = parameters.get("campaign_objective", "product launch")
        channels = parameters.get("target_channels", ["instagram", "tiktok", "youtube"])
        budget = parameters.get("budget_range", "medium")
        timeline = parameters.get("timeline", "4 weeks")
        narrative = parameters.get("brand_narrative")

        logger.info(f"Creating campaign for '{product_name}' - {objective}")

        # If no narrative provided, generate one
        if not narrative:
            story_result = await self.generate_brand_story(parameters)
            narrative = story_result["narrative"]

        # Generate campaign concept using Gemini
        campaign = await self._generate_campaign_concept(
            product_name,
            objective,
            channels,
            budget,
            timeline,
            narrative
        )

        # Generate content pieces for each channel
        content_pieces = await self._generate_channel_content(
            product_name,
            campaign,
            channels
        )

        campaign_content = CampaignContent(
            campaign_id=f"campaign-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}",
            campaign_name=campaign.get("name", f"{product_name} Launch"),
            product_name=product_name,
            tagline=campaign.get("tagline", ""),
            core_concept=campaign.get("concept", ""),
            content_pieces=content_pieces,
            target_channels=channels,
            timeline=timeline,
            kpis=campaign.get("kpis", []),
            budget_recommendation=campaign.get("budget_recommendation", "")
        )

        return {
            "campaign": campaign_content.model_dump(),
            "confidence": 0.85,
            "total_content_pieces": len(content_pieces)
        }

    async def atomize_content(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Atomize pillar content into micro-content ("Turkey Slice")

        Parameters:
            - pillar_content: Original long-form content
            - content_type: blog, video_script, narrative, etc.
            - target_formats: Desired output formats
            - count_per_format: Number of pieces per format

        Returns:
            Multiple atomized content pieces
        """
        self.validate_capability(AgentCapability.OPTIMIZATION)

        pillar_content = parameters.get("pillar_content", "")
        content_type = parameters.get("content_type", "blog")
        target_formats = parameters.get("target_formats", [
            ContentFormat.SOCIAL_POST,
            ContentFormat.VIDEO_SCRIPT,
            ContentFormat.EMAIL
        ])
        count_per_format = parameters.get("count_per_format", 3)

        logger.info(f"Atomizing {content_type} into {len(target_formats)} formats")

        # Use Gemini for content atomization (faster, creative)
        atomized_pieces = await self._atomize_pillar_content(
            pillar_content,
            content_type,
            target_formats,
            count_per_format
        )

        return {
            "atomized_content": [piece.model_dump() for piece in atomized_pieces],
            "total_pieces": len(atomized_pieces),
            "source_content_type": content_type,
            "confidence": 0.82
        }

    async def generate_content_piece(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate single content piece

        Parameters:
            - format: Content format (video_script, social_post, etc.)
            - platform: Target platform
            - product_name: Product name
            - key_message: Main message
            - tone: Brand voice tone
            - duration_seconds: For video (optional)

        Returns:
            Single optimized content piece
        """
        self.validate_capability(AgentCapability.GENERATION)

        format_type = ContentFormat(parameters.get("format", "social_post"))
        platform = parameters.get("platform", "instagram")
        product_name = parameters.get("product_name", "")
        key_message = parameters.get("key_message", "")
        tone = parameters.get("tone", "aspirational")
        duration = parameters.get("duration_seconds")

        logger.info(f"Generating {format_type} for {platform}")

        # Generate content using Gemini
        content_piece = await self._generate_single_content(
            format_type,
            platform,
            product_name,
            key_message,
            tone,
            duration
        )

        return {
            "content": content_piece.model_dump(),
            "confidence": 0.85
        }

    async def generate_influencer_brief(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate influencer collaboration brief

        Parameters:
            - product_name: Product to promote
            - influencer_profile: Influencer details
            - collaboration_type: Sponsored post, unboxing, review, etc.
            - brand_guidelines: Brand dos and don'ts

        Returns:
            Influencer collaboration brief
        """
        self.validate_capability(AgentCapability.GENERATION)

        product_name = parameters.get("product_name", "")
        influencer = parameters.get("influencer_profile", {})
        collab_type = parameters.get("collaboration_type", "sponsored_post")
        guidelines = parameters.get("brand_guidelines", {})

        logger.info(f"Generating influencer brief for {product_name}")

        # Generate brief using Gemini
        brief = await self._generate_collab_brief(
            product_name,
            influencer,
            collab_type,
            guidelines
        )

        return {
            "influencer_brief": brief,
            "confidence": 0.80,
            "collaboration_type": collab_type
        }

    # Helper methods

    def _load_luxury_templates(self) -> Dict[str, str]:
        """Load luxury storytelling templates (Moët Hennessy style)"""
        return {
            "heritage": """
{product_name} is not merely a beverage—it is a {heritage_period} legacy reborn.

Crafted in the heart of {origin_location}, each bottle embodies the spirit of Korean tradition,
where {key_ingredient} has been revered for generations as the essence of {cultural_significance}.

Our master distillers, trained in techniques passed down through {generations} generations,
transform {raw_materials} into an elixir that bridges past and future.
""",
            "craftsmanship": """
The creation of {product_name} is an act of devotion.

{duration} days of meticulous fermentation. {temperature_control} precision.
Hand-selected {ingredient_1} from {source_location}, harvested at the peak of {season}.

Every step honors the craft. Every bottle tells a story.

This is not mass production. This is mastery.
""",
            "exclusivity": """
{product_name} exists for those who understand that true luxury is measured not in price,
but in rarity, in experience, in the stories we carry with us.

Limited to {production_quantity} bottles per {time_period}.
Each numbered. Each unique. Each a collector's treasure.

This is not for everyone. And that is precisely the point.
"""
        }

    async def _generate_luxury_narrative(
        self,
        product_name: str,
        description: str,
        ingredients: List[str],
        origin_story: str,
        style: StorytellingStyle,
        target_audience: str
    ) -> str:
        """Generate luxury brand narrative using Gemini"""

        narrative_prompt = f"""
You are a luxury brand storyteller specializing in premium spirits and beverages.

Create a compelling brand narrative for:

**Product**: {product_name}
**Description**: {description}
**Key Ingredients**: {', '.join(ingredients)}
**Origin Story**: {origin_story}
**Style**: {style}
**Target Audience**: {target_audience}

Style Guidelines:
- Moët Hennessy level of sophistication
- Emphasize heritage, craftsmanship, and Korean cultural elements
- Create emotional resonance
- Avoid generic marketing speak
- Use sensory language
- Build aspiration and exclusivity

Structure:
1. Opening Hook (2-3 sentences that captivate)
2. Heritage & Origin (the story of creation)
3. Craftsmanship & Process (the art of making)
4. Experience & Emotion (what it feels like)
5. Invitation (call to join the story)

Length: 400-600 words

Write the narrative:
"""

        try:
            narrative = await self.call_gemini(
                prompt=narrative_prompt,
                system_prompt="You are an award-winning luxury brand storyteller."
            )
            return narrative

        except Exception as e:
            logger.error(f"Narrative generation failed: {e}")
            return f"The Story of {product_name}\n\nA premium Korean beverage experience..."

    async def _extract_themes_and_hooks(self, narrative: str) -> Dict[str, Any]:
        """Extract themes and emotional hooks using Claude"""

        extraction_prompt = f"""
Analyze this brand narrative and extract:

**Narrative:**
{narrative}

Extract:
1. Title (compelling headline, 5-10 words)
2. Core Message (one sentence essence)
3. Key Themes (3-5 recurring themes)
4. Emotional Hooks (3-5 emotional triggers)
5. Heritage Elements (Korean cultural references)
6. Craftsmanship Details (production/quality details)

Return as JSON:
{{
    "title": "...",
    "core_message": "...",
    "themes": ["theme1", "theme2", ...],
    "hooks": ["hook1", "hook2", ...],
    "heritage": ["element1", "element2", ...],
    "craftsmanship": ["detail1", "detail2", ...]
}}
"""

        try:
            response = await self.call_claude(
                prompt=extraction_prompt,
                system_prompt="You are an expert in brand narrative analysis."
            )

            # Parse JSON
            import re
            json_match = re.search(r'```json\n(.*?)\n```', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(1))
            else:
                data = json.loads(response)

            return data

        except Exception as e:
            logger.error(f"Theme extraction failed: {e}")
            return {
                "title": "Brand Story",
                "core_message": "",
                "themes": [],
                "hooks": [],
                "heritage": [],
                "craftsmanship": []
            }

    async def _generate_campaign_concept(
        self,
        product_name: str,
        objective: str,
        channels: List[str],
        budget: str,
        timeline: str,
        narrative: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate campaign concept using Gemini"""

        concept_prompt = f"""
Create a marketing campaign for:

**Product**: {product_name}
**Objective**: {objective}
**Channels**: {', '.join(channels)}
**Budget**: {budget}
**Timeline**: {timeline}

**Brand Narrative Summary**:
{narrative.get('core_message', '')}
Themes: {', '.join(narrative.get('key_themes', []))}

Create:
1. Campaign Name (catchy, memorable)
2. Tagline (5-8 words)
3. Core Concept (the big idea, 2-3 sentences)
4. KPIs (5 measurable goals)
5. Budget Recommendation (how to allocate {budget} budget)

Return as JSON:
{{
    "name": "...",
    "tagline": "...",
    "concept": "...",
    "kpis": ["kpi1", "kpi2", ...],
    "budget_recommendation": "..."
}}
"""

        try:
            response = await self.call_gemini(prompt=concept_prompt)

            import re
            json_match = re.search(r'```json\n(.*?)\n```', response, re.DOTALL)
            if json_match:
                concept = json.loads(json_match.group(1))
            else:
                concept = json.loads(response)

            return concept

        except Exception as e:
            logger.error(f"Campaign concept generation failed: {e}")
            return {
                "name": f"{product_name} Launch Campaign",
                "tagline": "Experience Something Extraordinary",
                "concept": "A multi-channel campaign celebrating craft and heritage.",
                "kpis": ["Brand awareness", "Engagement rate", "Conversion"],
                "budget_recommendation": "Allocate across digital channels"
            }

    async def _generate_channel_content(
        self,
        product_name: str,
        campaign: Dict[str, Any],
        channels: List[str]
    ) -> List[Dict[str, Any]]:
        """Generate content for each channel"""

        all_content = []

        channel_specs = {
            "instagram": {"format": ContentFormat.SOCIAL_POST, "count": 3},
            "tiktok": {"format": ContentFormat.VIDEO_SCRIPT, "count": 2},
            "youtube": {"format": ContentFormat.VIDEO_SCRIPT, "count": 1},
            "email": {"format": ContentFormat.EMAIL, "count": 2}
        }

        for channel in channels:
            spec = channel_specs.get(channel.lower(), {"format": ContentFormat.SOCIAL_POST, "count": 2})

            for i in range(spec["count"]):
                piece = await self._generate_single_content(
                    format_type=spec["format"],
                    platform=channel,
                    product_name=product_name,
                    key_message=campaign.get("tagline", ""),
                    tone="aspirational"
                )
                all_content.append(piece.model_dump())

        return all_content

    async def _generate_single_content(
        self,
        format_type: ContentFormat,
        platform: str,
        product_name: str,
        key_message: str,
        tone: str,
        duration: Optional[int] = None
    ) -> ContentPiece:
        """Generate single content piece"""

        content_prompt = f"""
Create {format_type} content for {platform}:

**Product**: {product_name}
**Key Message**: {key_message}
**Tone**: {tone}
{f"**Duration**: {duration} seconds" if duration else ""}

Platform-specific requirements:
- Instagram: Visual, hashtags, 2200 char limit
- TikTok: Viral hooks, trending sounds, 15-60s
- YouTube: Longer format, storytelling, SEO
- Email: Subject + body, CTA

Generate optimized content for this platform.

Return as JSON:
{{
    "title": "...",
    "content": "...",
    "hashtags": ["tag1", "tag2", ...],
    "cta": "...",
    "metadata": {{}}
}}
"""

        try:
            response = await self.call_gemini(prompt=content_prompt)

            import re
            json_match = re.search(r'```json\n(.*?)\n```', response, re.DOTALL)
            if json_match:
                content_data = json.loads(json_match.group(1))
            else:
                content_data = json.loads(response)

            piece = ContentPiece(
                content_id=f"content-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                format=format_type,
                platform=platform,
                title=content_data.get("title", ""),
                content=content_data.get("content", ""),
                duration_seconds=duration,
                hashtags=content_data.get("hashtags", []),
                cta=content_data.get("cta"),
                metadata=content_data.get("metadata", {})
            )

            return piece

        except Exception as e:
            logger.error(f"Content generation failed: {e}")
            return ContentPiece(
                content_id=f"content-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                format=format_type,
                platform=platform,
                title=f"{product_name} on {platform}",
                content=f"Discover {product_name}. {key_message}"
            )

    async def _atomize_pillar_content(
        self,
        pillar_content: str,
        content_type: str,
        target_formats: List[ContentFormat],
        count_per_format: int
    ) -> List[ContentPiece]:
        """Atomize pillar content using Turkey Slice method"""

        atomize_prompt = f"""
You are a content atomization expert.

Take this pillar content and "slice" it into micro-content pieces:

**Pillar Content** ({content_type}):
{pillar_content}

**Target Formats**: {', '.join([f.value for f in target_formats])}
**Pieces per format**: {count_per_format}

"Turkey Slice" method: Extract key insights/moments from pillar content and
transform each into standalone pieces optimized for different formats.

For each piece:
1. Extract a specific insight/moment
2. Reframe for the target format
3. Optimize for platform (length, tone, hooks)
4. Add platform-specific elements (hashtags, CTAs)

Return as JSON array:
[
    {{
        "format": "social_post",
        "platform": "instagram",
        "title": "...",
        "content": "...",
        "hashtags": [...],
        "cta": "..."
    }},
    ...
]
"""

        try:
            response = await self.call_gemini(prompt=atomize_prompt, max_tokens=4000)

            import re
            json_match = re.search(r'```json\n(.*?)\n```', response, re.DOTALL)
            if json_match:
                pieces_data = json.loads(json_match.group(1))
            else:
                pieces_data = json.loads(response)

            content_pieces = []
            for piece_data in pieces_data:
                piece = ContentPiece(
                    content_id=f"atomized-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{len(content_pieces)}",
                    format=ContentFormat(piece_data.get("format", "social_post")),
                    platform=piece_data.get("platform", "general"),
                    title=piece_data.get("title", ""),
                    content=piece_data.get("content", ""),
                    hashtags=piece_data.get("hashtags", []),
                    cta=piece_data.get("cta")
                )
                content_pieces.append(piece)

            return content_pieces

        except Exception as e:
            logger.error(f"Content atomization failed: {e}")
            return []

    async def _generate_collab_brief(
        self,
        product_name: str,
        influencer: Dict[str, Any],
        collab_type: str,
        guidelines: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate influencer collaboration brief"""

        brief_prompt = f"""
Create an influencer collaboration brief:

**Product**: {product_name}
**Influencer**: {influencer.get('name', 'Partner')}
- Followers: {influencer.get('followers', 'N/A')}
- Platform: {influencer.get('platform', 'Instagram')}
- Niche: {influencer.get('niche', 'Lifestyle')}

**Collaboration Type**: {collab_type}

**Brand Guidelines**:
{json.dumps(guidelines, indent=2)}

Create brief with:
1. Objective
2. Deliverables
3. Key Messages
4. Creative Freedom vs. Must-Haves
5. Posting Schedule
6. Compensation
7. Success Metrics

Return as structured JSON.
"""

        try:
            response = await self.call_gemini(prompt=brief_prompt)

            import re
            json_match = re.search(r'```json\n(.*?)\n```', response, re.DOTALL)
            if json_match:
                brief = json.loads(json_match.group(1))
            else:
                brief = json.loads(response)

            return brief

        except Exception as e:
            logger.error(f"Influencer brief generation failed: {e}")
            return {
                "objective": f"Promote {product_name}",
                "deliverables": ["Social posts"],
                "compensation": "TBD"
            }


# Singleton instance
_bard_agent = None

def get_bard_agent(world_model_url: Optional[str] = None) -> BardAgent:
    """Get singleton Bard agent instance"""
    global _bard_agent
    if _bard_agent is None:
        _bard_agent = BardAgent(world_model_url=world_model_url)
    return _bard_agent
