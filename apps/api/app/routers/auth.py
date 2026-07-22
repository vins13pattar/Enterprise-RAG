from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select
from apps.api.app.db import get_session
from apps.api.app.security import verify_password, create_token, current_user
from packages.shared.models import User
router=APIRouter(prefix='/api/v1/auth', tags=['auth'])
class Login(BaseModel): email:str; password:str
@router.post('/login')
def login(body:Login, session:Session=Depends(get_session)):
    u=session.exec(select(User).where(User.email==body.email)).first()
    if not u or not verify_password(body.password,u.hashed_password): raise HTTPException(401,'Invalid credentials')
    return {'access_token':create_token(u),'token_type':'bearer'}
@router.get('/me')
def me(user:User=Depends(current_user)): return {'id':user.id,'email':user.email,'full_name':user.full_name}
