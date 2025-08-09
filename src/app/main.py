from __future__ import annotations

import logging
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel

from src.core.config import Settings
from src.core.logging import setup_logging
from src.services import retriever_local
from src.agents.doc_researcher import DocResearcher
from src.app.deps import doc_researcher, local_index, settings


setup_logging(settings().log_level)
logger = logging.getLogger(__name__)


class AskRequest(BaseModel):
    query: str
    k: Optional[int] = None


class AskResponse(BaseModel):
    answer: str
    sources: List[str]


app = FastAPI(title="Agno Doc Bot", version="0.2.0")


@app.post("/ask", response_model=AskResponse)
def ask(
    req: AskRequest,
    agent: DocResearcher = Depends(doc_researcher),
    index = Depends(local_index),
    settings: Settings = Depends(settings),
) -> AskResponse:
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

    return AskResponse(answer="Não foram encontrados resultados para a sua pesquisa.", sources=[])


@app.get("/stats")
def stats(index=Depends(local_index)):
    return retriever_local.stats(index)


@app.get("/health")
def health():
    return {"status": "ok"}

