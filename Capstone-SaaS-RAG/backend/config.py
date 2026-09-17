"""Central configuration loaded from environment variables / .env.

DEMO_MODE=true (default) makes every external integration (Claude, HF Inference API,
Cosmos DB) fall back to a local, deterministic, in-memory implementation so the app
is fully demoable to architects/management with zero cloud dependencies or API keys.
Flip DEMO_MODE=false and supply real credentials to run against live services.
"""
from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    demo_mode: bool = True

    anthropic_api_key: str = ""
    claude_model: str = "claude-sonnet-4-20250514"

    huggingfacehub_api_token: str = ""
    hf_embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"

    cosmos_endpoint: str = ""
    cosmos_key: str = ""
    cosmos_database: str = "genai_rag_demo"
    cosmos_container: str = "documents"

    faiss_index_path: str = "./backend/data/faiss_index"

    app_title: str = "Generative AI RAG SaaS — Architect Demo"

    @property
    def has_claude_credentials(self) -> bool:
        return bool(self.anthropic_api_key) and not self.demo_mode

    @property
    def has_hf_credentials(self) -> bool:
        return bool(self.huggingfacehub_api_token) and not self.demo_mode

    @property
    def has_cosmos_credentials(self) -> bool:
        return bool(self.cosmos_endpoint and self.cosmos_key) and not self.demo_mode


settings = Settings()
