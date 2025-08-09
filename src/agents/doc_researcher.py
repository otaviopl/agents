from __future__ import annotations

import json
import logging
from typing import List

from agno.agent import Agent
# from agno.tools.duckduckgo import DuckDuckGoTools

from src.core.config import Settings


LOGGER = logging.getLogger(__name__)


class DocResearcher:
    """Level-1 support agent using Agno.

    It has two public methods: handle_local and handle_web_fallback.
    """

    def __init__(self, settings: Settings) -> None:
        self.agent = Agent(
            name="doc_researcher",
            instructions=settings.agent_instructions,
            tools=[],
        )

    def handle_local(self, query: str, passages: List[str], sources: List[str]) -> dict:
        """Force the response to only use provided passages as context."""
        if not passages:
            return {"answer": "Não encontrado", "sources": []}

        context = "\n\n".join(passages)
        prompt = (
            "Contexto:\n" + context + "\n\n" +
            "Pergunta: " + query + "\n" +
            "Instruções: Responda apenas com base no Contexto e sempre em Português do Brasil. "
            "Retorne JSON: {\"answer\": string, \"sources\": string[]}"
        )

        response = self.agent.run(prompt)
        content = getattr(response, "content", str(response)).strip()
        # remove markdown ```json fences if present
        if content.startswith("```"):
            content = content.strip("` ")
            if content.lower().startswith("json"):
                content = content[4:].strip()
            # remove trailing ``` if exists
            if content.endswith("```"):
                content = content[:-3].strip()
        try:
            data = json.loads(content)
            if not isinstance(data, dict) or "answer" not in data or "sources" not in data:
                raise ValueError("Invalid JSON fields")
            # override sources with local file paths provided
            data["sources"] = sources
            return data
        except Exception:
            # Fallback: wrap content into expected JSON
            return {"answer": content, "sources": sources}

    # def handle_web_fallback(self, query: str) -> dict:
    #     """Handle a query using the web search tool."""
    #     response = self.agent.run(query)
    #     content = getattr(response, "content", str(response)).strip()
    #     if content.startswith("```"):
    #         content = content.strip("` ")
    #         if content.lower().startswith("json"):
    #             content = content[4:].strip()
    #         if content.endswith("```"):
    #             content = content[:-3].strip()
    #     try:
    #         data = json.loads(content)
    #         if not isinstance(data, dict) or "answer" not in data or "sources" not in data:
    #             raise ValueError("Invalid JSON fields")
    #         return data
    #     except Exception:
    #         return {"answer": content, "sources": []}

