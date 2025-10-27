"""
Dependencies for API services
"""
from app.services.news.search_service import SearchService
from app.services.recommendations.recommendation_service import RecommendationService
from app.services.news.article_service import ArticleService
from app.services.chat.chat_service import ChatService


def get_search_service() -> SearchService:
    """
    Create and return a search service instance
    """
    return SearchService()


def get_recommendation_service() -> RecommendationService:
    """
    Create and return a recommendation service instance
    """
    return RecommendationService()


def get_article_service() -> ArticleService:
    """
    Create and return an article service instance
    """
    return ArticleService()


def get_chat_service() -> ChatService:
    """
    Create and return a chat service instance
    """
    return ChatService()
