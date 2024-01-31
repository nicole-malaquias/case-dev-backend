from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_session
from app.models import Competitor, Tournament
from app.schemas import (
    CompetitorSchema,
    TournamentSchema,
    TournamentSchemaResponse,
)

router = APIRouter(prefix='', tags=['/'])

Session = Annotated[Session, Depends(get_session)]


@router.post(
    '/tournament', status_code=201, response_model=TournamentSchemaResponse
)
def create_tournament(tournament: TournamentSchema, session: Session):
    """
    Cria um torneio

    - **name**: Nome do torneio
    - **date_start**: Data de início do torneio
    - **date_end**: Data de término do torneio

    """
    new_tourament = Tournament.create_tournament(**tournament.dict())
    session.add(new_tourament)
    session.commit()
    session.refresh(new_tourament)

    return new_tourament


@router.post('/tournament/{tournament_id}/competitor', status_code=201)
def register_competitors(
    tournament_id: int, competitor: CompetitorSchema, session: Session
):
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
def match_list(
    tournament_id: int, competitor: CompetitorSchema, session: Session
):
    try:
        Competitor.create_competitor(
            names=competitor.names,
            tournament_id=tournament_id,
            session=session,
        )
        return None
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
