"""Workflow that orchestrates support diagnosis and documentation lookup."""

from __future__ import annotations

# Allow running this script directly without installing the package
import sys
from pathlib import Path

# Add the project root ('agno-doc-bot') to PYTHONPATH if not already present
ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

import json
import logging
from typing import List, Optional

from agno.workflow import Workflow
from pydantic import BaseModel, Field

from src.agents.doc_researcher import DocResearcher
from src.agents.support_diagnoser import SupportDiagnoser

try:  # pragma: no cover - optional dependency
    from agno.storage.sqlite import SqliteStorage
except Exception:  # pragma: no cover - handle missing SQLAlchemy
    SqliteStorage = None  # type: ignore

LOGGER = logging.getLogger(__name__)


class SupportWorkflowInput(BaseModel):
    """Entrada para o SupportWorkflow."""

    query: str = Field(..., title="Pergunta/Incidente", description="Ex: 'Erro ao emitir NF no n8n'")
    session_id: Optional[str] = Field(None, title="Session ID (opcional)")


class SupportWorkflowOutput(BaseModel):
    """Structured output returned by the workflow."""

    diagnosis: str
    probable_causes: List[str] = Field(default_factory=list)
    recommended_actions: List[str] = Field(default_factory=list)
    evidence: List[str] = Field(default_factory=list)
    sources: List[str] = Field(default_factory=list)


class SupportWorkflow(Workflow):
    """Workflow that combines SupportDiagnoser and DocResearcher."""

    # Define explicit models for Playground introspection
    input_model = SupportWorkflowInput
    output_model = SupportWorkflowOutput

    def __init__(
        self,
        support_diagnoser: SupportDiagnoser,
        doc_researcher: DocResearcher,
        *,
        storage: Optional[SqliteStorage] = None,
    ) -> None:
        super().__init__(storage=storage)
        self.support_diagnoser = support_diagnoser
        self.doc_researcher = doc_researcher

    def run(self, input=None) -> SupportWorkflowOutput:  # type: ignore[override]
        """Run the workflow for a support query.

        Estratégia:
        1. Tentar responder usando a documentação local (DocResearcher).
        2. Se não houver contexto suficiente, usar SupportDiagnoser (que pode recorrer ao n8n).
        """

        from src.core.config import get_settings  # avoid circular import at top
        from src.services import retriever_local

        # Normalização da entrada para lidar com chamadas do Playground
        if input is None:
            raise ValueError("query must not be empty")

        if isinstance(input, str):
            input = SupportWorkflowInput(query=input)
        elif isinstance(input, dict):
            if "query" not in input or not input["query"]:
                raise ValueError("query must not be empty")
            input = SupportWorkflowInput(**input)
        elif not isinstance(input, SupportWorkflowInput):
            raise ValueError("invalid input type")

        query = (input.query or "").strip()
        if not query:
            raise ValueError("query must not be empty")

        # Attempt to load cached session state
        try:
            self.load_session()
        except Exception as exc:  # pragma: no cover - defensive
            LOGGER.error("Failed to load workflow session: %s", exc)

        if query in self.session_state:
            try:
                return SupportWorkflowOutput.model_validate(self.session_state[query])
            except Exception:
                LOGGER.warning("Invalid cached entry for query: %s", query)

        settings = get_settings()
        index = retriever_local.build_or_load_index(settings.docs_dir, settings.index_path)
        passages = retriever_local.search(index, query, k=settings.k)

        if passages:
            passages_text = [p.text for p in passages]
            sources_local = [p.path for p in passages]
            local_data = self.doc_researcher.handle_local(query, passages_text, sources_local)

            diagnosis = local_data.get("answer", "")
            diag_sources: list[str] = local_data.get("sources", [])

            output = SupportWorkflowOutput(
                diagnosis=diagnosis,
                probable_causes=[],
                recommended_actions=[],
                evidence=diag_sources,
                sources=diag_sources,
            )
        else:
            # Fallback to SupportDiagnoser (may call n8n)
            diag_data = self.support_diagnoser.diagnose(query)
            diagnosis = diag_data.get("answer", "Não encontrado")
            diag_sources = diag_data.get("sources", [])

            output = SupportWorkflowOutput(
                diagnosis=diagnosis,
                probable_causes=[diagnosis] if diagnosis else [],
                recommended_actions=[],
                evidence=diag_sources,
                sources=diag_sources,
            )

        # Cache result by query
        self.session_state[query] = output.model_dump()
        try:
            self.write_to_storage()
        except Exception as exc:
            LOGGER.error("Failed to persist workflow session: %s", exc)

        return output

