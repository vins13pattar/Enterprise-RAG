from datetime import datetime, timedelta
from uuid import UUID
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlmodel import Session, select
from packages.shared.config import get_settings
from packages.shared.models import User, WorkspaceMembership, RoleName
from .db import get_session
pwd_context=CryptContext(schemes=['bcrypt'], deprecated='auto'); oauth2_scheme=OAuth2PasswordBearer(tokenUrl='/api/v1/auth/login')
def hash_password(p): return pwd_context.hash(p)
def verify_password(p,h): return pwd_context.verify(p,h)
def create_token(user: User):
    s=get_settings(); exp=datetime.utcnow()+timedelta(minutes=s.jwt_expire_minutes)
    return jwt.encode({'sub':str(user.id),'iss':s.jwt_issuer,'exp':exp}, s.jwt_secret, algorithm='HS256')
def current_user(token: str=Depends(oauth2_scheme), session: Session=Depends(get_session)):
    try: payload=jwt.decode(token, get_settings().jwt_secret, algorithms=['HS256'], issuer=get_settings().jwt_issuer); uid=UUID(payload['sub'])
    except (JWTError, KeyError, ValueError): raise HTTPException(401,'Invalid authentication token')
    user=session.get(User, uid)
    if not user or user.disabled: raise HTTPException(401,'Inactive user')
    return user
def require_workspace(session: Session, user: User, workspace_id: UUID, roles: set[RoleName]|None=None):
    m=session.exec(select(WorkspaceMembership).where(WorkspaceMembership.user_id==user.id, WorkspaceMembership.workspace_id==workspace_id)).first()
    if not m: raise HTTPException(403,'Workspace access denied')
    if roles and m.role not in roles and m.role!=RoleName.admin: raise HTTPException(403,'Insufficient role')
    return m
