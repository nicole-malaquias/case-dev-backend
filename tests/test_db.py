from datetime import datetime

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Competitor, Tournament


def test_create_tournament(session):
    # Crie um novo torneio
    new_tournament = Tournament(
        name='Sample Tournament',
        date_start=datetime.now(),
        date_end=datetime.now(),
    )
    session.add(new_tournament)
    session.commit()

    # Consulte o torneio pelo nome
    tournament = session.scalar(
        select(Tournament).where(Tournament.name == 'Sample Tournament')
    )

    # Verifique se o torneio foi criado corretamente
    assert tournament.name == 'Sample Tournament'
    assert tournament.date_start is not None
    assert tournament.date_end is not None


def test_create_competitor_invalid_tournament_id(session: Session):
    # Tente criar competidores com um 'tournament_id' que não existe
    invalid_tournament_id = 999  # Um ID que não deve existir no banco de dados

    # Dados do competidor a serem criados
    competitor_names = ['Competitor1', 'Competitor2']

    # Tente criar competidores com um 'tournament_id' inválido
    with pytest.raises(ValueError) as exc_info:
        Competitor.create_competitor(
            competitor_names, invalid_tournament_id, session
        )

    # Verifique se a exceção tem a mensagem esperada
    assert 'Tournament with ID' in str(exc_info.value)
    assert str(invalid_tournament_id) in str(exc_info.value)

    # Certifique-se de que não há competidores criados no banco de dados
    competitors = session.query(Competitor).all()
    assert len(competitors) == 0
