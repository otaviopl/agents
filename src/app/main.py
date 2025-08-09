from __future__ import annotations

import logging
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel

from src.core.config import Settings
from src.core.logging import setup_logging
from src.services import retriever_local
from src.agents.doc_researcher import DocResearcher
from src.app.deps import (
    doc_researcher,
    local_index,
    settings,
    support_diagnoser,
    support_workflow,
)
from src.workflows.support_workflow import (
    SupportWorkflow,
    SupportWorkflowInput,
    SupportWorkflowOutput,
)


setup_logging(settings().log_level)
logger = logging.getLogger(__name__)


class AskRequest(BaseModel):
    query: str
    k: Optional[int] = None


class AskResponse(BaseModel):
    answer: str
    sources: List[str]


class SupportWorkflowRequest(SupportWorkflowInput):
    pass


class SupportWorkflowResponse(SupportWorkflowOutput):
    pass


app = FastAPI(title="Agno Doc Bot", version="0.2.0")


@app.post("/ask", response_model=AskResponse)
def ask(
    req: AskRequest,
    agent: DocResearcher = Depends(doc_researcher),
    index = Depends(local_index),
    settings: Settings = Depends(settings),
    support_agent: SupportDiagnoser = Depends(support_diagnoser),
) -> AskResponse:
    # Save request
    with open("docs/requests.log", "a") as f:
        f.write(req.model_dump_json() + "\n")

    query = (req.query or "").strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query must not be empty")

    k = req.k or settings.k

    # Local first
    logger.info("Local search start: k=%s, index_stats=%s", k, retriever_local.stats(index))
    local_passages = retriever_local.search(index, query, k=k)
    passages_text = [p.text for p in local_passages]
    sources_local = [p.path for p in local_passages]
    logger.info("Local hits: %d", len(local_passages))
    logger.info("Context size (chars): %d", sum(len(t) for t in passages_text))

    if passages_text:
        data = agent.handle_local(query, passages_text, sources_local)
        return AskResponse(answer=data.get("answer", ""), sources=data.get("sources", []))

    else:
        # Call the support diagnoser agent
        diagnosis_response = support_agent.diagnose(query)
        return AskResponse(
            answer=diagnosis_response.get("answer", "Não foi possível diagnosticar o problema."),
            sources=diagnosis_response.get("sources", [])
        )


@app.post("/workflows/support/run", response_model=SupportWorkflowResponse)
def run_support_workflow(
    req: SupportWorkflowRequest,
    workflow: SupportWorkflow = Depends(support_workflow),
) -> SupportWorkflowResponse:
    try:
        result = workflow.run(req)
        return SupportWorkflowResponse(**result.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:  # pragma: no cover - unexpected errors
        logger.error("Support workflow failed: %s", exc)
        raise HTTPException(status_code=500, detail="Workflow execution failed")


@app.get("/stats")
def stats(index=Depends(local_index)):
    return retriever_local.stats(index)


@app.get("/health")
def health():
    return {"status": "ok"}

