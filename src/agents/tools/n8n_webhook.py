from __future__ import annotations

import httpx

from agno.tools.decorator import tool
from agno.tools import Toolkit

from src.core.config import Settings


class N8nWebhookTool(Toolkit):
    """Toolkit que expõe a função `get_error_logs` para recuperar logs de erro via webhook n8n."""

    def __init__(self, settings: Settings):
        self.settings = settings

        # Registra a ferramenta (função) no Toolkit
        tool = self.get_error_logs
        entry = getattr(tool, "entrypoint", tool)
        if hasattr(tool, "name") and not hasattr(entry, "__name__"):
            setattr(entry, "__name__", tool.name)  # type: ignore[attr-defined]
        super().__init__(name="n8n_webhook", tools=[entry])

    @tool(name="get_n8n_error_logs", description="Recupera logs de erro do webhook n8n configurado em N8N_WEBHOOK_URL")
    def get_error_logs(self) -> str:  # type: ignore[override]
        """Busca logs de erro no webhook n8n indicado em settings.n8n_webhook_url."""

        if not getattr(self.settings, "n8n_webhook_url", None):
            return "n8n webhook URL não configurada."

        try:
            response = httpx.get(self.settings.n8n_webhook_url, timeout=10)
            response.raise_for_status()
            return response.text
        except httpx.RequestError as e:
            return f"Erro ao buscar logs no webhook n8n: {e}"