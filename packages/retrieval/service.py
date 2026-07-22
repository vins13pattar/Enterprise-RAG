from dataclasses import dataclass
from sqlmodel import Session, select
from packages.shared.models import DocumentChunk
from packages.providers.embeddings import get_embedding_provider
@dataclass
class RetrievalResult: chunk_id:str; text:str; source:str; page:int|None; score:float; method:str; metadata:dict; selection_reason:str
def _cos(a,b): return sum(x*y for x,y in zip(a,b))
class RetrievalService:
    def __init__(self, session: Session): self.session=session; self.embedder=get_embedding_provider()
    def search(self, workspace_id, query:str, strategy='hybrid', top_k=5, filters=None):
        qv=self.embedder.embed(query); qterms=set(query.lower().split()); rows=self.session.exec(select(DocumentChunk).where(DocumentChunk.workspace_id==workspace_id)).all(); out=[]
        for c in rows:
            if filters and any(str(getattr(c,k,''))!=str(v) for k,v in filters.items()): continue
            score=_cos(qv,self.embedder.embed(c.text)); kw=len(qterms & set(c.text.lower().split()))/(len(qterms) or 1)
            final=score if strategy=='similarity' else (0.7*score+0.3*kw if strategy=='hybrid' else score-.05*len(out))
            out.append(RetrievalResult(c.chunk_id,c.text,c.source,c.page,round(final,4),strategy,{'document_id':str(c.document_id),'section':c.section},'workspace ACL filter matched; score within top_k'))
        return sorted(out,key=lambda r:r.score, reverse=True)[:top_k]
