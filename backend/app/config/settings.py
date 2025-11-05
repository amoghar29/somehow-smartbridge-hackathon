from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "Personal Finance Bot"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = False
    
    # Database
    MONGODB_URL: str
    MONGODB_DB_NAME: str = "finance_bot"
    REDIS_URL: str = "redis://localhost:6379"
    
    # Security
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:8501"]
    
    # AI/ML
    HUGGINGFACE_API_KEY: str
    OPENAI_API_KEY: str = ""
    GRANITE_MODEL_NAME: str = "ibm-granite/granite-7b-base"
    GRANITE_EMBEDDING_MODEL: str = "ibm-granite/granite-embedding-125m-english"
    
    # Vector Store
    CHROMA_PERSIST_DIRECTORY: str = "./data/embeddings"
    CHROMA_COLLECTION_NAME: str = "finance_documents"
    
    # File Upload
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB
    ALLOWED_EXTENSIONS: List[str] = ["pdf", "txt", "doc", "docx", "csv", "xlsx"]
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_STORAGE_URL: str = "memory://"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


settings = get_settings()