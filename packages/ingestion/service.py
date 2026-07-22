import hashlib
from uuid import uuid4
from sqlmodel import Session
from packages.shared.config import get_settings
from packages.shared.models import Document, DocumentChunk, IngestionJob, JobStatus
from packages.providers.embeddings import get_embedding_provider
class IngestionService:
    def __init__(self, session: Session): self.session=session; self.embedder=get_embedding_provider(); self.settings=get_settings()
    def create_document(self, workspace_id, name, content_type, text, user_id, idempotency_key):
        checksum=hashlib.sha256(text.encode()).hexdigest(); doc=Document(workspace_id=workspace_id,name=name,source_uri=name,content_type=content_type,checksum=checksum,created_by=user_id,status=JobStatus.queued)
        self.session.add(doc); self.session.commit(); self.session.refresh(doc)
        job=IngestionJob(document_id=doc.id, workspace_id=workspace_id, idempotency_key=idempotency_key, status=JobStatus.queued); self.session.add(job); self.session.commit(); self.process_text(doc,text,job); return doc
    def process_text(self, doc, text, job):
        try:
            for status in [JobStatus.extracting,JobStatus.validating,JobStatus.chunking,JobStatus.embedding,JobStatus.indexing]: job.status=status; self.session.add(job); self.session.commit()
            size=650; chunks=[text[i:i+size] for i in range(0,len(text),size)] or ['']
            for i,ch in enumerate(chunks):
                cid=f'{doc.id}:{i}'; c=DocumentChunk(chunk_id=cid,document_id=doc.id,workspace_id=doc.workspace_id,text=ch,page=None,section=f'chunk-{i}',source=doc.name,title=doc.name,content_type=doc.content_type,chunk_index=i,token_count=len(ch.split()),checksum=hashlib.sha256(ch.encode()).hexdigest(),acl=doc.acl,embedding_model=self.embedder.model,embedding_version=self.embedder.version); self.session.add(c)
            doc.status=JobStatus.completed; job.status=JobStatus.completed; self.session.add(doc); self.session.add(job); self.session.commit()
        except Exception as e:
            doc.status=JobStatus.failed; job.status=JobStatus.failed; job.error=str(e); job.dead_lettered=True; self.session.add(doc); self.session.add(job); self.session.commit(); raise
