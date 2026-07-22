from uuid import UUID
from fastapi import APIRouter, Depends, UploadFile, File, Header
from pydantic import BaseModel
from sqlmodel import Session, select
from apps.api.app.db import get_session
from apps.api.app.security import current_user, require_workspace
from packages.shared.models import User, Document, DocumentChunk, RoleName
from packages.ingestion.service import IngestionService
router=APIRouter(tags=['documents'])
class UrlIn(BaseModel): url:str; text:str|None=None
@router.post('/api/v1/workspaces/{workspace_id}/documents')
async def upload(workspace_id:UUID, file:UploadFile=File(...), idempotency_key:str=Header(default='demo'), session:Session=Depends(get_session), user:User=Depends(current_user)):
    require_workspace(session,user,workspace_id,{RoleName.admin,RoleName.knowledge_manager}); data=(await file.read()).decode('utf-8','ignore'); return IngestionService(session).create_document(workspace_id,file.filename,file.content_type or 'text/plain',data,user.id,idempotency_key)
@router.post('/api/v1/workspaces/{workspace_id}/sources/url')
def url(workspace_id:UUID, body:UrlIn, session:Session=Depends(get_session), user:User=Depends(current_user)):
    require_workspace(session,user,workspace_id,{RoleName.admin,RoleName.knowledge_manager}); return IngestionService(session).create_document(workspace_id,body.url,'text/html',body.text or body.url,user.id,body.url)
@router.get('/api/v1/workspaces/{workspace_id}/documents')
def docs(workspace_id:UUID, session:Session=Depends(get_session), user:User=Depends(current_user)):
    require_workspace(session,user,workspace_id); return session.exec(select(Document).where(Document.workspace_id==workspace_id, Document.deleted_at==None)).all()
@router.get('/api/v1/documents/{document_id}')
def doc(document_id:UUID, session:Session=Depends(get_session), user:User=Depends(current_user)):
    d=session.get(Document,document_id); require_workspace(session,user,d.workspace_id); return d
@router.delete('/api/v1/documents/{document_id}')
def delete_doc(document_id:UUID, session:Session=Depends(get_session), user:User=Depends(current_user)):
    d=session.get(Document,document_id); require_workspace(session,user,d.workspace_id,{RoleName.admin,RoleName.knowledge_manager}); import datetime; d.deleted_at=datetime.datetime.utcnow(); session.add(d); session.commit(); return {'deleted':True}
@router.post('/api/v1/documents/{document_id}/retry')
def retry(document_id:UUID): return {'queued':True,'document_id':document_id}
@router.post('/api/v1/documents/{document_id}/reindex')
def reindex(document_id:UUID): return {'queued':True,'document_id':document_id}
@router.get('/api/v1/documents/{document_id}/chunks')
def chunks(document_id:UUID, session:Session=Depends(get_session), user:User=Depends(current_user)):
    d=session.get(Document,document_id); require_workspace(session,user,d.workspace_id); return session.exec(select(DocumentChunk).where(DocumentChunk.document_id==document_id)).all()
