import os
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./foodstore.db')
args = {'connect_args': {'check_same_thread': False}} if DATABASE_URL.startswith('sqlite') else {}
engine = create_engine(DATABASE_URL, **args)

def crear_tablas():
    import models  # noqa: F401
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
