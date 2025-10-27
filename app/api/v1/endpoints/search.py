"""
Search endpoints for news and content search
"""
from fastapi import APIRouter, HTTPException, Depends
from app.models.schemas import SearchQuery, SearchResponse
from app.services.news.search_service import SearchService
from app.core.dependencies import get_search_service

router = APIRouter()


@router.post("/", response_model=SearchResponse)
async def search_content(
    query: SearchQuery,
    search_service: SearchService = Depends(get_search_service)
):
    """
    Search for news articles and content based on semantic similarity
    """
    try:
        results = await search_service.search(query.query, query.top_k)
        return SearchResponse(
            query=query.query,
            results=results,
            count=len(results)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")
