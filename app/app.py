from fastapi import FastAPI

from .schemas import TournamentSchema

app = FastAPI()


@app.post('/tournament/', status_code=201, response_model=TournamentSchema)
def create_tournament(tournament: TournamentSchema):
    """
    Cria um torneio

    - **name**: Nome do torneio
    - **date_start**: Data de início do torneio
    - **date_end**: Data de término do torneio

    """
    return tournament
