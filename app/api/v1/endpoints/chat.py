"""
Chat endpoints for AI-powered conversations
"""
from fastapi import APIRouter, HTTPException, Depends
from app.models.schemas import ChatRequest, ChatResponse
from app.services.chat.chat_service import ChatService
from app.core.dependencies import get_chat_service

router = APIRouter()


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    Chat with AI assistant about news content
    """
    try:
        response = await chat_service.generate_response(
            message=request.message,
            history=request.history
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")
