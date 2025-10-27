"""
Pydantic schemas for API request/response models
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# Base models
class Article(BaseModel):
    """Article model"""
    id: str
    type: str
    title: str
    description: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    image: Optional[str] = None
    extra: Optional[Dict[str, Any]] = None
    score: Optional[float] = None


class ChatTurn(BaseModel):
    """Chat history turn"""
    user: str
    bot: str


# Request models
class SearchQuery(BaseModel):
    """Search query request"""
    query: str
    top_k: int = Field(default=10, le=100)


class RecommendationRequest(BaseModel):
    """Recommendation request"""
    user_id: str
    top_k: int = Field(default=10, le=100)


class ArticlesRequest(BaseModel):
    """Articles request"""
    limit: int = Field(default=10, le=100)
    offset: int = Field(default=0, ge=0)
    article_type: str = Field(default="article", pattern="^(article|video)$")


class ChatRequest(BaseModel):
    """Chat request"""
    message: str
    history: List[ChatTurn] = Field(default_factory=list)


# Response models
class SearchResponse(BaseModel):
    """Search response"""
    query: str
    results: List[Article]
    count: int
    intent: Optional[str] = None
    confidence: Optional[float] = None
    description: Optional[str] = None
    message: Optional[str] = None


class RecommendationResponse(BaseModel):
    """Recommendation response"""
    user_id: str
    results: List[Article]
    count: int
    fallback: Optional[str] = None


class ArticlesResponse(BaseModel):
    """Articles response"""
    articles: List[Article]
    count: int
    limit: int
    offset: int
    type: str


class ChatResponse(BaseModel):
    """Chat response"""
    response: str
    sources: List[Article] = Field(default_factory=list)
