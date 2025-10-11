"""
Content Studio API Router
Phase 2D: Content Studio

Public API for AI-powered content generation:
- Video script generation
- Content atomization
- Product descriptions
- Social media content
- Recipe variations
- Batch generation
"""
from fastapi import APIRouter, HTTPException, Body, Query
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from services.content_studio import (
    get_content_studio,
    ContentFormat,
    VideoStyle,
    ToneOfVoice
)

router = APIRouter()


# Request Models

class VideoScriptRequest(BaseModel):
    """Video script generation request"""
    product_id: Optional[str] = Field(None, description="Product to feature")
    topic: Optional[str] = Field(None, description="Video topic if no product")
    duration_seconds: int = Field(60, ge=15, le=300, description="Target duration (15-300s)")
    style: str = Field("cinematic", description="Video style: cinematic, educational, documentary, energetic, minimalist, authentic")
    target_audience: str = Field("general", description="Target demographic")
    language: str = Field("en", description="Output language (en, ko, zh, ja)")


class ContentAtomizationRequest(BaseModel):
    """Content atomization request"""
    pillar_content: str = Field(..., description="Source pillar content")
    pillar_title: str = Field(..., description="Title of pillar content")
    output_formats: List[str] = Field(..., description="Output formats: video_script, blog_post, social_post, email, short_form")
    count_per_format: int = Field(3, ge=1, le=10, description="Pieces per format")


class ProductDescriptionRequest(BaseModel):
    """Product description generation request"""
    product_id: str = Field(..., description="Product identifier")
    length: str = Field("medium", description="Length: short, medium, long")
    tone: str = Field("friendly", description="Tone: professional, casual, friendly, enthusiastic, educational, inspirational, humorous")
    include_storytelling: bool = Field(True, description="Include origin story/lore")
    language: str = Field("en", description="Output language")


class RecipeVariationRequest(BaseModel):
    """Recipe variation request"""
    base_recipe: str = Field(..., description="Base recipe text")
    variation_type: str = Field(..., description="Variation type: seasonal, fusion, simplified, premium")
    count: int = Field(3, ge=1, le=10, description="Number of variations")


class SocialContentRequest(BaseModel):
    """Social media content request"""
    topic: str = Field(..., description="Content topic")
    platform: str = Field(..., description="Platform: instagram, twitter, tiktok, facebook")
    count: int = Field(5, ge=1, le=20, description="Number of posts")
    include_hashtags: bool = Field(True, description="Include hashtags")
    language: str = Field("en", description="Output language")


class ContentBatchRequest(BaseModel):
    """Batch content generation request"""
    campaign_name: str = Field(..., description="Campaign name")
    product_ids: List[str] = Field(default_factory=list, description="Products to feature")
    formats: List[str] = Field(..., description="Content formats to generate")
    target_audience: str = Field("general", description="Target demographic")
    key_messages: List[str] = Field(default_factory=list, description="Key messages to include")
    language: str = Field("en", description="Output language")


# API Endpoints

@router.post("/video-script")
async def generate_video_script(request: VideoScriptRequest):
    """
    Generate AI-powered video script (Sora-style)

    Creates cinematic video scripts with:
    - Shot-by-shot breakdown
    - Visual descriptions (cinematography, lighting, movement)
    - Voiceover narration
    - Music/SFX notes
    - Emotional storytelling
    - Cultural context

    Perfect for:
    - Product videos
    - Brand storytelling
    - Educational content
    - Cultural heritage pieces
    """
    try:
        studio = get_content_studio()

        # Validate style
        try:
            style = VideoStyle(request.style)
        except ValueError:
            raise HTTPException(400, f"Invalid style. Options: {[s.value for s in VideoStyle]}")

        script = await studio.generate_video_script(
            product_id=request.product_id,
            topic=request.topic,
            duration_seconds=request.duration_seconds,
            style=style,
            target_audience=request.target_audience,
            language=request.language
        )

        return script.to_dict()

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Video script generation failed: {str(e)}")


