"""
Recommendation endpoints for personalized content
"""
from fastapi import APIRouter, HTTPException, Depends
from app.models.schemas import RecommendationRequest, RecommendationResponse
from app.services.recommendations.recommendation_service import RecommendationService
from app.core.dependencies import get_recommendation_service

router = APIRouter()


@router.post("/", response_model=RecommendationResponse)
async def get_recommendations(
    request: RecommendationRequest,
    rec_service: RecommendationService = Depends(get_recommendation_service)
):
    """
    Get personalized recommendations for a user
    """
    try:
        results = await rec_service.get_recommendations(
            user_id=request.user_id,
            top_k=request.top_k
        )
        return RecommendationResponse(
            user_id=request.user_id,
            results=results,
            count=len(results)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendation failed: {str(e)}")
