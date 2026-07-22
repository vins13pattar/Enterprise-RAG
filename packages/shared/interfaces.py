"""Provider and repository contracts for the Enterprise RAG domain.

These protocols keep domain services independent from concrete infrastructure such as
Qdrant, Redis, MinIO/S3, FastAPI, or specific LLM vendors. Runtime adapters should
implement these contracts and tests should use contract tests against the same surface.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Iterable, Protocol, runtime_checkable
from uuid import UUID


@dataclass(frozen=True)
class ChunkRecord:
    chunk_id: str
    document_id: UUID
    workspace_id: UUID
    text: str
    source: str
    chunk_index: int
    token_count: int
    checksum: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class VectorRecord:
    chunk_id: str
    workspace_id: UUID
    document_id: UUID
    embedding: list[float]
    payload: dict[str, Any]


@dataclass(frozen=True)
class RetrievalCandidate:
    chunk_id: str
    text: str
    source: str
    score: float
    method: str
    metadata: dict[str, Any]
    selected_reason: str


@dataclass(frozen=True)
class CacheKeyParts:
    workspace_id: str
    query_hash: str
    retrieval_config_version: str
    embedding_version: str
    index_version: str
    prompt_version: str
    generation_model: str


@runtime_checkable
class VectorStore(Protocol):
    def ensure_collection(self, workspace_id: UUID, embedding_dimensions: int, *, version: str) -> None: ...

    def upsert_vectors(self, records: Iterable[VectorRecord], *, collection_version: str) -> None: ...

    def delete_document_vectors(self, workspace_id: UUID, document_id: UUID) -> int: ...

    def similarity_search(self, workspace_id: UUID, embedding: list[float], *, top_k: int, filters: dict[str, Any]) -> list[RetrievalCandidate]: ...

    def mmr_search(self, workspace_id: UUID, embedding: list[float], *, top_k: int, fetch_k: int, lambda_mult: float, filters: dict[str, Any]) -> list[RetrievalCandidate]: ...

    def hybrid_search(self, workspace_id: UUID, query: str, embedding: list[float], *, top_k: int, filters: dict[str, Any]) -> list[RetrievalCandidate]: ...

    def health_check(self) -> dict[str, Any]: ...


@runtime_checkable
class ObjectStore(Protocol):
    def put_bytes(self, key: str, data: bytes, *, content_type: str, metadata: dict[str, str]) -> str: ...

    def get_bytes(self, key: str) -> bytes: ...

    def delete_prefix(self, prefix: str) -> int: ...


@runtime_checkable
class CacheStore(Protocol):
    def get_json(self, key: str) -> dict[str, Any] | None: ...

    def set_json(self, key: str, value: dict[str, Any], *, ttl_seconds: int) -> None: ...

    def delete_prefix(self, prefix: str) -> int: ...


@runtime_checkable
class EmbeddingProvider(Protocol):
    model: str
    version: str
    dimensions: int

    def embed(self, text: str) -> list[float]: ...


@runtime_checkable
class LLMProvider(Protocol):
    model: str

    def generate_structured(self, prompt: str, *, temperature: float, max_tokens: int) -> dict[str, Any]: ...

    def stream(self, prompt: str, *, temperature: float, max_tokens: int) -> Iterable[str]: ...


@runtime_checkable
class AuditSink(Protocol):
    def record(self, *, actor_id: UUID | None, workspace_id: UUID | None, action: str, target_type: str, target_id: str, metadata: dict[str, Any], occurred_at: datetime | None = None) -> None: ...
