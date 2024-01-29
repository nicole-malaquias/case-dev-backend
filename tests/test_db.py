from datetime import datetime

from sqlalchemy import select

from app.models import Tournament


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
