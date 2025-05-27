from pydantic_settings import BaseSettings
from typing import Optional, Literal, List
import os

class Settings(BaseSettings):
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = False
    
    # CORS
    cors_origins: str = "http://localhost:3000,http://localhost:5173"
    
    # LLM Provider Configuration
    llm_provider: Literal["openai", "anthropic", "gemini", "ollama", "none"] = "none"
    
    # API Keys
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    
    # Model Configuration
    openai_model: str = "gpt-4.1-nano-2025-04-14"
    anthropic_model: str = "claude-3-haiku-20240307"
    gemini_model: str = "gemini-pro"
    ollama_model: str = "llama2"
    ollama_base_url: str = "http://localhost:11434"
    
    # Clustering Configuration
    max_concurrent_requests: int = 5
    clustering_timeout: int = 30
    min_clusters: int = 2
    max_clusters: int = 8
    embedding_model: str = "all-MiniLM-L6-v2"
    
    # Telegram Parsing
    posts_limit_per_channel: int = 50
    hours_back: int = 24
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Преобразует строку CORS origins в список"""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings() 