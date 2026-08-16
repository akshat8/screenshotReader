from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BACKEND_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    mongodb_uri: str = "mongodb://localhost:27017/screenshot_memory"

    pinecone_api_key: str = ""
    pinecone_index_name: str = "screenshot-memory"
    pinecone_dimension: int = 1024

    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_vision_model: str = "nvidia/nemotron-nano-12b-v2-vl:free"
    openrouter_llm_model: str = "nvidia/nemotron-nano-9b-v2:free"

    embedding_model: str = "BAAI/bge-large-en-v1.5"

    upload_dir: str = "./uploads"
    max_upload_count: int = 50
    max_file_size_mb: int = 10

    relevance_threshold: float = 0.35
    hybrid_semantic_weight: float = 0.7
    hybrid_keyword_weight: float = 0.3
    top_k: int = 5

    api_host: str = "0.0.0.0"
    api_port: int = 8000

    @property
    def upload_path(self) -> Path:
        path = Path(self.upload_dir)
        if not path.is_absolute():
            path = BACKEND_ROOT / path
        return path.resolve()


settings = Settings()
