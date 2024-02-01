import logging
from datetime import datetime

import pytest
from sqlalchemy.orm import Session
from sqlalchemy.sql import select

from app.models import Competitor, Tournament

logger = logging.getLogger(__name__)


def test_create_tournament(session):
    logger.info('Testing creating a tournament...')
    new_tournament = Tournament(
        name='Sample Tournament',
        date_start=datetime.now(),
        date_end=datetime.now(),
    )
    session.add(new_tournament)
    session.commit()

    tournament = session.scalar(
        select(Tournament).where(Tournament.name == 'Sample Tournament')
    )

    assert tournament.name == 'Sample Tournament'
    assert tournament.date_start is not None
    assert tournament.date_end is not None
    logger.info('Tournament created successfully.')


def test_create_competitor_invalid_tournament_id(session: Session):
    logger.info('Testing creating a competitor with invalid tournament ID...')
    invalid_tournament_id = 999

    competitor_names = ['Competitor1', 'Competitor2']

    with pytest.raises(ValueError) as exc_info:
        Competitor.create_competitor(
            competitor_names, invalid_tournament_id, session
        )

    assert 'Tournament with ID' in str(exc_info.value)
    assert str(invalid_tournament_id) in str(exc_info.value)

    competitors = session.query(Competitor).all()
    assert len(competitors) == 0
    logger.info(
        'Competitor creation with invalid tournament ID tested successfully.'
    )
