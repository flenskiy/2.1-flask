from typing import Type

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, func

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import EmailType

Base = declarative_base()


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    email = Column(EmailType, unique=True, index=True)
    password = Column(String(60), nullable=False)
    registration_time = Column(DateTime, server_default=func.now())

    def __str__(self):
        return f"User {self.id}: {self.email}"


class Advertisement(Base):
    __tablename__ = "advertisement"

    id = Column(Integer, primary_key=True)
    title = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=False)
    registration_time = Column(DateTime, server_default=func.now())
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)

    def __str__(self):
        return f"Advertisement {self.id}: {self.title}"


def create_tables(engine):
    # Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


ORM_MODEL = User | Advertisement
