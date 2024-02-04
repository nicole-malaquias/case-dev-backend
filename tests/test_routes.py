from app.models import Competitor, Match, Tournament


def create_test_tournament(client, session):
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


def test_register_competitor_after_tournament_start(client, session):
    ...
    payload = {
        'name': 'Example Tournament',
        'date_start': '2024-01-29T12:00:00',
        'date_end': '2024-02-05T18:00:00',
    }
    tournamnet = client.post('/tournament', json=payload)
    tournament_id = tournamnet.json().get('id', '')
    competitor_payload = {
        'names': ['Competitor1', 'Competitor2', 'Competitor3']
    }
    client.post(
        f'/tournament/{tournament_id}/competitor', json=competitor_payload
    )
    response = client.post(
        f'/tournament/{tournament_id}/competitor', json=competitor_payload
    )
    print('\n' * 5)
    print(response.json())


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

    assert response.status_code == 400

    assert response.json() == {'detail': 'Tournament with ID 999 not found.'}


def test_set_winner_for_nonexistent_tournament(client, session):
    """
    Test setting a winner for a match in a nonexistent tournament.

    - Attempts to set a winner for a match in a tournament with ID 999.
    - Checks if the response status code is 404 (Not Found).
    """
    response = client.post('/tournament/999/match/1', json={'name': 'winner'})
    print('\n' * 5)
    print(response.json())
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


def test_winner_consolation_match(client, session):

    tournament_payload = {
        'name': 'Tournament Teste Consolation',
        'date_start': '2024-01-29T12:00:00',
        'date_end': '2024-02-05T18:00:00',
        'number_matches': 30,
    }

    new_tournament = Tournament(**tournament_payload)
    session.add(new_tournament)
    session.commit()

    for i in range(0, 4):
        if i % 2 == 0:
            competitor = Competitor(
                name=f'Competitor{i}',
                tournament_id=new_tournament.id,
                group='group_1',
            )
            session.add(competitor)
            session.commit()
        else:
            competitor = Competitor(
                name=f'Competitor{i}',
                tournament_id=new_tournament.id,
                group='group_2',
            )
            session.add(competitor)
            session.commit()

    competitors = (
        session.query(Competitor)
        .filter_by(tournament_id=new_tournament.id)
        .all()
    )

    first_match = Match(
        competitor_1_id=competitors[0].id,
        competitor_2_id=competitors[1].id,
        tournament_id=new_tournament.id,
        round=1,
        winner_id=competitors[0].id,
        state='finished',
    )

    secont_match = Match(
        competitor_1_id=competitors[2].id,
        competitor_2_id=competitors[3].id,
        tournament_id=new_tournament.id,
        round=1,
        winner_id=competitors[2].id,
        state='finished',
    )

    session.add_all([first_match, secont_match])
    session.commit()

    response = client.get(
        f'/tournament/{new_tournament.id}/match/',
    )

    assert response.status_code == 201


def test_create_consolation_match(client, session):

    tournament_payload = {
        'name': 'Example Tournament',
        'date_start': '2024-01-29T12:00:00',
        'date_end': '2024-02-05T18:00:00',
    }
    tournament_response = client.post('/tournament', json=tournament_payload)
    tournament_id = tournament_response.json().get('id', '')

    competitor_payload = {
        'names': ['Competitor1', 'Competitor2', 'Competitor3', 'Competitor4']
    }
    client.post(
        f'/tournament/{tournament_id}/competitor', json=competitor_payload
    )

    response = client.get(f'/tournament/{tournament_id}/match')

    rodada_1_winner = response.json()['Round 1'][0]['competitor_1']
    rodada_1_id = response.json()['Round 1'][0]['id']

    rodada_2_winner = response.json()['Round 1'][1]['competitor_2']
    rodada_2_id = response.json()['Round 1'][1]['id']

    response_rodada_1 = client.post(
        f'/tournament/{tournament_id}/match/{rodada_1_id}',
        json={'name': rodada_1_winner},
    )
    assert response_rodada_1.status_code == 201

    response_rodada_2 = client.post(
        f'/tournament/{tournament_id}/match/{rodada_2_id}',
        json={'name': rodada_2_winner},
    )
    assert response_rodada_2.status_code == 201

    response = client.get(f'/tournament/{tournament_id}/match')

    assert response.status_code == 201


