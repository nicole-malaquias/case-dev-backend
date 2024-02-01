from app.models import Match


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


def test_create_tournament_failure(client, session):
    payload = {
        'name': 'Torneio de Exemplo',
        'date_start': '2024-02-05T18:00:00',
        'date_end': '2024-01-29T12:00:00',
    }
    response = client.post('/tournament', json=payload)

    assert response.status_code == 422


def test_register_competitors_tournament_not_found(client, session):

    tournament_id = 999

    competitor_payload = {
        'names': ['Competitor1', 'Competitor2', 'Competitor3'],
    }

    response = client.post(
        f'/tournament/{tournament_id}/competitor', json=competitor_payload
    )

    assert response.status_code == 404
    assert 'Tournament with ID' in response.json()['detail']


def test_register_competitors_single_name_failure(client, session):
    payload = {
        'name': 'Torneio de Exemplo',
        'date_start': '2024-01-29T12:00:00',
        'date_end': '2024-02-05T18:00:00',
    }

    response = client.post('/tournament', json=payload)
    tournament_id = response.json().get('id', '')
    competitor_payload = {
        'names': ['SingleName'],
    }

    response = client.post(
        f'/tournament/{tournament_id}/competitor', json=competitor_payload
    )

    assert response.status_code == 404
    assert (
        'A tournament must have at least 2 competitors.'
        in response.json()['detail']
    )


def test_register_competitors_success(client, session):
    payload = {
        'name': 'Torneio de Exemplo',
        'date_start': '2024-01-29T12:00:00',
        'date_end': '2024-02-05T18:00:00',
    }

    response = client.post('/tournament', json=payload)
    tournament_id = response.json().get('id', '')
    competitor_payload = {
        'names': ['Competitor1', 'Competitor2'],
    }

    response = client.post(
        f'/tournament/{tournament_id}/competitor', json=competitor_payload
    )

    assert response.status_code == 201
    assert response.json() is None


def test_get_match_list_with_two_competitors(client, session):

    payload = {
        'name': 'Torneio de Exemplo',
        'date_start': '2024-01-29T12:00:00',
        'date_end': '2024-02-05T18:00:00',
    }

    response = client.post('/tournament', json=payload)
    tournament_id = response.json().get('id', '')
    competitor_payload = {
        'names': ['Competitor1', 'Competitor2'],
    }
    response = client.post(
        f'/tournament/{tournament_id}/competitor', json=competitor_payload
    )

    response = client.get(f'/tournament/{tournament_id}/match')

    assert response.status_code == 201


def test_get_match_list_with_two_competitors1(client, session):

    payload = {
        'name': 'Torneio de Exemplo',
        'date_start': '2024-01-29T12:00:00',
        'date_end': '2024-02-05T18:00:00',
    }

    response = client.post('/tournament', json=payload)
    tournament_id = response.json().get('id', '')
    competitor_payload = {
        'names': ['Competitor1', 'Competitor2'],
    }
    response = client.post(
        f'/tournament/{tournament_id}/competitor', json=competitor_payload
    )

    response = client.get(f'/tournament/{tournament_id}/match')

    assert response.status_code == 201


def test_create_tournament_and_register_odd_number_of_comp_get_match_list(
    client, session
):
    tournament_payload = {
        'name': 'Torneio de Exemplo',
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
        ],
    }
    competitors_response = client.post(
        f'/tournament/{tournament_id}/competitor', json=competitors_payload
    )

    assert competitors_response.status_code == 201


def test_create_tournament_and_register_odd_number_of_comp_get_match_list1(
    client, session
):
    tournament_payload = {
        'name': 'Torneio de Exemplo',
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
        ],
    }
    competitors_response = client.post(
        f'/tournament/{tournament_id}/competitor', json=competitors_payload
    )

    assert competitors_response.status_code == 201


def test_create_match_with_odd_number_of_competitors(client, session):

    tournament_payload = {
        'name': 'Torneio de Exemplo',
        'date_start': '2024-01-29T12:00:00',
        'date_end': '2024-02-05T18:00:00',
    }
    tournament_response = client.post('/tournament', json=tournament_payload)
    tournament_id = tournament_response.json().get('id', '')

    assert tournament_response.status_code == 201

    competitors_payload = {
        'names': ['Competitor1', 'Competitor2', 'Competidor3'],
    }
    competitors_response = client.post(
        f'/tournament/{tournament_id}/competitor', json=competitors_payload
    )

    assert competitors_response.status_code == 201

    Match.create_match(tournament_id, session)

    matches_response = client.get(f'/tournament/{tournament_id}/match')

    assert matches_response.status_code == 201
