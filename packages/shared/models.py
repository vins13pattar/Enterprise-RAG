from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Column, JSON
class RoleName(str, Enum): admin='admin'; knowledge_manager='knowledge_manager'; reviewer='reviewer'; user='user'
class JobStatus(str, Enum): queued='queued'; extracting='extracting'; validating='validating'; chunking='chunking'; embedding='embedding'; indexing='indexing'; completed='completed'; partially_completed='partially_completed'; failed='failed'
class TimestampMixin(SQLModel):
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
class User(TimestampMixin, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True); email: str = Field(index=True, unique=True); hashed_password: str; full_name: str='Demo Admin'; disabled: bool=False
class Role(TimestampMixin, table=True): id: UUID=Field(default_factory=uuid4, primary_key=True); name: RoleName=Field(index=True, unique=True)
class Workspace(TimestampMixin, table=True):
    id: UUID=Field(default_factory=uuid4, primary_key=True); name: str; description: str=''; instructions: str=''; created_by: Optional[UUID]=None; deleted_at: Optional[datetime]=None
class WorkspaceMembership(TimestampMixin, table=True):
    id: UUID=Field(default_factory=uuid4, primary_key=True); user_id: UUID=Field(index=True); workspace_id: UUID=Field(index=True); role: RoleName=RoleName.user
class Document(TimestampMixin, table=True):
    id: UUID=Field(default_factory=uuid4, primary_key=True); workspace_id: UUID=Field(index=True); name: str; source_uri: str; content_type: str; status: JobStatus=JobStatus.queued; checksum: str=Field(index=True); acl: dict=Field(default_factory=dict, sa_column=Column(JSON)); created_by: Optional[UUID]=None; deleted_at: Optional[datetime]=None; failure_reason: str=''
class DocumentVersion(TimestampMixin, table=True): id: UUID=Field(default_factory=uuid4, primary_key=True); document_id: UUID; workspace_id: UUID; version: int=1; object_key: str; checksum: str
class DocumentChunk(TimestampMixin, table=True):
    id: UUID=Field(default_factory=uuid4, primary_key=True); chunk_id: str=Field(index=True, unique=True); document_id: UUID=Field(index=True); workspace_id: UUID=Field(index=True); text: str; page: Optional[int]=None; section: str=''; source: str; title: str=''; content_type: str=''; chunk_index: int; token_count: int; checksum: str; acl: dict=Field(default_factory=dict, sa_column=Column(JSON)); embedding_model: str; embedding_version: str
class IngestionJob(TimestampMixin, table=True): id: UUID=Field(default_factory=uuid4, primary_key=True); document_id: UUID; workspace_id: UUID; status: JobStatus=JobStatus.queued; attempts: int=0; idempotency_key: str=Field(index=True); error: str=''; dead_lettered: bool=False
class EmbeddingConfiguration(TimestampMixin, table=True): id: UUID=Field(default_factory=uuid4, primary_key=True); workspace_id: UUID; provider: str; model: str; version: str; dimensions: int=64
class RetrievalConfiguration(TimestampMixin, table=True): id: UUID=Field(default_factory=uuid4, primary_key=True); workspace_id: UUID; strategy: str='hybrid'; top_k: int=5; fetch_k: int=20; similarity_threshold: float=.15; mmr_lambda: float=.5; max_context_tokens: int=3000; version: str='v1'
class Conversation(TimestampMixin, table=True): id: UUID=Field(default_factory=uuid4, primary_key=True); workspace_id: UUID; user_id: UUID; title: str='New conversation'; deleted_at: Optional[datetime]=None
class Message(TimestampMixin, table=True): id: UUID=Field(default_factory=uuid4, primary_key=True); conversation_id: UUID; role: str; content: str
class RetrievalTrace(TimestampMixin, table=True): id: UUID=Field(default_factory=uuid4, primary_key=True); request_id: str=Field(index=True); workspace_id: UUID; query: str; strategy: str; diagnostics: dict=Field(default_factory=dict, sa_column=Column(JSON))
class GeneratedResponse(TimestampMixin, table=True): id: UUID=Field(default_factory=uuid4, primary_key=True); conversation_id: Optional[UUID]=None; workspace_id: UUID; answer: str; confidence: float; grounded: bool; needs_human_review: bool; warnings: list=Field(default_factory=list, sa_column=Column(JSON))
class Citation(TimestampMixin, table=True): id: UUID=Field(default_factory=uuid4, primary_key=True); response_id: UUID; source_id: str; document_name: str; page: Optional[int]=None; chunk_id: str; quote: str
class UserFeedback(TimestampMixin, table=True): id: UUID=Field(default_factory=uuid4, primary_key=True); response_id: UUID; user_id: UUID; rating: str; corrected_answer: str=''
class EvaluationDataset(TimestampMixin, table=True): id: UUID=Field(default_factory=uuid4, primary_key=True); workspace_id: UUID; name: str
class EvaluationQuestion(TimestampMixin, table=True): id: UUID=Field(default_factory=uuid4, primary_key=True); dataset_id: UUID; question: str; expected_answer: str; expected_chunk_ids: list=Field(default_factory=list, sa_column=Column(JSON))
class EvaluationRun(TimestampMixin, table=True): id: UUID=Field(default_factory=uuid4, primary_key=True); dataset_id: UUID; status: str='queued'; metrics: dict=Field(default_factory=dict, sa_column=Column(JSON))
class EvaluationResult(TimestampMixin, table=True): id: UUID=Field(default_factory=uuid4, primary_key=True); run_id: UUID; question_id: UUID; metrics: dict=Field(default_factory=dict, sa_column=Column(JSON)); answer: str=''
class HumanReview(TimestampMixin, table=True): id: UUID=Field(default_factory=uuid4, primary_key=True); response_id: UUID; workspace_id: UUID; status: str='pending'; reviewer_notes: str=''; edited_answer: str=''
class AuditLog(TimestampMixin, table=True): id: UUID=Field(default_factory=uuid4, primary_key=True); actor_id: Optional[UUID]=None; workspace_id: Optional[UUID]=None; action: str; target_type: str; target_id: str; metadata: dict=Field(default_factory=dict, sa_column=Column(JSON))
