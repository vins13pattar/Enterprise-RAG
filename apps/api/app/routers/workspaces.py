from uuid import UUID
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel import Session, select
from apps.api.app.db import get_session
from apps.api.app.security import current_user, require_workspace
from packages.shared.models import User, Workspace, WorkspaceMembership, RoleName, RetrievalConfiguration, EmbeddingConfiguration
router=APIRouter(prefix='/api/v1/workspaces', tags=['workspaces'])
class WorkspaceIn(BaseModel): name:str; description:str=''; instructions:str=''
@router.post('')
def create(body:WorkspaceIn, session:Session=Depends(get_session), user:User=Depends(current_user)):
    w=Workspace(name=body.name,description=body.description,instructions=body.instructions,created_by=user.id); session.add(w); session.commit(); session.refresh(w)
    session.add(WorkspaceMembership(user_id=user.id,workspace_id=w.id,role=RoleName.admin)); session.add(RetrievalConfiguration(workspace_id=w.id)); session.add(EmbeddingConfiguration(workspace_id=w.id,provider='mock',model='mock-embedding-v1',version='2026-07-22')); session.commit(); return w
@router.get('')
def list_ws(session:Session=Depends(get_session), user:User=Depends(current_user)):
    ids=[m.workspace_id for m in session.exec(select(WorkspaceMembership).where(WorkspaceMembership.user_id==user.id)).all()]
    return session.exec(select(Workspace).where(Workspace.id.in_(ids), Workspace.deleted_at==None)).all()
@router.get('/{workspace_id}')
def get_ws(workspace_id:UUID, session:Session=Depends(get_session), user:User=Depends(current_user)):
    require_workspace(session,user,workspace_id); return session.get(Workspace, workspace_id)
@router.patch('/{workspace_id}')
def patch_ws(workspace_id:UUID, body:WorkspaceIn, session:Session=Depends(get_session), user:User=Depends(current_user)):
    require_workspace(session,user,workspace_id,{RoleName.admin,RoleName.knowledge_manager}); w=session.get(Workspace,workspace_id); w.name=body.name; w.description=body.description; w.instructions=body.instructions; session.add(w); session.commit(); return w
