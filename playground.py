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
from src.agents.doc_researcher import DocResearcher
from src.agents.support_diagnoser import SupportDiagnoser
from src.workflows.support_workflow import SupportWorkflow

# ---------------------------------------------------------------------------
# Configurações
# ---------------------------------------------------------------------------
settings = get_settings()

# Instâncias reutilizadas
doc_researcher = DocResearcher(settings)
support_diagnoser = SupportDiagnoser(settings)

# Workflow
support_workflow = SupportWorkflow(
    support_diagnoser=support_diagnoser,
    doc_researcher=doc_researcher,
)

agent = doc_researcher.agent  # Agente interno já configurado

# Cria o playground incluindo o workflow de suporte
playground = Playground(agents=[agent], workflows=[support_workflow])
app = playground.get_app()


if __name__ == "__main__":
    # O Playground adiciona automaticamente o prefixo /v1
    # Servir na porta padrão 7777
    playground.serve("playground:app", reload=True)