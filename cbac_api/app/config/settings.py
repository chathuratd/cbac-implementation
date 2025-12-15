from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Database Configuration
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_COLLECTION: str = "user_behaviors"
    
    MONGODB_URL: str = "mongodb://admin:admin123@localhost:27017/"
    MONGODB_DATABASE: str = "cbac_system"
    MONGODB_COLLECTION_PROMPTS: str = "prompts"
    
    # Embedding Model
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384
    
    # Clustering Parameters
    MIN_CLUSTER_SIZE: int = 3
    MIN_SAMPLES: int = 2
    CLUSTER_SELECTION_EPSILON: float = 0.0
    
    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra environment variables


# Global settings instance
settings = Settings()
