import logging
import math
import random
from typing import Annotated

from fastapi import Depends
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
from sqlalchemy.orm import DeclarativeBase, Session, relationship
from sqlalchemy.orm.exc import NoResultFound

from app.database import get_session

GROUP_1 = 'group_1'
GROUP_2 = 'group_2'
STATUS_FINISHED = 'finished'
STATUS_PENDING = 'pending'

Session = Annotated[Session, Depends(get_session)]
logger = logging.getLogger(__name__)


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
    is_active = Column(
        Boolean,
        default=False,
    )

    @classmethod
    def create_tournament(cls, session: Session, **kwargs):
        """
        Creates a new tournament.

        Parameters:
            - session: SQLAlchemy session.
            - **kwargs: Additional tournament data.

        Returns:
            The created tournament.
        """

        new_tournament = cls(**kwargs)
        session.add(new_tournament)
        session.commit()
        logger.info('Tournament inserted in the bank.')
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

    @classmethod
    def _number_of_matches(cls, number_competitors):
        return math.ceil(math.log2(number_competitors))

    @classmethod
    def create_competitors(cls, names, tournament_id, session):
        """
        Creates competitors and validates that the tournament ID
        they are joining they want to participate exists.
        Adds competitors to a group similar to the brackets
        of the championship.
        """
        existing_tournament = session.query(Tournament).get(tournament_id)
        if existing_tournament is None:
            raise ValueError(f'Tournament with ID {tournament_id} not found.')

        if existing_tournament.is_active:
            raise ValueError(
                'This championship has already started; adding new competitors is not allowed.'  # noqa
            )

        if len(names) < 2:
            raise ValueError('A tournament must have at least 2 competitors.')

        random.shuffle(names)
        competitors = []

        for ind, name in enumerate(names):
            group = GROUP_1 if ind % 2 == 0 else GROUP_2
            competitor_name = f'{name} -{random.randint(1, 100)}'
            new_competitor = cls(
                name=competitor_name,
                tournament_id=tournament_id,
                group=group,
            )
            competitors.append(new_competitor)

        session.add_all(competitors)
        session.commit()
        number_matches = cls._number_of_matches(len(names))
        existing_tournament.number_matches = number_matches
        existing_tournament.is_active = True
        logger.info('Competitors inserted in the bank.')


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
        """
        This method sets the pairs for the matches.
        If a list with an odd value arrives,
        place one of the items alone in a tuple

        """
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
    def create_match(cls, tournament_id: int, session: Session):
        """
        This method creates matches for a tournament,
        verifies if it is the last round,
        and adds the competitors to their respective matches.
        """
        logging.info('Start creating matches.')
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
        is_consolation_match = cls._should_create_consolation(
            existing_tournament.number_matches, matches
        )
        logging.info('Verifying if the consolation match should be created.')
        if is_consolation_match:
            cls._create_consolation_match(
                tournament_id, existing_tournament.number_matches, session
            )
            return

        logging.info('Verifying if the final match should be created.')
        is_final_match = cls._should_create_final_match(
            existing_tournament, matches
        )

        if is_final_match:
            cls._create_final_match(
                session, tournament_id, existing_tournament.number_matches
            )
            return

        if (
            matches
            and matches[0].round == existing_tournament.number_matches + 1
        ):
            logging.info('Its not necessary create the match')
            return

        if matches and matches[0].state == STATUS_PENDING:
            logging.info('Its not necessary create the match')

            return
        if matches:
            round = matches[0].round + 1
        else:
            round = 1
        logging.info('Start creating matches for group 1 and 2.')

        pairs_group_1 = cls._set_pair(competitors_group_1)
        pairs_group_2 = cls._set_pair(competitors_group_2)
        cls._create_matches_for_group(
            session, tournament_id, pairs_group_1, round
        )
        cls._create_matches_for_group(
            session, tournament_id, pairs_group_2, round
        )

    @staticmethod
    def _get_competitors_by_group(
        session: Session, tournament_id: int, group: str
    ):
        """
        This method gets the competitors by group.
        """
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

    @staticmethod
    def _should_create_final_match(existing_tournament, matches):

        """
        This method verifies if the final match should be created.
        """

        total_atual = matches[0].round if matches else 0

        total_experado = existing_tournament.number_matches + 1
        total = total_experado - total_atual

        # caso exista só duas pessoas no torneio
        if existing_tournament.number_matches == 1 and total_atual == 0:
            return True

        if total == 1:
            return True
        if total_experado == 1 and total_atual == 0:
            return True

        return False

    @staticmethod
    def _create_final_match(
        session: Session, tournament_id: int, last_round: int
    ):
        """
        This method creates the final match.
        """
        finalists = (
            session.query(Competitor)
            .filter(
                Competitor.tournament_id == tournament_id,
                Competitor.status == True,  # noqa
            )
            .limit(2)
            .all()
        )

        if len(finalists) == 2:
            finalists = Match(
                competitor_1_id=finalists[0].id,
                competitor_2_id=finalists[1].id,
                tournament_id=tournament_id,
                round=last_round + 1,
                state=STATUS_PENDING,
            )

            session.add(finalists)
            session.commit()
            logging.info('Final match created.')

    def _create_matches_for_group(
        session: Session,
        tournament_id: int,
        pairs: list[Competitor],
        round: int,
    ):
        """
        This method creates the matches for a group.
        """
        for pair in pairs:
            if len(pair) == 2:
                new_match = Match(
                    competitor_1_id=pair[0].id,
                    competitor_2_id=pair[1].id,
                    tournament_id=tournament_id,
                    round=round,
                    state=STATUS_PENDING,
                )
                session.add(new_match)
            else:
                new_match = Match(
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
    def list_matches(cls, tournament_id: int, session: Session):
        """
        This method lists all matches from a tournament.
        """
        logging.info('Finding matches.')

        try:
            matches = (
                session.query(Match)
                .filter_by(tournament_id=tournament_id)
                .order_by(desc(Match.round))
                .all()
            )

            if not matches:
                raise NoResultFound(
                    'No matches found for the specified tournament.'
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

            logging.info('Matches found.')
            return dic

        except NoResultFound as e:
            logging.warning(
                f'No matches found for tournament with ID {tournament_id}.'
            )
            raise ValueError(str(e))

    @classmethod
    def set_winner(cls, match_id: int, name: str, session: Session):
        """
        This method sets the winner of a match and updates the state of the
        competitors.
        """

        logging.info('Setting the winner of the match.')
        name = name.get('name', '')
        match = session.query(Match).get(match_id)
        if match is None:
            logging.error(f'Match with ID {match_id} not found.')
            raise ValueError(f'Match with ID {match_id} not found.')

        competitor_winner = (
            session.query(Competitor)
            .filter(Competitor.name == name, Match.id == match_id)
            .first()
        )

        if competitor_winner is None:
            logging.error(f'Competitor with name {name} not found.')
            raise ValueError(f'Competitor with name {name} not found.')

        competitor_loser = (
            session.query(Competitor)
            .filter(Competitor.name != name)
            .filter(
                or_(
                    Competitor.id == match.competitor_1_id
                    if match.competitor_1_id
                    else False,
                    Competitor.id == match.competitor_2_id
                    if match.competitor_2_id
                    else False,
                )
            )
            .one_or_none()
        )

        if competitor_loser is None:
            session.rollback()
            logging.error('Competitor not found or match is not valid.')
            raise ValueError('Competitor not found or match is not valid')

        competitor_loser.status = False
        competitor_winner.won = True
        competitor_loser.won = False

        match.winner_id = competitor_winner.id
        match.state = STATUS_FINISHED

        session.commit()

        return match

    @classmethod
    def get_top4(cls, tournament: int, session: Session):
        """
        Fetches the finalists and determines the winner, 2nd place,
        fetches the semifinalists and determines the 3rd and 4th places.
        """

        championship = session.query(Tournament).get(tournament)
        competitors = (
            session.query(Competitor)
            .filter(Competitor.tournament_id == tournament)
            .all()
        )
        if len(competitors) == 2 and championship.number_matches == 1:
            result = {}
            for competitor in competitors:
                if competitor.status:
                    result['first'] = competitor.name.split(' ')[0]
                else:
                    result['second'] = competitor.name.split(' ')[0]
            return result

        finalists = (
            session.query(Match)
            .filter(
                Match.tournament_id == tournament,
                Match.round == championship.number_matches + 1,
            )
            .all()
        )
        winner = finalists[0].winner.name.split()
        second_place = (
            finalists[0].competitor_2.name
            if finalists[0].competitor_1.name == winner
            else finalists[0].competitor_1.name
        )

        semi_finalists = (
            session.query(Match)
            .filter(
                Match.tournament_id == tournament,
                Match.round == championship.number_matches,
            )
            .all()
        )

        third_place_winner = semi_finalists[0].winner.name
        fourth_place = (
            semi_finalists[0].competitor_2.name
            if semi_finalists[0].competitor_1.name == third_place_winner
            else semi_finalists[0].competitor_1.name
        )

        result = {
            'winner': winner,
            'second_place': second_place,
            'third_place': third_place_winner,
            'fourth_place': fourth_place,
        }
        return 'result'

    @staticmethod
    def _create_consolation_match(
        tournament_id: int, last_round: int, session: Session
    ):
        """
        Creates a consolation match for a tournament.

        Args:
            tournament_id (int): The ID of the tournament.
            last_round (int): The last round number.
            session (Session): The SQLAlchemy session.

        """
        penultimate_round = last_round - 1

        # Verify if a consolation match should be created
        is_consolation = (
            session.query(Match)
            .filter(
                Match.tournament_id == tournament_id,
                Match.round == last_round,
            )
            .all()
        )
        for match in is_consolation:
            from pprint import pprint

            pprint(vars(match))
            if match.state == STATUS_PENDING:
                return

        if penultimate_round >= 1 and not is_consolation:
            # Query matches from the last completed round
            semi_finalists_matches = (
                session.query(Match)
                .filter(
                    Match.tournament_id == tournament_id,
                    Match.round == penultimate_round,
                )
                .all()
            )

            losers = []
            for match in semi_finalists_matches:
                competitor_1_id = match.competitor_1_id
                competitor_2_id = match.competitor_2_id

                if competitor_1_id is not None and competitor_2_id is not None:
                    losers.append(
                        competitor_1_id
                        if match.winner_id == competitor_2_id
                        else competitor_2_id
                    )
                elif competitor_1_id is not None:
                    losers.append(competitor_1_id)
                elif competitor_2_id is not None:
                    losers.append(competitor_2_id)
                else:
                    pass
            # Create a new match for the consolation semi-final

            new_semi_final_match = Match(
                competitor_1_id=losers[0],
                competitor_2_id=losers[1],
                tournament_id=tournament_id,
                round=last_round,
                state=STATUS_PENDING,
            )
            session.add(new_semi_final_match)
            session.commit()
            logging.info('Consolation match created.')

    @staticmethod
    def _should_create_consolation(total, matches):
        """
        This method verifies if a consolation match should be created.
        """
        if matches:
            total_atual = matches[0].round
            sub = total - total_atual
            if sub == 1:
                return True
        return False
