"""
Search service for content search functionality
"""
import re
from typing import List, Tuple
from app.database.milvus_client import MilvusClient
from app.utils.embedding_utils import EmbeddingService
from app.models.schemas import Article


class SearchService:
    """Service for searching news content"""
    
    def __init__(self):
        self.milvus_client = MilvusClient()
        self.embedding_service = EmbeddingService()
    
    def classify_intent(self, query: str) -> Tuple[str, float, str]:
        """Classify the intent of the search query"""
        q = query.lower()
        
        if any(w in q for w in ["video", "film", "movie", "watch", "vod"]):
            return "vod_search", 0.8, "Recherche VOD/vidéo"
        elif any(w in q for w in ["score", "result", "match result"]):
            return "match_score", 0.8, "Résultat d'un match"
        elif any(w in q for w in ["schedule", "when", "time", "date"]):
            return "match_schedule", 0.8, "Horaire d'un match"
        elif any(w in q for w in ["news", "latest", "recent"]):
            return "latest_news", 0.8, "Actualités récentes"
        elif any(w in q for w in ["program", "show", "broadcast"]):
            return "program_information", 0.8, "Info programme"
        else:
            return "generic_search", 0.6, "Recherche générique"
    
    async def search(self, query: str, top_k: int = 10) -> List[Article]:
        """Search for content based on query"""
        # Classify intent and prepare filters
        intent, confidence, description = self.classify_intent(query)
        
        # Generate embedding for the query
        query_vector = self.embedding_service.embed_text(query)
        
        # Build filter expression based on intent and query
        filter_expr = None
        year_match = re.search(r"\b(20\d{2}|19\d{2})\b", query)
        year = year_match.group(0) if year_match else None
        
        if intent == "vod_search":
            filter_expr = 'type == "video"'
            if year:
                filter_expr += f' AND date LIKE "{year}%"'
        
        # Search in Milvus
        results = self.milvus_client.search(
            query_vector=query_vector,
            top_k=top_k * 2,  # Over-fetch for better results
            filter_expr=filter_expr
        )
        
        # Convert to Article objects
        articles = []
        for result in results[:top_k]:
            # Handle image field
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
            articles.append(article)
        
        return articles
