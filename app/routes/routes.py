import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_session
from app.models import Competitor, Match, Tournament
from app.schemas import (
    CompetitorSchema,
    TournamentSchema,
    TournamentSchemaResponse,
    WinnerRegistrationSchema,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix='', tags=['/'])

Session = Annotated[Session, Depends(get_session)]


@router.post(
    '/tournament', status_code=201, response_model=TournamentSchemaResponse
)
def create_tournament(tournament: TournamentSchema, session: Session):
    """
    Creates a new tournament.

    Parameters:
        - tournament: Tournament data (TournamentSchema).
        - session: SQLAlchemy session.

    Returns:
        The created tournament.
    """
    try:

        new_tournament = Tournament.create_tournament(
            session=session, **tournament.dict()
        )

        return new_tournament
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))


@router.post('/tournament/{tournament_id}/competitor', status_code=201)
def register_competitors(
    tournament_id: int, competitor: CompetitorSchema, session: Session
):
    """
    Registers competitors in a tournament.

    Parameters:
        - tournament_id: The ID of the tournament.
        - names: List of competitor names.
    """
    try:
        Competitor.create_competitor(
            names=competitor.names,
            tournament_id=tournament_id,
            session=session,
        )
        return None
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get('/tournament/{tournament_id}/match', status_code=201)
def get_match_list(tournament_id: int, session: Session):
    """
    Gets the list of matches for a specific tournament.

    Parameters:
        - tournament_id: The ID of the tournament.
        - session: SQLAlchemy session.

    Returns:
        A dictionary containing information about the matches.
    """
    try:

        Match.create_match(tournament_id, session)

        matches_info = Match.list_matches(tournament_id, session)

        return matches_info
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post('/tournament/{tournament_id}/match/{match_id}', status_code=201)
def put_winner_for_match(
    tournament_id: int,
    match_id: int,
    winner: WinnerRegistrationSchema,
    session: Session,
):
    """
    Sets the winner of a match in a specific tournament.

    Parameters:
        - tournament_id: The ID of the tournament.
        - match_id: The ID of the match.
        - winner: Winner data (WinnerRegistrationSchema).
        - session: SQLAlchemy session.

    Returns:
        A dictionary containing information about the matches.
    """
    try:
        winner_data = winner.dict()
        match_instance = Match()
        match_instance.set_winner(match_id, winner_data, session)

        success_message = f'Winner successfully updated for match {match_id}'
        return {'message': success_message, 'matches_info': match_instance}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get('/tournament/{tournament_id}/result', status_code=201)
def get_top4(tournament: int, session: Session):
    """
    Gets the top 4 competitors in a specific tournament.

    Parameters:
        - tournament_id: The ID of the tournament.
        - session: SQLAlchemy session.

    Returns:
        A dictionary containing information about the top 4 competitors.
    """
    try:
        top4 = Match.get_top4(tournament, session)
        return top4
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
