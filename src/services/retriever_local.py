from __future__ import annotations

import logging
import os
import pickle
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import numpy as np
from markdown_it import MarkdownIt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


LOGGER = logging.getLogger(__name__)


CHUNK_SIZE = 900
OVERLAP = 150


@dataclass
class Passage:
    text: str
    path: str
    title: str
    chunk_id: int
    score: float


def _read_markdown(filepath: Path) -> str:
    try:
        text = filepath.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        text = filepath.read_text(encoding="latin-1", errors="ignore")
    return text


def _extract_title(md_text: str, default: str) -> str:
    # First markdown heading or fallback to filename
    for line in md_text.splitlines():
        if line.strip().startswith("# "):
            return line.strip().lstrip("# ").strip()
    return default


def _chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = OVERLAP) -> List[str]:
    tokens = re.split(r"(\s+)", text)
    # join tokens into roughly sized char windows maintaining whitespace
    chunks: List[str] = []
    i = 0
    while i < len(tokens):
        acc = []
        acc_len = 0
        j = i
        while j < len(tokens) and acc_len < chunk_size:
            acc.append(tokens[j])
            acc_len += len(tokens[j])
            j += 1
        chunk = "".join(acc).strip()
        if chunk:
            chunks.append(chunk)
        if j >= len(tokens):
            break
        # move by (chunk_size - overlap) in characters
        step = max(chunk_size - overlap, 1)
        # approximate by characters
        consumed = 0
        k = i
        while k < len(tokens) and consumed < step:
            consumed += len(tokens[k])
            k += 1
        i = k
    return chunks


def build_or_load_index(
    docs_dir: str,
    index_path: str = ".local_index.pkl",
    force_rebuild: bool = False,
) -> Dict:
    """Load a previously built local index or (re)build it.

    The index is automatically rebuilt if:
    1. ``force_rebuild`` is explicitly set to ``True``; or
    2. Any markdown file inside ``docs_dir`` was modified after the index file
       was created.
    """

    index_file = Path(index_path)
    docs_path = Path(docs_dir)

    # Gather markdown files *before* deciding to load the index so we can
    # compare modification times when necessary.
    md_files = list(docs_path.glob("**/*.md"))

    latest_doc_mtime: float = 0.0
    if md_files:
        latest_doc_mtime = max(fp.stat().st_mtime for fp in md_files)

    should_rebuild = force_rebuild
    if index_file.exists() and not force_rebuild:
        try:
            index_mtime = index_file.stat().st_mtime
            # Rebuild if any markdown was updated after the index file.
            if latest_doc_mtime > index_mtime:
                LOGGER.info("Docs changed after index build (index: %s, docs: %s). Rebuilding index.", index_mtime, latest_doc_mtime)
                should_rebuild = True
            else:
                with index_file.open("rb") as f:
                    data = pickle.load(f)
                LOGGER.info("Local index loaded: %s", index_file)
                return data
        except Exception:
            LOGGER.warning("Failed to load index, rebuilding.")
            should_rebuild = True

    if not md_files:
        LOGGER.info("No markdown files found in %s", docs_dir)

    # If we reached this point, we need to build the index (first time or rebuild).

    if should_rebuild:
        LOGGER.info("Building local index from %s", docs_dir)

    passages: List[str] = []
    meta: List[Tuple[str, str, int]] = []  # (path, title, chunk_id)

    for fp in md_files:
        raw = _read_markdown(fp)
        title = _extract_title(raw, default=fp.name)
        chunks = _chunk_text(raw)
        for idx, ch in enumerate(chunks):
            passages.append(ch)
            meta.append((str(fp), title, idx))

    if not passages:
        LOGGER.info("No passages extracted from markdown in %s", docs_dir)

    vectorizer = TfidfVectorizer(ngram_range=(1, 2))
    matrix = vectorizer.fit_transform(passages)

    data = {
        "vectorizer": vectorizer,
        "matrix": matrix,
        "passages": passages,
        "meta": meta,
        "files": len(md_files),
        "chunks": len(passages),
    }

    with index_file.open("wb") as f:
        pickle.dump(data, f)
    LOGGER.info("Local index built: %s files, %s chunks", data["files"], data["chunks"])
    return data


def search(index: Dict, query: str, k: int = 5) -> List[Passage]:
    if not index or index.get("matrix") is None:
        return []
    vec = index["vectorizer"].transform([query])
    sim = cosine_similarity(vec, index["matrix"]).ravel()
    if sim.size == 0:
        return []
    top_idx = np.argsort(sim)[::-1][:k]
    results: List[Passage] = []
    for i in top_idx:
        path, title, chunk_id = index["meta"][int(i)]
        results.append(
            Passage(
                text=index["passages"][int(i)],
                path=path,
                title=title,
                chunk_id=int(chunk_id),
                score=float(sim[int(i)]),
            )
        )
    return results


def stats(index: Dict) -> Dict[str, int]:
    return {"files": int(index.get("files", 0)), "chunks": int(index.get("chunks", 0))}

