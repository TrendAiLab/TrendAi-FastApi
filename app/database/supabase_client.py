"""
Supabase database client
"""
from typing import List, Dict
from supabase import create_client, Client
from config.settings import get_settings


class SupabaseClient:
    """Supabase database client"""
    
    def __init__(self):
        self.settings = get_settings()
        self._client = None
    
    def get_client(self) -> Client:
        """Get Supabase client"""
        if self._client is None:
            self._client = create_client(
                self.settings.supabase_url,
                self.settings.supabase_anon_key,
            )
        return self._client
    
    def get_user_interactions(self, user_id: str) -> List[Dict]:
        """Get user interaction data"""
        client = self.get_client()
        
        # Get views/interactions
        views = (
            client.table("user_interactions")
            .select("article_id, interaction_score")
            .eq("user_id", user_id)
            .execute()
            .data
        )
        
        # Get bookmarks
        bookmarks = (
            client.table("bookmarks")
            .select("article_id")
            .eq("user_id", user_id)
            .execute()
            .data
        )
        
        # Combine and weight the signals
        weights = {}
        
        for view in views:
            article_id = view["article_id"]
            score = view.get("interaction_score", 1) or 1
            weights[article_id] = weights.get(article_id, 0) + score
        
        for bookmark in bookmarks:
            article_id = bookmark["article_id"]
            weights[article_id] = weights.get(article_id, 0) + 3  # Bookmarks have higher weight
        
        return [{"id": aid, "weight": w} for aid, w in weights.items()]
