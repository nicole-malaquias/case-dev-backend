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
    def create_competitor(cls, names, tournament_id, session):
        if tournament_id is None:
            raise ValueError(
                " The 'tournament_id' is mandatory when creating competitors."
            )

        existing_tournament = session.query(Tournament).get(tournament_id)
        if existing_tournament is None:
            raise ValueError(f'Tournament with ID {tournament_id} not found.')
        competitors = []
        if len(names) < 2:
            raise ValueError('A tournament must have at least 2 competitors.')
        for name in names:
            new_competitor = Competitor(name=name, tournament_id=tournament_id)
            competitors.append(new_competitor)

        session.add_all(competitors)
        session.commit()
        return
