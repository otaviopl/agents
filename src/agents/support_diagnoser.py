from __future__ import annotations

import json
import logging
from typing import List

from agno.agent import Agent
from src.agents.tools.n8n_webhook import N8nWebhookTool

from src.core.config import Settings


LOGGER = logging.getLogger(__name__)


class SupportDiagnoser:
    """Support agent for diagnosing issues using web search."""

    def __init__(self, settings: Settings) -> None:
        self.agent = Agent(
            name="support_diagnoser",
            instructions=settings.support_agent_instructions,
            tools=[N8nWebhookTool(settings).get_error_logs],
        )

    def diagnose(self, query: str) -> dict:
        """Diagnose an issue using web search."""
        prompt = (
            f"Diagnose the following support issue: {query}. "
            "You have access to a tool to retrieve error logs from an n8n webhook. "
            "When you use the n8n webhook tool, you will receive a JSON object containing an 'incidents' array. "
            "Each item in the 'incidents' array represents an n8n workflow execution incident with the following fields: "
            "workflow (full workflow name), count (number of occurrences), first_ts and last_ts (timestamp of first and last occurrence), "
            "responsibles (array of responsible user IDs), error_signatures (list of combinations of last executed node, error message, and count), "
            "and executions (list of executions with ts, last_node, error_message, execution_url). "
            "You MUST use the n8n webhook tool to retrieve error logs if the query seems related to system errors or logs. "
            "Analyze the 'incidents' data to diagnose the request. "
            "Provide a concise answer and relevant sources. "
            "Return JSON: {\"answer\": string, \"sources\": string[]}"
        )

        try:
            response = self.agent.run(prompt)
            content = getattr(response, "content", str(response)).strip()

            # Similar JSON parsing logic as in DocResearcher
            if content.startswith("```"):
                content = content.strip("` ")
                if content.lower().startswith("json"):
                    content = content[4:].strip()
                if content.endswith("```"):
                    content = content[:-3].strip()
            data = json.loads(content)
            if not isinstance(data, dict) or "answer" not in data or "sources" not in data:
                raise ValueError("Invalid JSON fields")
            return data
        except Exception as exc:
            LOGGER.error("SupportDiagnoser failed: %s", exc)
            return {"answer": "Diagnóstico indisponível", "sources": []}
