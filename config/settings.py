"""
Application settings and configuration
"""
import os
from typing import List
from functools import lru_cache


class Settings():
    """Application settings"""
    
    # Server configuration
    host: str = "0.0.0.0"
    port: int = 8088
    debug: bool = False
    
    # CORS settings
    allowed_origins: List[str] = ["*"]
    
    # Database connections
    milvus_uri: str = os.getenv("MILVUS_URI", "")
    milvus_token: str = os.getenv("MILVUS_TOKEN", "")
    
    supabase_url: str = os.getenv("SUPABASE_URL", "")
    supabase_anon_key: str = os.getenv("SUPABASE_ANON_KEY", "")
    
    # External API keys
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    replicate_api_token: str = os.getenv("REPLICATE_API_TOKEN", "")
    
    # Model configuration
    embedding_model: str = "BAAI/bge-m3"
    
    # GPU configuration
    force_cpu: bool = os.getenv("FORCE_CPU", "false").lower() == "true"
    gpu_memory_fraction: float = float(os.getenv("GPU_MEMORY_FRACTION", "0.8"))
    use_mixed_precision: bool = os.getenv("USE_MIXED_PRECISION", "true").lower() == "true"
    
    # Search configuration
    default_top_k: int = 10
    max_search_results: int = 100
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore"
    }


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
