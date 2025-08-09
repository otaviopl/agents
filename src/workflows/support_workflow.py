"""Workflow that orchestrates support diagnosis and documentation lookup."""

from __future__ import annotations

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
    """Input for running the workflow."""

    query: str


class SupportWorkflowOutput(BaseModel):
    """Structured output returned by the workflow."""

    diagnosis: str
    probable_causes: List[str] = Field(default_factory=list)
    recommended_actions: List[str] = Field(default_factory=list)
    evidence: List[str] = Field(default_factory=list)
    sources: List[str] = Field(default_factory=list)


class SupportWorkflow(Workflow):
    """Workflow that combines SupportDiagnoser and DocResearcher."""

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

    def run(self, input: SupportWorkflowInput) -> SupportWorkflowOutput:  # type: ignore[override]
        """Run the workflow for a support query."""

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
            except Exception:  # pragma: no cover - cache corruption
                LOGGER.warning("Invalid cached entry for query: %s", query)

        # Step 1: diagnose the support issue
        diag_data = self.support_diagnoser.diagnose(query)
        diagnosis = diag_data.get("answer", "")
        diag_sources = diag_data.get("sources", [])

        # Step 2: fetch internal instructions
        doc_prompt = (
            f"Instruções internas para: {query}. "
            "Retorne JSON: {\"steps\": string[], \"sources\": string[]}."
        )
        doc_res = self.doc_researcher.agent.run(doc_prompt)
        doc_content = getattr(doc_res, "content", str(doc_res)).strip()
        try:
            doc_json = json.loads(doc_content)
        except Exception:
            doc_json = {"steps": [doc_content], "sources": []}

        recommended = doc_json.get("steps", [])
        if isinstance(recommended, str):
            recommended = [recommended]
        sources_doc = doc_json.get("sources", [])

        output = SupportWorkflowOutput(
            diagnosis=diagnosis,
            probable_causes=[diagnosis] if diagnosis else [],
            recommended_actions=recommended,
            evidence=diag_sources,
            sources=list(dict.fromkeys(diag_sources + sources_doc)),
        )

        # Cache result by query
        self.session_state[query] = output.model_dump()
        try:
            self.write_to_storage()
        except Exception as exc:  # pragma: no cover - optional storage
            LOGGER.error("Failed to persist workflow session: %s", exc)

        return output

