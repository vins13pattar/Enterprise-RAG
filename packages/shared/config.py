from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')
    database_url: str = 'sqlite:///./enterprise_rag.db'
    redis_url: str = 'redis://localhost:6379/0'
    qdrant_url: str = 'http://localhost:6333'
    minio_endpoint: str = 'localhost:9000'
    minio_access_key: str = 'minioadmin'
    minio_secret_key: str = 'minioadmin'
    minio_bucket: str = 'enterprise-rag'
    llm_provider: str = 'mock'
    llm_model: str = 'mock-grounded-v1'
    embedding_provider: str = 'mock'
    embedding_model: str = 'mock-embedding-v1'
    embedding_version: str = '2026-07-22'
    jwt_secret: str = Field(default='dev-secret')
    jwt_issuer: str = 'enterprise-rag'
    jwt_expire_minutes: int = 120
    human_review_threshold: float = 0.55
    retrieval_top_k: int = 5
    retrieval_fetch_k: int = 20
    retrieval_similarity_threshold: float = 0.15
    retrieval_mmr_lambda: float = 0.5
    upload_max_bytes: int = 10485760
    cors_origins: str = 'http://localhost:3000'
def get_settings(): return Settings()
