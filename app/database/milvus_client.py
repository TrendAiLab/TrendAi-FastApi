"""
Milvus database connection and operations
"""
from typing import List, Dict, Optional
from pymilvus import connections, Collection
from config.settings import get_settings


class MilvusClient:
    """Milvus database client"""
    
    def __init__(self):
        self.settings = get_settings()
        self._connection = None
        self._collection = None
    
    def connect(self) -> Collection:
        """Connect to Milvus and return collection"""
        if self._collection is None:
            connections.connect(
                uri=self.settings.milvus_uri,
                token=self.settings.milvus_token,
            )
            self._collection = Collection("content_items")
            self._collection.load()
        return self._collection
    
    def search(
        self, 
        query_vector: List[float], 
        top_k: int = 10,
        filter_expr: Optional[str] = None
    ) -> List[Dict]:
        """Search for similar vectors in Milvus"""
        collection = self.connect()
        
        results = collection.search(
            data=[query_vector],
            anns_field="embedding",
            param={"metric_type": "COSINE", "params": {"nprobe": 10}},
            limit=top_k,
            expr=filter_expr,
            output_fields=[
                "id", "type", "title", "description",
                "date", "time", "extra", "image"
            ],
            consistency_level="Strong",
        )
        
        formatted_results = []
        for hits in results:
            for hit in hits:
                formatted_results.append({
                    "id": hit.id,
                    "score": hit.score,
                    **{field: hit.entity.get(field) for field in [
                        "type", "title", "description", "date", "time", "extra", "image"
                    ]}
                })
        
        return formatted_results
    
    def query(
        self,
        expr: str,
        output_fields: List[str],
        limit: Optional[int] = None
    ) -> List[Dict]:
        """Query Milvus collection"""
        collection = self.connect()
        
        return collection.query(
            expr=expr,
            output_fields=output_fields,
            limit=limit,
            consistency_level="Strong",
        )
    
    def fetch_vectors(self, ids: List[int]) -> List[List[float]]:
        """Fetch embedding vectors for given IDs"""
        if not ids:
            return []
        
        try:
            collection = self.connect()
            
            # Convert IDs to match Milvus format
            milvus_ids = []
            for id_num in ids:
                milvus_ids.extend([f"article_{id_num}", f"video_{id_num}", str(id_num)])
            
            # Query with string IDs
            id_list_str = "', '".join(milvus_ids)
            expr = f"id in ['{id_list_str}']"
            
            rows = collection.query(
                expr=expr,
                output_fields=["embedding"],
                consistency_level="Strong",
            )
            
            return [row["embedding"] for row in rows]
        except Exception as e:
            print(f"Error fetching vectors: {e}")
            return []
