"""
Chat service for AI-powered conversations
"""
import os
from typing import List
from app.database.milvus_client import MilvusClient
from app.utils.embedding_utils import EmbeddingService
from app.models.schemas import ChatTurn, ChatResponse, Article
from config.settings import get_settings


class ChatService:
    """Service for AI-powered chat functionality"""
    
    def __init__(self):
        self.milvus_client = MilvusClient()
        self.embedding_service = EmbeddingService()
        self.settings = get_settings()
    
    async def generate_response(self, message: str, history: List[ChatTurn]) -> ChatResponse:
        """Generate AI response based on message and context"""
        try:
            # Search for relevant content
            message_vector = self.embedding_service.embed_text(message)
            search_results = self.milvus_client.search(
                query_vector=message_vector,
                top_k=5
            )
            
            # Filter relevant results (score > 0.5)
            relevant_results = [
                result for result in search_results 
                if result.get("score", 0) > 0.5
            ]
            
            if not relevant_results:
                return ChatResponse(
                    response="Désolé, je n'ai rien trouvé.",
                    sources=[]
                )
            
            # Build context from relevant results
            context = "\n".join([
                f"[{result['title']}] : {result.get('description', '')}" 
                for result in relevant_results
            ])
            
            # Build conversation history
            conversation_history = "\n".join([
                f"Utilisateur : {turn.user}\nAssistant : {turn.bot}"
                for turn in history[-4:]  # Last 4 turns
            ])
            
            # Generate response using Groq
            prompt = f"""
Contexte :
{context}

Historique :
{conversation_history}

Question : {message}

— Réponds uniquement via le contexte ci‑dessus —
"""
            
            ai_response = self._call_groq_api(prompt)
            
            # Convert results to Article objects for sources
            sources = []
            for result in relevant_results[:5]:
                image_url = result.get("image", "")
                if not image_url and result.get("extra"):
                    try:
                        import json
                        extra_data = json.loads(result["extra"]) if isinstance(result["extra"], str) else result["extra"]
                        image_url = extra_data.get("image", "")
                    except:
                        image_url = ""
                
                article = Article(
                    id=result["id"],
                    type=result["type"],
                    title=result["title"],
                    description=result.get("description", ""),
                    date=result.get("date", ""),
                    time=result.get("time", ""),
                    image=image_url,
                    extra={
                        "image": image_url,
                        "categorieLabel": "",
                        "videoId": None,
                        "typeVideo": None,
                        "isVideo": result["type"] == "video"
                    },
                    score=result.get("score", 0.0)
                )
                sources.append(article)
            
            return ChatResponse(
                response=ai_response,
                sources=sources
            )
            
        except Exception as e:
            print(f"Error in generate_response: {e}")
            return ChatResponse(
                response=f"Erreur lors de la génération de la réponse: {str(e)}",
                sources=[]
            )
    
    def _call_groq_api(self, prompt: str) -> str:
        """Call Groq API for text generation"""
        try:
            from groq import Groq
            
            if not self.settings.groq_api_key:
                return "Configuration manquante : token Groq absent."
            
            client = Groq(api_key=self.settings.groq_api_key)
            
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Tu es un assistant qui répond en français. "
                            "Réponds de manière concise en te basant sur le contexte."
                        )
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=1024,
                top_p=1.0,
            )
            
            return completion.choices[0].message.content
            
        except Exception as e:
            return f"Erreur Groq : {e}"
