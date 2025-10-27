"""
Embedding utilities for text processing
"""
import torch
from typing import List
from sentence_transformers import SentenceTransformer
from config.settings import get_settings


class EmbeddingService:
    """Service for generating text embeddings"""
    
    def __init__(self):
        self.settings = get_settings()
        self._model = None
        self.device = self._get_device()
    
    def _get_device(self) -> str:
        """Determine the best available device (GPU/CPU)"""
        if self.settings.force_cpu:
            print("Using CPU - forced by configuration")
            return "cpu"
            
        if torch.cuda.is_available():
            device = f"cuda:{torch.cuda.current_device()}"
            gpu_name = torch.cuda.get_device_name(torch.cuda.current_device())
            gpu_memory = torch.cuda.get_device_properties(torch.cuda.current_device()).total_memory / 1e9
            print(f"Using GPU: {gpu_name} ({gpu_memory:.1f}GB)")
            
            # Set GPU memory fraction
            if self.settings.gpu_memory_fraction < 1.0:
                torch.cuda.set_per_process_memory_fraction(self.settings.gpu_memory_fraction)
                print(f"GPU memory fraction set to {self.settings.gpu_memory_fraction}")
            
            return device
        elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            print("Using Apple Silicon GPU (MPS)")
            return "mps"
        else:
            print("Using CPU - GPU not available or not configured")
            return "cpu"
    
    def get_model(self) -> SentenceTransformer:
        """Get or initialize the embedding model"""
        if self._model is None:
            self._model = SentenceTransformer(self.settings.embedding_model, device=self.device)
            
            # Enable mixed precision for better GPU performance
            if self.device.startswith('cuda') and self.settings.use_mixed_precision:
                try:
                    self._model.half()  # Use FP16 for faster inference
                    print("Mixed precision (FP16) enabled for faster GPU inference")
                except Exception as e:
                    print(f"Warning: Could not enable mixed precision: {e}")
                    
        return self._model
    
    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        model = self.get_model()
        return model.encode([text])[0].tolist()
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        model = self.get_model()
        return model.encode(texts).tolist()
