import math
import random

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    and_,
    desc,
    or_,
)
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.orm.exc import NoResultFound

GROUP_1 = 'group_1'
GROUP_2 = 'group_2'
STATUS_FINISHED = 'finished'
STATUS_PENDING = 'pending'


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
    number_matches = Column(Integer, nullable=True)

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
    group = Column(
        Enum('group_1', 'group_2', name='competitor_group'), nullable=True
    )
    tournament_id = Column(
        Integer, ForeignKey('tournaments.id'), nullable=False
    )
    tournament = relationship('Tournament', back_populates='competitors')
    status = Column(Boolean, default=True)

    @staticmethod
    def _number_of_matches(number_competitors):
        if number_competitors < 2:
            raise ValueError(
                'O número de participantes deve ser pelo menos 2.'
            )

        return math.ceil(math.log2(number_competitors))

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
        random.shuffle(names)
        for ind in range(0, len(names)):
            if ind % 2 == 0:
                estado = GROUP_1
            else:
                estado = GROUP_2
            new_competitor = cls(
                name=names[ind],
                tournament_id=tournament_id,
                group=estado,
            )
            print(new_competitor)
            competitors.append(new_competitor)

        number_matches = cls._number_of_matches(len(names))
        session.query(Tournament).get(
            tournament_id
        ).number_matches = number_matches

        session.commit()
        session.add_all(competitors)
        session.commit()
        return


class Match(Base):
    __tablename__ = 'matches'

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        unique=True,
        nullable=False,
    )
    competitor_1_id = Column(
        Integer, ForeignKey('competitors.id'), nullable=True
    )
    competitor_2_id = Column(
        Integer, ForeignKey('competitors.id'), nullable=True
    )
    winner_id = Column(Integer, ForeignKey('competitors.id'), nullable=True)
    tournament_id = Column(
        Integer, ForeignKey('tournaments.id'), nullable=False
    )
    competitor_1 = relationship('Competitor', foreign_keys=[competitor_1_id])
    competitor_2 = relationship('Competitor', foreign_keys=[competitor_2_id])
    winner = relationship('Competitor', foreign_keys=[winner_id])
    tournament = relationship('Tournament')
    round = Column(Integer, nullable=False)
    state = Column(
        Enum('pending', 'finished', name='match_state'), nullable=False
    )

    @staticmethod
    def _set_pair(names):
        random.shuffle(names)
        pairs = []
        if len(names) % 2 != 0:
            winder_abs = names.pop()
            pairs.append((winder_abs,))
        [
            pairs.append((names[i], names[i + 1]))
            for i in range(0, len(names), 2)
        ]
        return pairs

    @classmethod
    def create_match(cls, tournament_id, session):
        existing_tournament = session.query(Tournament).get(tournament_id)

        if existing_tournament is None:
            raise ValueError(f'Tournament with ID {tournament_id} not found.')

        matches = (
            session.query(Match)
            .filter_by(tournament_id=tournament_id)
            .order_by(desc(Match.round))
            .all()
        )

        competitors_group_1 = cls._get_competitors_by_group(
            session, tournament_id, GROUP_1
        )
        competitors_group_2 = cls._get_competitors_by_group(
            session, tournament_id, GROUP_2
        )

        if cls._should_create_final_match(existing_tournament, matches):

            cls._create_final_match(
                session, tournament_id, existing_tournament.number_matches
            )
            return

        if matches and matches[0].round == existing_tournament.number_matches:
            return

        if matches and matches[0].state == STATUS_PENDING:
            return

        round = len(matches) + 1

        cls._create_matches_for_group(
            session, tournament_id, competitors_group_1, round
        )
        cls._create_matches_for_group(
            session, tournament_id, competitors_group_2, round
        )

    @classmethod
    def _get_competitors_by_group(cls, session, tournament_id, group):
        return (
            session.query(Competitor)
            .filter(
                and_(
                    Competitor.tournament_id == tournament_id,
                    Competitor.group == group,
                    Competitor.status == True,  # noqa
                )
            )
            .all()
        )

    @classmethod
    def _should_create_final_match(cls, existing_tournament, matches):
        total_experado = existing_tournament.number_matches
        total_atual = len(matches)

        total = total_experado - total_atual
        if total == 1:
            return True
        if total_experado == 1 and total_atual == 0:
            return True

        return False

    @classmethod
    def _create_final_match(cls, session, tournament_id, last_round):
        finalists = (
            session.query(Competitor)
            .filter(
                Competitor.tournament_id == tournament_id,
                Competitor.status == True,  # noqa
            )
            .limit(2)
            .all()
        )
        print(finalists)
        if len(finalists) == 2:
            new_match = cls(
                competitor_1_id=finalists[0].id,
                competitor_2_id=finalists[1].id,
                tournament_id=tournament_id,
                round=last_round,
                state=STATUS_PENDING,
            )

            session.add(new_match)
            session.commit()

    @classmethod
    def _create_matches_for_group(
        cls, session, tournament_id, competitors, round
    ):
        pairs = cls._set_pair(competitors)

        for pair in pairs:
            if len(pair) == 2:
                new_match = cls(
                    competitor_1_id=pair[0].id,
                    competitor_2_id=pair[1].id,
                    tournament_id=tournament_id,
                    round=round,
                    state=STATUS_PENDING,
                )
                session.add(new_match)
            else:
                new_match = cls(
                    competitor_1_id=pair[0].id,
                    competitor_2_id=None,
                    tournament_id=tournament_id,
                    round=round,
                    state=STATUS_FINISHED,
                    winner_id=pair[0].id,
                )
                session.add(new_match)

        session.commit()

    @classmethod
    def list_matches(cls, tournament_id, session):
        matches = (
            session.query(Match)
            .filter_by(tournament_id=tournament_id)
            .order_by(desc(Match.round))
            .all()
        )
        dic = {}
        for match in matches:
            if f'Round {match.round}' not in dic:
                dic[f'Round {match.round}'] = []
            dic[f'Round {match.round}'].append(
                {
                    'competitor_1': match.competitor_1.name,
                    'competitor_2': match.competitor_2.name
                    if match.competitor_2
                    else None,
                    'winner': match.winner.name if match.winner else None,
                    'state': match.state,
                    'round': match.round,
                    'id': match.id,
                }
            )
        return dic

    @classmethod
    def set_winner(cls, match_id, name, session):
        match = session.query(Match).get(match_id)

        # Encontrar os competidores pelo nome
        competitor_winner = (
            session.query(Competitor).filter(Competitor.name == name).first()
        )

        try:
            competitor_loser = (
                session.query(Competitor)
                .filter(Competitor.name != name)
                .filter(
                    or_(
                        Competitor.id == match.competitor_1_id,
                        Competitor.id == match.competitor_2_id,
                    )
                )
                .one()
            )
        except NoResultFound:
            # Tratar o caso em que o perdedor não é encontrado
            session.rollback()
            raise ValueError('Competitor not found or match is not valid')

        # Atualizar o estado dos competidores
        competitor_winner.won = True
        competitor_loser.won = False

        # Atualizar o estado do jogo
        match.winner_id = competitor_winner.id
        match.state = STATUS_FINISHED

        session.commit()

        return match
