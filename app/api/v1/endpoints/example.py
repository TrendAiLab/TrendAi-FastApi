"""
Example endpoints for testing
"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def example_endpoint():
    """Example endpoint for testing"""
    return {"message": "Hello from Trend AI Server!"}
