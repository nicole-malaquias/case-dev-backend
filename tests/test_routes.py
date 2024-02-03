from app.models import Competitor, Match, Tournament


def test_create_tournament_success(client, session):
    payload = {
        'name': 'Torneio de Exemplo',
        'date_start': '2024-01-29T12:00:00',
        'date_end': '2024-02-05T18:00:00',
    }

    response = client.post('/tournament', json=payload)

    assert response.status_code == 201

    expected_fields = ['id', 'name', 'date_start', 'date_end']
    fields_present = [field in response.json() for field in expected_fields]

    assert all(fields_present)


def test_create_tournament_failure_invalid_dates(client, session):
    """
    Test creating a tournament with invalid date range.

    - Attempts to create a tournament with invalid date range.
    - Checks if the response status code is 422 (Unprocessable Entity).
    """
    payload = {
        'name': 'Example Tournament',
        'date_start': '2024-02-05T18:00:00',
        'date_end': '2024-01-29T12:00:00',
    }
    response = client.post('/tournament', json=payload)

    assert response.status_code == 422


def test_register_competitors_tournament_not_found(client, session):
    """
    Test registering competitors for a nonexistent tournament.

    - Attempts to register competitors for a tournament with ID 999.
    - Checks if the response status code is 404 (Not Found).
    - Checks if the response detail contains the expected message.
    """
    tournament_id = 999
    competitor_payload = {
        'names': ['Competitor1', 'Competitor2', 'Competitor3']
    }
    response = client.post(
        f'/tournament/{tournament_id}/competitor', json=competitor_payload
    )

    assert response.status_code == 404
    assert 'Tournament with ID' in response.json()['detail']


def test_register_competitors_single_name_failure(client, session):
    """
    Test registering a single competitor for a tournament (failure).

    - Creates a tournament.
    - Attempts to register a single competitor for the tournament.
    - Checks if the response status code is 404 (Not Found).
    - Checks if the response detail contains the expected message.
    """
    payload = {
        'name': 'Example Tournament',
        'date_start': '2024-01-29T12:00:00',
        'date_end': '2024-02-05T18:00:00',
    }
    response = client.post('/tournament', json=payload)
    tournament_id = response.json().get('id', '')
    competitor_payload = {'names': ['SingleName']}
    response = client.post(
        f'/tournament/{tournament_id}/competitor', json=competitor_payload
    )

    assert response.status_code == 404
    assert (
        'A tournament must have at least 2 competitors.'
        in response.json()['detail']
    )


def test_register_competitors_success(client, session):
    """
    Test successfully registering competitors for a tournament.

    - Creates a tournament.
    - Registers two competitors for the tournament.
    - Checks if the response status code is 201 (Created).
    - Checks if the response JSON is None.
    """
    payload = {
        'name': 'Example Tournament',
        'date_start': '2024-01-29T12:00:00',
        'date_end': '2024-02-05T18:00:00',
    }
    response = client.post('/tournament', json=payload)
    tournament_id = response.json().get('id', '')
    competitor_payload = {'names': ['Competitor1', 'Competitor2']}
    response = client.post(
        f'/tournament/{tournament_id}/competitor', json=competitor_payload
    )

    assert response.status_code == 201
    assert response.json() is None


def test_get_match_list_with_two_competitors(client, session):
    """
    Test getting the match list for a tournament with two competitors.

    - Creates a tournament.
    - Registers two competitors for the tournament.
    - Gets the list of matches for the tournament.
    - Checks if the response status code is 201 (Created).
    """
    payload = {
        'name': 'Example Tournament',
        'date_start': '2024-01-29T12:00:00',
        'date_end': '2024-02-05T18:00:00',
    }
    response = client.post('/tournament', json=payload)
    tournament_id = response.json().get('id', '')
    competitor_payload = {'names': ['Competitor1', 'Competitor2']}
    response = client.post(
        f'/tournament/{tournament_id}/competitor', json=competitor_payload
    )

    response = client.get(f'/tournament/{tournament_id}/match')

    assert response.status_code == 201


