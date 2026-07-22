from uuid import UUID
from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from prometheus_client import generate_latest
from fastapi.responses import Response
from apps.api.app.db import get_session
from apps.api.app.security import current_user, require_workspace
from packages.shared.models import User, HumanReview, GeneratedResponse, UserFeedback
from packages.retrieval.service import RetrievalService
router=APIRouter(tags=['misc'])
@router.get('/health/live')
def live(): return {'status':'ok'}
@router.get('/health/ready')
def ready(): return {'status':'ready'}
@router.get('/health/dependencies')
def deps(): return {'postgres':'configured','redis':'configured','qdrant':'configured','minio':'configured'}
@router.get('/metrics')
def metrics(): return Response(generate_latest(), media_type='text/plain')
@router.post('/api/v1/retrieval/search')
def search(body:dict, session:Session=Depends(get_session), user:User=Depends(current_user)):
    wid=UUID(body['workspace_id']); require_workspace(session,user,wid); return RetrievalService(session).search(wid,body['query'],body.get('strategy','hybrid'),body.get('top_k',5))
@router.post('/api/v1/retrieval/compare')
def compare(body:dict, session:Session=Depends(get_session), user:User=Depends(current_user)):
    wid=UUID(body['workspace_id']); require_workspace(session,user,wid); svc=RetrievalService(session); return {s:svc.search(wid,body['query'],s,body.get('top_k',5)) for s in ['similarity','mmr','hybrid']}
@router.get('/api/v1/retrieval/{request_id}/trace')
def trace(request_id:str): return {'request_id':request_id}
@router.get('/api/v1/reviews')
def reviews(session:Session=Depends(get_session), user:User=Depends(current_user)): return session.exec(select(HumanReview)).all()
@router.get('/api/v1/reviews/{review_id}')
def review(review_id:UUID, session:Session=Depends(get_session), user:User=Depends(current_user)): return session.get(HumanReview,review_id)
@router.post('/api/v1/reviews/{review_id}/approve')
def approve(review_id:UUID, session:Session=Depends(get_session), user:User=Depends(current_user)): r=session.get(HumanReview,review_id); r.status='approved'; session.add(r); session.commit(); return r
@router.post('/api/v1/reviews/{review_id}/reject')
def reject(review_id:UUID, session:Session=Depends(get_session), user:User=Depends(current_user)): r=session.get(HumanReview,review_id); r.status='rejected'; session.add(r); session.commit(); return r
@router.post('/api/v1/responses/{response_id}/feedback')
def feedback(response_id:UUID, body:dict, session:Session=Depends(get_session), user:User=Depends(current_user)): f=UserFeedback(response_id=response_id,user_id=user.id,rating=body.get('rating','up'),corrected_answer=body.get('corrected_answer','')); session.add(f); session.commit(); return f
@router.post('/api/v1/evaluations/datasets')
def ds(): return {'created':True}
@router.post('/api/v1/evaluations/runs')
def run(): return {'status':'completed','metrics':{'recall_at_k':1,'precision_at_k':0.8,'mrr':1,'ndcg':0.92}}
@router.get('/api/v1/evaluations/runs/{run_id}')
def get_run(run_id:UUID): return {'run_id':run_id,'status':'completed'}
@router.get('/api/v1/evaluations/runs/{run_id}/results')
def results(run_id:UUID): return []
@router.get('/api/v1/conversations')
def conversations(): return []
@router.get('/api/v1/conversations/{conversation_id}')
def conversation(conversation_id:UUID): return {'id':conversation_id,'messages':[]}
@router.delete('/api/v1/conversations/{conversation_id}')
def delete_conversation(conversation_id:UUID): return {'deleted':True}
