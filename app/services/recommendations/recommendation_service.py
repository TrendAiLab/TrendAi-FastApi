"""
Recommendation service for personalized content
"""
from typing import List, Optional
from app.database.milvus_client import MilvusClient
from app.database.supabase_client import SupabaseClient
from app.services.news.article_service import ArticleService
from app.utils.embedding_utils import EmbeddingService
from app.models.schemas import Article


class RecommendationService:
    """Service for generating personalized recommendations"""
    
    def __init__(self):
        self.milvus_client = MilvusClient()
        self.supabase_client = SupabaseClient()
        self.article_service = ArticleService()
        self.embedding_service = EmbeddingService()
    
    async def get_recommendations(self, user_id: str, top_k: int = 10) -> List[Article]:
        """Get personalized recommendations for a user"""
        try:
            print(f"Getting recommendations for user: {user_id}")
            
            # Get user interactions and build user vector
            user_vector = await self._build_user_vector(user_id)
            
            # If no user vector, use fallback strategies
            if user_vector is None:
                return await self._fallback_recommendations(user_id, top_k)
            
            print(f"User vector built successfully, dimension: {len(user_vector)}")
            
            # Over-fetch, then filter already-seen
            recommendations = self.milvus_client.search(
                query_vector=user_vector,
                top_k=top_k + 20
            )
            
            print(f"Found {len(recommendations)} recommendations from Milvus")
            
            # Filter out articles user has already seen
            user_interactions = self.supabase_client.get_user_interactions(user_id)
            seen_ids = {str(interaction["id"]) for interaction in user_interactions}
            
            fresh_recommendations = [
                rec for rec in recommendations 
                if str(rec["id"]) not in seen_ids
            ][:top_k]
            
            print(f"Filtered to {len(fresh_recommendations)} fresh recommendations")
            
            # Convert to Article objects
            articles = []
            for rec in fresh_recommendations:
                image_url = rec.get("image", "")
                if not image_url and rec.get("extra"):
                    try:
                        import json
                        extra_data = json.loads(rec["extra"]) if isinstance(rec["extra"], str) else rec["extra"]
                        image_url = extra_data.get("image", "")
                    except:
                        image_url = ""
                
                article = Article(
                    id=rec["id"],
                    type=rec["type"],
                    title=rec["title"],
                    description=rec.get("description", ""),
                    date=rec.get("date", ""),
                    time=rec.get("time", ""),
                    image=image_url,
                    extra={
                        "image": image_url,
                        "categorieLabel": "",
                        "videoId": None,
                        "typeVideo": None,
                        "isVideo": rec["type"] == "video"
                    },
                    score=rec.get("score", 0.0)
                )
                articles.append(article)
            
            return articles
            
        except Exception as e:
            print(f"Error in get_recommendations: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    async def _build_user_vector(self, user_id: str) -> Optional[List[float]]:
        """Build user vector from interaction history"""
        user_interactions = self.supabase_client.get_user_interactions(user_id)
        print(f"DEBUG - User {user_id} has {len(user_interactions)} interactions: {user_interactions}")
        
        if not user_interactions:
            return None
        
        article_ids = [interaction["id"] for interaction in user_interactions]
        print(f"DEBUG - Looking for vectors for article IDs: {article_ids}")
        
        vectors = self.milvus_client.fetch_vectors(article_ids)
        print(f"DEBUG - Found {len(vectors)} vectors for {len(article_ids)} articles")
        
        if not vectors:
            return None
        
        # Calculate weighted average of vectors
        dim = len(vectors[0])
        weighted_sum = [0.0] * dim
        total_weight = 0
        
        for interaction, vector in zip(user_interactions, vectors):
            weight = interaction["weight"]
            total_weight += weight
            for i in range(dim):
                weighted_sum[i] += weight * vector[i]
        
        return [x / total_weight for x in weighted_sum]
    
    async def _fallback_recommendations(self, user_id: str, top_k: int) -> List[Article]:
        """Fallback recommendation strategies when no user vector is available"""
        user_interactions = self.supabase_client.get_user_interactions(user_id)
        
        if not user_interactions:
            # No interactions at all - return general popular articles
            return await self.article_service.get_articles(limit=top_k, article_type="article")
        
        # User has interactions but no vectors - try semantic search based on keywords
        keywords = self._extract_keywords_from_interactions(user_interactions, limit=5)
        
        if keywords:
            # Create search query from extracted keywords
            search_query = " ".join(keywords)
            print(f"Fallback search using extracted keywords: {search_query}")
            
            keyword_vector = self.embedding_service.embed_text(search_query)
            fallback_recs = self.milvus_client.search(
                query_vector=keyword_vector,
                top_k=top_k * 2
            )
        else:
            # If no keywords extracted, fall back to general popular articles
            return await self.article_service.get_articles(limit=top_k * 2, article_type="article")
        
        # Filter out any articles the user has already seen
        seen_ids = {str(interaction["id"]) for interaction in user_interactions}
        fresh_fallback = [
            rec for rec in fallback_recs 
            if str(rec["id"]) not in seen_ids
        ][:top_k]
        
        # Convert to Article objects
        articles = []
        for rec in fresh_fallback:
            article = Article(
                id=rec["id"],
                type=rec["type"],
                title=rec["title"],
                description=rec.get("description", ""),
                date=rec.get("date", ""),
                time=rec.get("time", ""),
                image=rec.get("image", ""),
                extra=rec.get("extra", {}),
                score=rec.get("score", 0.0)
            )
            articles.append(article)
        
        return articles
    
    def _extract_keywords_from_interactions(self, user_interactions: List[dict], limit: int = 5) -> List[str]:
        """Extract keywords from user's latest interactions"""
        try:
            # Get article IDs from latest interactions (sorted by weight/recency)
            article_ids = [
                interaction["id"] for interaction in sorted(
                    user_interactions, key=lambda x: x["weight"], reverse=True
                )[:limit]
            ]
            
            if not article_ids:
                return []
            
            # Fetch article details from Milvus
            milvus_ids = []
            for id_num in article_ids:
                milvus_ids.extend([f"article_{id_num}", f"video_{id_num}", str(id_num)])
            
            id_list_str = "', '".join(milvus_ids)
            expr = f"id in ['{id_list_str}']"
            
            rows = self.milvus_client.query(
                expr=expr,
                output_fields=["title", "description"]
            )
            
            # Count keyword frequency across all articles
            keyword_counts = {}
            
            for row in rows:
                # Extract from title (give title keywords more weight)
                if row.get("title"):
                    title_keywords = self._extract_capitalized_words(row["title"])
                    for keyword in title_keywords:
                        keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 2  # Title gets 2x weight
                
                # Extract from description
                if row.get("description"):
                    desc_keywords = self._extract_capitalized_words(row["description"])
                    for keyword in desc_keywords:
                        keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
            
            # Only keep keywords that appear 3+ times
            frequent_keywords = [keyword for keyword, count in keyword_counts.items() if count >= 3]
            
            # Sort by frequency and return top keywords
            frequent_keywords.sort(key=lambda k: keyword_counts[k], reverse=True)
            
            print(f"Keyword frequency analysis: {keyword_counts}")
            print(f"Frequent keywords (3+ occurrences): {frequent_keywords}")
            
            # Return top 5 most frequent keywords
            return frequent_keywords[:5]
            
        except Exception as e:
            print(f"Error extracting keywords from interactions: {e}")
            return []
    
    def _extract_capitalized_words(self, text: str) -> List[str]:
        """Extract words that start with capital letters from text"""
        if not text:
            return []
        
        import re
        # Find words that start with capital letters
        pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'
        matches = re.findall(pattern, text)
        
        # Filter out common words and short words
        stop_words = {
            'The', 'Le', 'La', 'Les', 'Un', 'Une', 'Des', 'Du', 'De', 
            'Et', 'Ou', 'Pour', 'Par', 'Sur', 'Avec', 'Dans', 'Sans'
        }
        
        keywords = []
        for match in matches:
            # Skip if it's a stop word or too short
            if match not in stop_words and len(match) > 2:
                keywords.append(match)
        
        return keywords
