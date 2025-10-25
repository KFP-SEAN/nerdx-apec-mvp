"""
Helios Specialized Agent Models

Data models for Zeitgeist, Bard, and Master Planner agents.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

from models.helios.usage_models import ModelType


class AgentType(str, Enum):
    """Types of specialized agents"""
    ZEITGEIST = "zeitgeist"  # Market analysis
    BARD = "bard"  # Brand storytelling
    MASTER_PLANNER = "master_planner"  # Multi-agent orchestration


class AgentStatus(str, Enum):
    """Agent execution status"""
    IDLE = "idle"
    THINKING = "thinking"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"


class TrendCategory(str, Enum):
    """Market trend categories"""
    TECHNOLOGY = "technology"
    CONSUMER_BEHAVIOR = "consumer_behavior"
    INDUSTRY = "industry"
    COMPETITIVE = "competitive"
    REGULATORY = "regulatory"
    ECONOMIC = "economic"


class ContentType(str, Enum):
    """Brand content types"""
    BRAND_STORY = "brand_story"
    CAMPAIGN = "campaign"
    SOCIAL_MEDIA = "social_media"
    BLOG_POST = "blog_post"
    EMAIL = "email"
    VIDEO_SCRIPT = "video_script"


# Zeitgeist Agent Models

class MarketTrend(BaseModel):
    """Represents a market trend"""
    trend_id: str
    title: str
    description: str
    category: TrendCategory
    confidence: float = Field(ge=0.0, le=1.0)
    impact_score: float = Field(ge=0.0, le=10.0)
    time_horizon: str  # "short-term", "mid-term", "long-term"
    data_sources: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)
    detected_at: datetime = Field(default_factory=datetime.utcnow)


class ZeitgeistAnalysisRequest(BaseModel):
    """Request for Zeitgeist market analysis"""
    analysis_id: str
    industry: str
    region: Optional[str] = "global"
    time_period: str = "last_30_days"
    focus_areas: List[str] = Field(default_factory=list)
    competitors: List[str] = Field(default_factory=list)
    depth: str = "standard"  # "quick", "standard", "deep"


class ZeitgeistAnalysisResponse(BaseModel):
    """Response from Zeitgeist analysis"""
    analysis_id: str
    status: AgentStatus
    trends: List[MarketTrend] = Field(default_factory=list)
    key_insights: List[str] = Field(default_factory=list)
    opportunities: List[Dict[str, Any]] = Field(default_factory=list)
    threats: List[Dict[str, Any]] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)

    # Metadata
    industry: str
    region: str
    analyzed_at: datetime = Field(default_factory=datetime.utcnow)
    model_used: ModelType
    confidence: float = Field(ge=0.0, le=1.0)
    processing_time_seconds: float


# Bard Agent Models

class BrandVoice(BaseModel):
    """Brand voice characteristics"""
    tone: str  # "professional", "casual", "inspirational", etc.
    personality_traits: List[str]
    values: List[str]
    target_audience: str
    do_list: List[str] = Field(default_factory=list)
    dont_list: List[str] = Field(default_factory=list)


class ContentRequest(BaseModel):
    """Request for Bard content generation"""
    content_id: str
    content_type: ContentType
    topic: str
    brief: str
    brand_voice: Optional[BrandVoice] = None
    target_length: Optional[int] = None  # words
    keywords: List[str] = Field(default_factory=list)
    style_references: List[str] = Field(default_factory=list)
    constraints: Dict[str, Any] = Field(default_factory=dict)


class GeneratedContent(BaseModel):
    """Generated content piece"""
    content_id: str
    content_type: ContentType
    title: Optional[str] = None
    body: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

    # Quality metrics
    readability_score: Optional[float] = None
    sentiment_score: Optional[float] = None
    keyword_density: Dict[str, float] = Field(default_factory=dict)

    # Generation info
    model_used: ModelType
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    revision_number: int = 0


class BardContentResponse(BaseModel):
    """Response from Bard content generation"""
    content_id: str
    status: AgentStatus
    content: Optional[GeneratedContent] = None
    alternatives: List[GeneratedContent] = Field(default_factory=list)

    # Metadata
    processing_time_seconds: float
    tokens_used: int
    cost_estimate: float


# Master Planner Models

class AgentTask(BaseModel):
    """Task for a specific agent"""
    task_id: str
    agent_type: AgentType
    action: str
    parameters: Dict[str, Any]
    priority: int = Field(ge=1, le=10, default=5)
    depends_on: List[str] = Field(default_factory=list)

    # Execution tracking
    status: AgentStatus = AgentStatus.IDLE
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class Goal(BaseModel):
    """High-level goal for Master Planner"""
    goal_id: str
    description: str
    objective: str
    success_criteria: List[str]
    deadline: Optional[datetime] = None

    # Decomposed tasks
    tasks: List[AgentTask] = Field(default_factory=list)

    # Execution tracking
    status: AgentStatus = AgentStatus.IDLE
    progress_percentage: float = Field(ge=0.0, le=100.0, default=0.0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class GoalCreationRequest(BaseModel):
    """Request to create a goal"""
    description: str
    objective: str
    success_criteria: List[str]
    deadline: Optional[datetime] = None
    context: Dict[str, Any] = Field(default_factory=dict)


class GoalExecutionResponse(BaseModel):
    """Response from goal execution"""
    goal_id: str
    status: AgentStatus
    progress_percentage: float
    completed_tasks: int
    total_tasks: int
    current_task: Optional[AgentTask] = None
    results: Dict[str, Any] = Field(default_factory=dict)

    # Resource usage
    total_tokens_used: int
    total_cost: float
    execution_time_seconds: float


# Unified Agent Response

class AgentResponse(BaseModel):
    """Unified response from any agent"""
    agent_type: AgentType
    request_id: str
    status: AgentStatus
    result: Dict[str, Any]

    # Resource tracking
    model_used: ModelType
    tokens_used: int
    cost_estimate: float
    cache_hit: bool = False
    cache_layer: Optional[str] = None

    # Timing
    started_at: datetime
    completed_at: datetime
    processing_time_seconds: float

    # Quality
    confidence: float = Field(ge=0.0, le=1.0)
    error: Optional[str] = None
