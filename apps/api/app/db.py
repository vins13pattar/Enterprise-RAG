from sqlmodel import SQLModel, create_engine, Session
from packages.shared.config import get_settings
engine = create_engine(get_settings().database_url, pool_pre_ping=True)
def init_db(): SQLModel.metadata.create_all(engine)
def get_session():
    with Session(engine) as s: yield s