def test_create_tournament_and_register_odd_number_of_comp_get_match_list(
    client, session
):
    """
    Test creating a tournament, registering an odd number of competitors,
    and getting the match list.

    - Creates a tournament.
    - Registers five competitors for the tournament.
    - Checks if the response status code is 201 (Created).
    """
    tournament_payload = {
        'name': 'Example Tournament',
        'date_start': '2024-01-29T12:00:00',
        'date_end': '2024-02-05T18:00:00',
    }
    tournament_response = client.post('/tournament', json=tournament_payload)
    tournament_id = tournament_response.json().get('id', '')

    assert tournament_response.status_code == 201

    competitors_payload = {
        'names': [
            'Competitor1',
            'Competitor2',
            'Competitor3',
            'Competitor4',
            'Competitor5',
        ]
    }
    competitors_response = client.post(
        f'/tournament/{tournament_id}/competitor', json=competitors_payload
    )

    assert competitors_response.status_code == 201


def test_create_match_with_odd_number_of_competitors(client, session):
    """
    Test creating a match with an odd number of competitors.

    - Creates a tournament.
    - Registers three competitors for the tournament.
    - Creates matches for the tournament.
    - Gets the list of matches for the tournament.
    - Checks if the response status code is 201 (Created).
    """
    tournament_payload = {
        'name': 'Example Tournament',
        'date_start': '2024-01-29T12:00:00',
        'date_end': '2024-02-05T18:00:00',
    }
    tournament_response = client.post('/tournament', json=tournament_payload)
    tournament_id = tournament_response.json().get('id', '')

    assert tournament_response.status_code == 201

    competitors_payload = {
        'names': ['Competitor1', 'Competitor2', 'Competitor3']
    }
    competitors_response = client.post(
        f'/tournament/{tournament_id}/competitor', json=competitors_payload
    )

    assert competitors_response.status_code == 201

    Match.create_match(tournament_id, session)

    matches_response = client.get(f'/tournament/{tournament_id}/match')

    assert matches_response.status_code == 201


def test_get_match_list_for_nonexistent_tournament(client, session):
    """
    Test getting the match list for a nonexistent tournament.

    - Attempts to get the list of matches for a tournament with ID 999.
    - Checks if the response status code is 404 (Not Found).
    - Checks if the response JSON contains the expected detail message.
    """
    response = client.get('/tournament/999/match')

    assert response.status_code == 404

    assert response.json() == {'detail': 'Tournament with ID 999 not found.'}


def test_set_winner_for_nonexistent_tournament(client, session):
    """
    Test setting a winner for a match in a nonexistent tournament.

    - Attempts to set a winner for a match in a tournament with ID 999.
    - Checks if the response status code is 404 (Not Found).
    """
    response = client.post('/tournament/999/match/1', json={'name': 'winner'})

    assert response.status_code == 404


def test_set_winner_for_match_successfully(client, session):
    """
    Test the process of setting a winner for a match successfully.

    - Creates a tournament.
    - Adds two competitors to the tournament.
    - Retrieves the created competitors.
    - Creates a match for the competitors.
    - Sets a winner for the match.
    - Checks if the response was successful (status code 201).
    """
    # Creates a tournament
    tournament_payload = {
        'name': 'Tournament set winner',
        'date_start': '2024-01-29T12:00:00',
        'date_end': '2024-02-05T18:00:00',
    }
    new_tournament = Tournament(**tournament_payload)
    session.add(new_tournament)
    session.commit()

    competitor1 = Competitor(
        name='Competitor1', tournament_id=new_tournament.id, group='group_1'
    )
    competitor2 = Competitor(
        name='Competitor2', tournament_id=new_tournament.id, group='group_1'
    )
    session.add_all([competitor1, competitor2])
    session.commit()

    competitor_1 = (
        session.query(Competitor).filter_by(name='Competitor1').first()
    )
    competitor_2 = (
        session.query(Competitor).filter_by(name='Competitor2').first()
    )

    new_match = Match(
        competitor_1_id=competitor_1.id,
        competitor_2_id=competitor_2.id,
        tournament_id=new_tournament.id,
        round=1,
        state='pending',
    )
    session.add(new_match)
    session.commit()

    response = client.post(
        f'/tournament/{new_tournament.id}/match/{new_match.id}',
        json={'name': 'Competitor1'},
    )

    assert response.status_code == 201
