from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_session
from app.models import Tournament
from app.schemas import TournamentSchema

router = APIRouter(prefix='', tags=['/'])

Session = Annotated[Session, Depends(get_session)]


@router.post('/tournament', status_code=201, response_model=TournamentSchema)
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
