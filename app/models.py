from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class Tournament(Base):
    __tablename__ = 'tournaments'

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        unique=True,
        nullable=False,
    )
    name = Column(String, nullable=False)
    date_start = Column(DateTime, nullable=False)
    date_end = Column(DateTime, nullable=False)
    competitors = relationship('Competitor', back_populates='tournament')

    @classmethod
    def create_tournament(cls, **kwargs):
        new_tournament = cls(**kwargs)
        return new_tournament


class Competitor(Base):
    __tablename__ = 'competitors'

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        unique=True,
        nullable=False,
    )
    name = Column(String(255), nullable=False)
    tournament_id = Column(
        Integer, ForeignKey('tournaments.id'), nullable=False
    )

    tournament = relationship('Tournament', back_populates='competitors')

    @classmethod
    def create_competitor(cls, **kwargs):
        new_competitor = cls(**kwargs)
        return new_competitor
