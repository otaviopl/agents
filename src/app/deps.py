from __future__ import annotations

import logging
from functools import lru_cache

from src.agents.doc_researcher import DocResearcher
from src.agents.support_diagnoser import SupportDiagnoser
from src.core.config import get_settings, Settings
from src.services import retriever_local
from src.workflows.support_workflow import SupportWorkflow

try:  # pragma: no cover - optional dependency
    from agno.storage.sqlite import SqliteStorage
except Exception:  # pragma: no cover - handle missing SQLAlchemy
    SqliteStorage = None  # type: ignore


@lru_cache(maxsize=1)
def settings() -> Settings:
    return get_settings()


@lru_cache(maxsize=1)
def local_index():
    s = settings()
    logging.getLogger(__name__).info(
        "Building/Loading local index from %s", s.docs_dir
    )
    return retriever_local.build_or_load_index(s.docs_dir, s.index_path)


@lru_cache(maxsize=1)
def doc_researcher() -> DocResearcher:
    s = settings()
    return DocResearcher(s)


@lru_cache(maxsize=1)
def support_diagnoser() -> SupportDiagnoser:
    s = settings()
    return SupportDiagnoser(s)


@lru_cache(maxsize=1)
def support_workflow() -> SupportWorkflow:
    """Return a cached instance of SupportWorkflow."""
    storage = None
    if SqliteStorage is not None:
        storage = SqliteStorage(
            table_name="support_workflow",
            db_file="support_workflow.db",
            mode="workflow",
        )
    return SupportWorkflow(
        support_diagnoser=support_diagnoser(),
        doc_researcher=doc_researcher(),
        storage=storage,
    )

