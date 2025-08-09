from __future__ import annotations

"""Playground app para testar seus agentes localmente.

Execute:
  python playground.py

Isso inicia um servidor FastAPI em http://localhost:7777. Depois, abra
https://app.agno.com/playground, adicione o endpoint `localhost:7777/v1`
ecomece a conversar com o agente.
"""

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.playground import Playground

from src.core.config import get_settings

# ---------------------------------------------------------------------------
# Configurações
# ---------------------------------------------------------------------------
settings = get_settings()

# Cria o agente utilizando o mesmo prompt principal do DocResearcher
agent = Agent(
    name="doc_researcher",
    model=OpenAIChat(id=settings.openai_model),
    instructions=settings.agent_instructions,
    markdown=True,
)

# Cria o playground e expõe o FastAPI app
playground = Playground(agents=[agent])
app = playground.get_app()


if __name__ == "__main__":
    # O Playground adiciona automaticamente o prefixo /v1
    # Servir na porta padrão 7777
    playground.serve("playground:app", reload=True)