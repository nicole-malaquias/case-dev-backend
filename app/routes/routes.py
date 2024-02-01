from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_session
from app.models import Competitor, Match, Tournament
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
    """
    Registra competidores em um torneio

    Parameters:
        - tournament_id: O ID do torneio.
        - names: [string].
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
    Obtém a lista de partidas para um torneio específico.

    Parameters:
        - tournament_id: O ID do torneio.
        - session: Sessão do SQLAlchemy.

    Returns:
        Um dicionário contendo informações sobre as partidas.
    """
    Match.create_match(tournament_id, session)

    matches_info = Match.list_matches(tournament_id, session)

    return matches_info
