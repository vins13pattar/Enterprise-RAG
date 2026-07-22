from uuid import UUID, uuid4
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlmodel import Session
from apps.api.app.db import get_session
from apps.api.app.security import current_user, require_workspace
from packages.shared.models import User, RetrievalTrace, GeneratedResponse, HumanReview
from packages.retrieval.service import RetrievalService
from packages.generation.service import GenerationService
from packages.shared.config import get_settings
router=APIRouter(prefix='/api/v1/chat', tags=['chat'])
class Query(BaseModel): workspace_id:UUID; question:str; strategy:str='hybrid'; top_k:int=5; metadata_filters:dict={}
def _answer(body, session, user):
    require_workspace(session,user,body.workspace_id); request_id=str(uuid4()); chunks=RetrievalService(session).search(body.workspace_id,body.question,body.strategy,body.top_k,body.metadata_filters); ans=GenerationService().generate(body.question,chunks,get_settings().human_review_threshold); session.add(RetrievalTrace(request_id=request_id,workspace_id=body.workspace_id,query=body.question,strategy=body.strategy,diagnostics={'chunks':[c.__dict__ for c in chunks]})); gr=GeneratedResponse(workspace_id=body.workspace_id,answer=ans.answer,confidence=ans.confidence,grounded=ans.grounded,needs_human_review=ans.needs_human_review,warnings=ans.warnings); session.add(gr); session.commit(); session.refresh(gr); 
    if ans.needs_human_review: session.add(HumanReview(response_id=gr.id,workspace_id=body.workspace_id)); session.commit()
    return {'request_id':request_id,'response_id':gr.id,**ans.model_dump()}
@router.post('/query')
def query(body:Query, session:Session=Depends(get_session), user:User=Depends(current_user)): return _answer(body,session,user)
@router.post('/stream')
def stream(body:Query, session:Session=Depends(get_session), user:User=Depends(current_user)):
    out=_answer(body,session,user)
    def gen():
        for word in out['answer'].split(): yield f'data: {word}\n\n'
        yield f'data: [DONE]\n\n'
    return StreamingResponse(gen(), media_type='text/event-stream')
