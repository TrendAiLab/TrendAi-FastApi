"""
API router setup for v1
"""
from fastapi import APIRouter
from app.api.v1.endpoints import search, recommendations, articles, chat, example

api_router = APIRouter()
api_router.include_router(search.router, prefix="/search", tags=["search"])
api_router.include_router(recommendations.router, prefix="/recommendations", tags=["recommendations"])
api_router.include_router(articles.router, prefix="/articles", tags=["articles"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(example.router, prefix="/example", tags=["example"])

