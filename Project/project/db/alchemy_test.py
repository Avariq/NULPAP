from sqlalchemy import create_engine, engine
from sqlalchemy.orm import Session

from project.config import DB_URI

engine = create_engine(DB_URI)
engine.connect()

session = Session(bind=engine)

print(session)