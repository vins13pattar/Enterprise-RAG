"""Workspace-safe cache key construction utilities."""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass

_SAFE = re.compile(r"[^a-zA-Z0-9_.:-]+")


@dataclass(frozen=True)
class RagCacheKey:
    namespace: str
    workspace_id: str
    query: str
    retrieval_config_version: str
    embedding_version: str
    index_version: str
    prompt_version: str
    generation_model: str

    def build(self) -> str:
        parts = {
            "namespace": self.namespace,
            "workspace_id": self.workspace_id,
            "retrieval_config_version": self.retrieval_config_version,
            "embedding_version": self.embedding_version,
            "index_version": self.index_version,
            "prompt_version": self.prompt_version,
            "generation_model": self.generation_model,
        }
        missing = [name for name, value in parts.items() if not str(value).strip()]
        if missing:
            raise ValueError(f"Cache key missing required component(s): {', '.join(sorted(missing))}")
        query_hash = hashlib.sha256(self.query.strip().lower().encode("utf-8")).hexdigest()[:32]
        return ":".join(
            [
                self._clean(self.namespace),
                f"ws={self._clean(self.workspace_id)}",
                f"q={query_hash}",
                f"retrieval={self._clean(self.retrieval_config_version)}",
                f"embedding={self._clean(self.embedding_version)}",
                f"index={self._clean(self.index_version)}",
                f"prompt={self._clean(self.prompt_version)}",
                f"model={self._clean(self.generation_model)}",
            ]
        )

    @staticmethod
    def _clean(value: str) -> str:
        return _SAFE.sub("_", str(value).strip())
