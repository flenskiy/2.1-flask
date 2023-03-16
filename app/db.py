from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import PG_DSN

from models import create_tables

engine = create_engine(PG_DSN)
Session = sessionmaker(engine)
create_tables(engine)
