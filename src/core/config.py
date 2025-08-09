"""
Core configuration for the Agno Doc Bot
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    docs_dir: str = "./docs"
    log_level: str = "INFO"
    k: int = 5
    index_path: str = ".local_index.pkl"
    api_port: int = 8088
    allowed_domains: list[str] = list
    agent_instructions: str = """You are a Level 1 support agent. Your main goal is to answer questions based on the provided documentation.

You should look for answers in the following sources:
- The provided text snippets from the local documentation.
- The allowed websites.

When you answer, you should always cite your sources.

If you can't find an answer, you should say so.
"""

    openai_api_key: Optional[str] = None
    openai_base_url: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")


def get_settings() -> Settings:
    load_dotenv()
    docs_dir = os.getenv("DOCS_DIR", "./docs")
    log_level = os.getenv("LOG_LEVEL", "INFO")
    k = int(os.getenv("K", "5"))
    index_path = os.getenv("INDEX_PATH", ".local_index.pkl")
    api_port = int(os.getenv("API_PORT", "8088"))
    allowed_domains = os.getenv("ALLOWED_DOMAINS", "notion.site,notion.so,www.notion.so").split(",")
    agent_instructions = os.getenv("AGENT_INSTRUCTIONS", """You are a Level 1 support agent. Your main goal is to answer questions based on the provided documentation.

You should look for answers in the following sources:
- The provided text snippets from the local documentation.
- The allowed websites.

When you answer, you should always cite your sources.

If you can't find an answer, you should say so.
""")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    openai_base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    openai_model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

    return Settings(
        docs_dir=docs_dir,
        log_level=log_level,
        k=k,
        index_path=index_path,
        api_port=api_port,
        allowed_domains=allowed_domains,
        agent_instructions=agent_instructions,
        openai_api_key=openai_api_key,
        openai_base_url=openai_base_url,
        openai_model=openai_model,
    )

