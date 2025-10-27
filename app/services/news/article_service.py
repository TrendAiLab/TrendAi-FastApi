"""
Article service for fetching articles
"""
from typing import List
from app.database.milvus_client import MilvusClient
from app.models.schemas import Article


class ArticleService:
    """Service for fetching articles"""
    
    def __init__(self):
        self.milvus_client = MilvusClient()
    
    async def get_articles(
        self, 
        limit: int = 10, 
        offset: int = 0, 
        article_type: str = "article"
    ) -> List[Article]:
        """Fetch paginated articles from Milvus"""
        try:
            # Build filter expression for type
            filter_expr = f'type == "{article_type}"'
            
            # Query articles with pagination
            # Note: Milvus doesn't have direct offset/limit for query, so we'll use a workaround
            fetch_limit = limit + offset
            
            rows = self.milvus_client.query(
                expr=filter_expr,
                output_fields=["id", "type", "title", "description", "date", "time", "extra", "image"],
                limit=fetch_limit
            )
            
            # Apply offset and limit manually
            paginated_rows = rows[offset:offset + limit]
            
            # Format results to Article objects
            articles = []
            for row in paginated_rows:
                # Handle image field - try both direct image field and from extra
                image_url = row.get("image", "")
                if not image_url and row.get("extra"):
                    try:
                        import json
                        extra_data = json.loads(row["extra"]) if isinstance(row["extra"], str) else row["extra"]
                        image_url = extra_data.get("image", "")
                    except:
                        image_url = ""
                
                article = Article(
                    id=row["id"],
                    type=row["type"],
                    title=row["title"],
                    description=row.get("description", ""),
                    date=row.get("date", ""),
                    time=row.get("time", ""),
                    image=image_url,
                    extra={
                        "image": image_url,
                        "categorieLabel": "",
                        "videoId": None,
                        "typeVideo": None,
                        "isVideo": row["type"] == "video"
                    },
                    score=1.0  # Default score since this is not a semantic search
                )
                articles.append(article)
            
            return articles
        
        except Exception as e:
            print(f"Error fetching articles from Milvus: {e}")
            return []