@router.post("/atomize")
async def atomize_content(request: ContentAtomizationRequest):
    """
    Content Atomization - "Turkey Slice" Method

    Takes ONE pillar content piece and atomizes it into
    MULTIPLE micro-content pieces for different platforms.

    Example transformation:
    - 1 long blog post (2000 words)
    → 5 social media posts
    → 3 short video scripts
    → 2 email newsletters
    → 1 infographic outline

    Benefits:
    - Maximum content leverage
    - Multi-platform presence
    - Consistent messaging
    - Efficient content production

    Use cases:
    - Launch campaigns
    - Product announcements
    - Educational series
    - Brand storytelling
    """
    try:
        studio = get_content_studio()

        # Validate formats
        formats = []
        for format_str in request.output_formats:
            try:
                formats.append(ContentFormat(format_str))
            except ValueError:
                raise HTTPException(400, f"Invalid format: {format_str}")

        atomized = await studio.atomize_content(
            pillar_content=request.pillar_content,
            pillar_title=request.pillar_title,
            output_formats=formats,
            count_per_format=request.count_per_format
        )

        return {
            "pillar_title": request.pillar_title,
            "total_pieces": len(atomized),
            "atomized_content": [content.to_dict() for content in atomized]
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Content atomization failed: {str(e)}")


@router.post("/product-description")
async def generate_product_description(request: ProductDescriptionRequest):
    """
    Generate compelling product description

    AI-powered product copywriting with:
    - Sensory details (taste, aroma, texture)
    - Unique selling points
    - Origin story/heritage (optional)
    - Food pairing suggestions
    - Tasting notes
    - SEO optimization
    - Clear call-to-action

    Perfect for:
    - E-commerce product pages
    - Marketing materials
    - Email campaigns
    - Print catalogs
    """
    try:
        studio = get_content_studio()

        # Validate tone
        try:
            tone = ToneOfVoice(request.tone)
        except ValueError:
            raise HTTPException(400, f"Invalid tone. Options: {[t.value for t in ToneOfVoice]}")

        description = await studio.generate_product_description(
            product_id=request.product_id,
            length=request.length,
            tone=tone,
            include_storytelling=request.include_storytelling,
            language=request.language
        )

        return description.to_dict()

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Product description generation failed: {str(e)}")


@router.post("/recipe-variations")
async def generate_recipe_variations(request: RecipeVariationRequest):
    """
    Generate recipe variations

    Transform one base recipe into multiple variations:
    - **Seasonal**: Adapt for different seasons
    - **Fusion**: Blend with other cuisines
    - **Simplified**: Easier preparation
    - **Premium**: Elevated version

    Use cases:
    - Content creation
    - Product development ideas
    - Menu planning
    - Educational content
    """
    try:
        studio = get_content_studio()

        variations = await studio.variate_recipe(
            base_recipe=request.base_recipe,
            variation_type=request.variation_type,
            count=request.count
        )

        return {
            "variation_type": request.variation_type,
            "variations_count": len(variations),
            "variations": [v.to_dict() for v in variations]
        }

    except Exception as e:
        raise HTTPException(500, f"Recipe variation failed: {str(e)}")


@router.post("/social-content")
async def generate_social_content(request: SocialContentRequest):
    """
    Generate platform-optimized social media content

    Creates engaging posts tailored for each platform:

    **Instagram**:
    - Visual-first storytelling
    - 5-10 hashtags
    - Aspirational tone
    - Story-friendly

    **Twitter/X**:
    - Concise (280 chars)
    - 1-2 hashtags
    - Conversational
    - Thread-ready

    **TikTok**:
    - Hook in first 3 seconds
    - Trending audio notes
    - Fast-paced
    - Entertainment-focused

    **Facebook**:
    - Community-building
    - Longer-form OK
    - Discussion-starter
    - Group-friendly

    Each post includes:
    - Optimized copy
    - Hashtag suggestions
    - Best posting time
    - Estimated reach
    """
    try:
        studio = get_content_studio()

        # Validate platform
        valid_platforms = ["instagram", "twitter", "tiktok", "facebook"]
        if request.platform not in valid_platforms:
            raise HTTPException(400, f"Invalid platform. Options: {valid_platforms}")

        posts = await studio.generate_social_content(
            topic=request.topic,
            platform=request.platform,
            count=request.count,
            include_hashtags=request.include_hashtags,
            language=request.language
        )

        return {
            "platform": request.platform,
            "topic": request.topic,
            "posts_count": len(posts),
            "posts": [post.to_dict() for post in posts]
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Social content generation failed: {str(e)}")


@router.post("/batch")
async def generate_content_batch(request: ContentBatchRequest):
    """
    Batch content generation from campaign brief

    Generate complete content package for a campaign:
    - Multiple formats
    - Multiple products
    - Consistent messaging
    - Brand voice aligned

    Perfect for:
    - Product launches
    - Seasonal campaigns
    - Event promotions
    - Brand initiatives

    Example brief:
    ```json
    {
      "campaign_name": "Summer Makgeolli Collection",
      "product_ids": ["makgeolli_peach", "makgeolli_yuzu"],
      "formats": ["video_script", "social_post", "email"],
      "target_audience": "millennials",
      "key_messages": ["refreshing", "authentic", "summer-perfect"],
      "language": "en"
    }
    ```

    Returns complete content package with:
    - Video scripts
    - Social media posts
    - Email campaigns
    - Product descriptions
    - All optimized and ready to use
    """
    try:
        studio = get_content_studio()

        content_brief = {
            "campaign_name": request.campaign_name,
            "product_ids": request.product_ids,
            "formats": request.formats,
            "target_audience": request.target_audience,
            "key_messages": request.key_messages,
            "language": request.language
        }

        content_package = await studio.generate_content_batch(content_brief)

        return content_package

    except Exception as e:
        raise HTTPException(500, f"Batch generation failed: {str(e)}")


@router.get("/formats")
async def get_available_formats():
    """
    Get available content formats

    Returns list of all supported content formats
    with descriptions and use cases.
    """
    return {
        "formats": [
            {
                "value": "video_script",
                "label": "Video Script",
                "description": "Cinematic video scripts with shot-by-shot breakdown",
                "use_cases": ["Product videos", "Brand storytelling", "Educational content"]
            },
            {
                "value": "blog_post",
                "label": "Blog Post",
                "description": "Long-form SEO-optimized articles",
                "use_cases": ["SEO content", "Thought leadership", "Educational guides"]
            },
            {
                "value": "social_post",
                "label": "Social Media Post",
                "description": "Platform-optimized social content",
                "use_cases": ["Instagram", "Twitter", "TikTok", "Facebook"]
            },
            {
                "value": "email",
                "label": "Email",
                "description": "Email newsletters and campaigns",
                "use_cases": ["Newsletter", "Promotional email", "Welcome series"]
            },
            {
                "value": "product_description",
                "label": "Product Description",
                "description": "Compelling e-commerce product copy",
                "use_cases": ["Product pages", "Catalogs", "Marketing materials"]
            },
            {
                "value": "recipe",
                "label": "Recipe",
                "description": "Culinary recipes with variations",
                "use_cases": ["Content creation", "Product pairing", "Educational"]
            },
            {
                "value": "lore",
                "label": "Brand Lore",
                "description": "Cultural stories and brand heritage",
                "use_cases": ["Brand storytelling", "Heritage content", "About us"]
            },
            {
                "value": "short_form",
                "label": "Short-Form Video",
                "description": "15-60 second video scripts for TikTok/Reels/Shorts",
                "use_cases": ["TikTok", "Instagram Reels", "YouTube Shorts"]
            }
        ]
    }


@router.get("/styles")
async def get_video_styles():
    """
    Get available video styles

    Returns list of video production styles
    with descriptions and best use cases.
    """
    return {
        "styles": [
            {
                "value": "cinematic",
                "label": "Cinematic",
                "description": "Sora-style artistic, high production value",
                "best_for": "Brand films, emotional storytelling, premium products"
            },
            {
                "value": "educational",
                "label": "Educational",
                "description": "Tutorial-style, how-to, informative",
                "best_for": "Product guides, tutorials, explainers"
            },
            {
                "value": "documentary",
                "label": "Documentary",
                "description": "Storytelling, history, cultural context",
                "best_for": "Heritage stories, maker profiles, origin stories"
            },
            {
                "value": "energetic",
                "label": "Energetic",
                "description": "Fast-paced, engaging, dynamic",
                "best_for": "Product launches, events, youth audience"
            },
            {
                "value": "minimalist",
                "label": "Minimalist",
                "description": "Simple, clean, focused",
                "best_for": "Product features, clean aesthetic, modern brands"
            },
            {
                "value": "authentic",
                "label": "Authentic",
                "description": "Raw, genuine, behind-the-scenes",
                "best_for": "Process videos, maker stories, transparency"
            }
        ]
    }


@router.get("/tones")
async def get_tone_options():
    """
    Get available tone of voice options

    Returns list of tone options for content generation.
    """
    return {
        "tones": [
            {
                "value": "professional",
                "label": "Professional",
                "description": "Formal, authoritative, expert",
                "best_for": "B2B, corporate, premium products"
            },
            {
                "value": "casual",
                "label": "Casual",
                "description": "Relaxed, conversational, approachable",
                "best_for": "Social media, community content, everyday products"
            },
            {
                "value": "friendly",
                "label": "Friendly",
                "description": "Warm, welcoming, personable",
                "best_for": "Customer service, welcome messages, community"
            },
            {
                "value": "enthusiastic",
                "label": "Enthusiastic",
                "description": "Excited, energetic, passionate",
                "best_for": "Launches, promotions, events"
            },
            {
                "value": "educational",
                "label": "Educational",
                "description": "Informative, clear, helpful",
                "best_for": "Guides, tutorials, how-to content"
            },
            {
                "value": "inspirational",
                "label": "Inspirational",
                "description": "Motivating, aspirational, uplifting",
                "best_for": "Brand stories, mission statements, testimonials"
            },
            {
                "value": "humorous",
                "label": "Humorous",
                "description": "Witty, playful, entertaining",
                "best_for": "Social media, viral content, youth audience"
            }
        ]
    }


@router.get("/platforms")
async def get_platform_specs():
    """
    Get social media platform specifications

    Returns detailed specs for each platform:
    - Character limits
    - Best practices
    - Content styles
    - Posting guidelines
    """
    return {
        "platforms": [
            {
                "name": "instagram",
                "label": "Instagram",
                "char_limit": 2200,
                "best_practices": [
                    "Visual-first content",
                    "5-10 hashtags",
                    "Use emojis",
                    "Stories for behind-the-scenes",
                    "Reels for trending content"
                ],
                "style": "Aspirational, authentic, visually appealing",
                "best_times": ["6-9 AM", "12-2 PM", "5-7 PM"]
            },
            {
                "name": "twitter",
                "label": "Twitter/X",
                "char_limit": 280,
                "best_practices": [
                    "Concise messaging",
                    "1-2 hashtags max",
                    "Use threads for longer stories",
                    "Engage with replies"
                ],
                "style": "Conversational, witty, timely",
                "best_times": ["8-10 AM", "12-1 PM", "5-6 PM"]
            },
            {
                "name": "tiktok",
                "label": "TikTok",
                "char_limit": 150,
                "video_length": "15-60 seconds",
                "best_practices": [
                    "Hook in first 3 seconds",
                    "Use trending sounds",
                    "Fast-paced editing",
                    "Authentic, not polished"
                ],
                "style": "Entertaining, authentic, trend-driven",
                "best_times": ["6-10 AM", "7-11 PM"]
            },
            {
                "name": "facebook",
                "label": "Facebook",
                "char_limit": 63206,
                "best_practices": [
                    "Community-focused",
                    "Longer posts OK",
                    "Leverage groups",
                    "Encourage discussion"
                ],
                "style": "Conversational, community-focused, inclusive",
                "best_times": ["1-4 PM", "6-9 PM"]
            }
        ]
    }
