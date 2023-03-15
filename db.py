from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import create_tables

DSN = "postgresql://postgres:postgres@localhost:5431/app"
engine = create_engine(DSN)
Session = sessionmaker(engine)
create_tables(engine)
