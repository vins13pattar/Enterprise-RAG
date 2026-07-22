from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from packages.shared.config import get_settings
from packages.shared.models import User, Role, RoleName
from apps.api.app.db import init_db, engine
from apps.api.app.security import hash_password
from apps.api.app.routers import auth, workspaces, documents, chat, misc
app=FastAPI(title='Enterprise Knowledge Assistant API', version='0.1.0')
app.add_middleware(CORSMiddleware, allow_origins=get_settings().cors_origins.split(','), allow_credentials=True, allow_methods=['*'], allow_headers=['*'])
@app.on_event('startup')
def startup():
    init_db()
    with Session(engine) as s:
        for r in RoleName:
            if not s.exec(select(Role).where(Role.name==r)).first(): s.add(Role(name=r))
        if not s.exec(select(User).where(User.email=='admin@example.com')).first(): s.add(User(email='admin@example.com',hashed_password=hash_password('admin'),full_name='Demo Admin'))
        s.commit()
for r in [auth.router, workspaces.router, documents.router, chat.router, misc.router]: app.include_router(r)
