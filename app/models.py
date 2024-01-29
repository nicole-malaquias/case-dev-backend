from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Tournament(Base):
    __tablename__ = 'tournaments'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    date_start = Column(DateTime, nullable=False)
    date_end = Column(DateTime, nullable=False)

    @classmethod
    def create_tournament(cls, **kwargs):
        new_tournament = cls(**kwargs)
        return new_tournament
