from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "HookLens AI"
    debug: bool = False
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    data_dir: str = "./data"
    whisper_model_size: str = "base"

    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "hooklens_chunks"
    embedding_model: str = "all-MiniLM-L6-v2"
    chunk_max_chars: int = 480
    chunk_overlap_chars: int = 80
    retrieval_top_k: int = 8

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"
    checkpoint_db_path: str = "./data/checkpoints.db"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