def test_get_to_generate_the_final_list_and_not_create_unnecessary(
    client, session
):
    tournament_payload = {
        'name': 'Example Tournament',
        'date_start': '2024-01-29T12:00:00',
        'date_end': '2024-02-05T18:00:00',
    }
    tournament_response = client.post('/tournament', json=tournament_payload)
    tournament_id = tournament_response.json().get('id', '')

    competitor_payload = {
        'names': ['Competitor1', 'Competitor2', 'Competitor3', 'Competitor4']
    }
    client.post(
        f'/tournament/{tournament_id}/competitor', json=competitor_payload
    )

    response = client.get(f'/tournament/{tournament_id}/match')

    rodada_1_winner = response.json()['Round 1'][0]['competitor_1']
    rodada_1_id = response.json()['Round 1'][0]['id']

    rodada_2_winner = response.json()['Round 1'][1]['competitor_2']
    rodada_2_id = response.json()['Round 1'][1]['id']

    response_rodada_1 = client.post(
        f'/tournament/{tournament_id}/match/{rodada_1_id}',
        json={'name': rodada_1_winner},
    )
    assert response_rodada_1.status_code == 201

    response_rodada_2 = client.post(
        f'/tournament/{tournament_id}/match/{rodada_2_id}',
        json={'name': rodada_2_winner},
    )
    assert response_rodada_2.status_code == 201

    response = client.get(f'/tournament/{tournament_id}/match')

    assert response.status_code == 201

    response = client.get(f'/tournament/{tournament_id}/match')

    rodada_consoletion = response.json()['Round 2'][0]['competitor_2']
    rodada_id = response.json()['Round 2'][0]['id']

    client.post(
        f'/tournament/{tournament_id}/match/{rodada_id}',
        json={'name': rodada_consoletion},
    )

    client.get(f'/tournament/{tournament_id}/match')

    rodada_winner = response.json()['Round 3'][0]['competitor_2']
    rodada_id = response.json()['Round 3'][0]['id']
    client.post(
        f'/tournament/{tournament_id}/match/{rodada_id}',
        json={'name': rodada_winner},
    )
    response = client.get(f'/tournament/{tournament_id}/match')
    response = client.get(f'/tournament/{tournament_id}/match')
    assert len(response.json()) == 3


def create_tournament(client, session, tournament_payload):
    response = client.post('/tournament', json=tournament_payload)
    return response.json().get('id', '')


def create_competitors(client, tournament_id, competitor_payload):
    client.post(
        f'/tournament/{tournament_id}/competitor', json=competitor_payload
    )


def create_match(client, tournament_id, match_id, winner_name):
    response = client.post(
        f'/tournament/{tournament_id}/match/{match_id}',
        json={'name': winner_name},
    )
    assert response.status_code == 201


def get_matches(client, tournament_id):
    response = client.get(f'/tournament/{tournament_id}/match')
    assert response.status_code == 201
    return response.json()


def test_get_top4(client, session):
    tournament_payload = {
        'name': 'Example Tournament',
        'date_start': '2024-01-29T12:00:00',
        'date_end': '2024-02-05T18:00:00',
    }
    competitor_payload = {
        'names': ['Competitor1', 'Competitor2', 'Competitor3', 'Competitor4']
    }

    tournament_id = create_tournament(client, session, tournament_payload)
    create_competitors(client, tournament_id, competitor_payload)

    matches_round_1 = get_matches(client, tournament_id)['Round 1']

    create_match(
        client,
        tournament_id,
        matches_round_1[0]['id'],
        matches_round_1[0]['competitor_1'],
    )
    create_match(
        client,
        tournament_id,
        matches_round_1[1]['id'],
        matches_round_1[1]['competitor_2'],
    )

    matches_round_2 = get_matches(client, tournament_id)['Round 2']
    create_match(
        client,
        tournament_id,
        matches_round_2[0]['id'],
        matches_round_2[0]['competitor_2'],
    )

    matches_round_3 = get_matches(client, tournament_id)['Round 3']
    create_match(
        client,
        tournament_id,
        matches_round_3[0]['id'],
        matches_round_3[0]['competitor_2'],
    )


def test_get_top4_with_two_competitor(client, session):
    """
    Test the retrieval of the top 4 competitors
      in a tournament with two competitors.

    Steps:
    1. Create a tournament.
    2. Add two competitors to the tournament.
    3. Retrieve the matches of the tournament.
    4. Post the result of the first match.
    5. Retrieve the matches again.
    6. Retrieve the results of the tournament.

    Verify if all steps are successful and if the status codes are correct.
    """
    # Step 1: Create Tournament
    tournament_payload = {
        'name': 'Example Tournament',
        'date_start': '2024-01-29T12:00:00',
        'date_end': '2024-02-05T18:00:00',
    }
    response_create_tournament = client.post(
        '/tournament', json=tournament_payload
    )
    assert response_create_tournament.status_code == 201
    tournament_id = response_create_tournament.json().get('id')

    # Step 2: Add Competitors
    competitor_payload = {'names': ['Competitor1', 'Competitor2']}
    response_add_competitors = client.post(
        f'/tournament/{tournament_id}/competitor', json=competitor_payload
    )
    assert response_add_competitors.status_code == 201

    # Step 3: Retrieve Matches
    response_get_matches = client.get(f'/tournament/{tournament_id}/match')
    assert response_get_matches.status_code == 201
    matches_round_1 = response_get_matches.json()

    # Verify if there are available matches
    assert 'Round 2' in matches_round_1
    assert matches_round_1['Round 2']

    # Step 4: Post Match Result
    winner_name = matches_round_1['Round 2'][0]['competitor_1']
    match_id = matches_round_1['Round 2'][0]['id']
    response_post_match_result = client.post(
        f'/tournament/{tournament_id}/match/{match_id}',
        json={'name': winner_name},
    )
    assert response_post_match_result.status_code == 201

    # Step 5: Retrieve Matches Again
    response_get_matches_again = client.get(
        f'/tournament/{tournament_id}/match'
    )
    assert response_get_matches_again.status_code == 201

    # Step 6: Retrieve Tournament Results
    response_get_tournament_result = client.get(
        f'/tournament/{tournament_id}/result'
    )
    assert response_get_tournament_result.status_code == 201
