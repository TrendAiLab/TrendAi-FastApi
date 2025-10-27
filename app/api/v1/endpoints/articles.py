"""
News articles endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
from app.models.schemas import ArticlesRequest, ArticlesResponse
from app.services.news.article_service import ArticleService
from app.core.dependencies import get_article_service

router = APIRouter()


@router.post("/", response_model=ArticlesResponse)
async def get_articles(
    request: ArticlesRequest,
    article_service: ArticleService = Depends(get_article_service)
):
    """
    Get paginated list of articles
    """
    try:
        articles = await article_service.get_articles(
            limit=request.limit,
            offset=request.offset,
            article_type=request.article_type
        )
        return ArticlesResponse(
            articles=articles,
            count=len(articles),
            limit=request.limit,
            offset=request.offset,
            type=request.article_type
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch articles: {str(e)}")
