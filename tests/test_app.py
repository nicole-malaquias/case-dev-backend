from fastapi.testclient import TestClient

from app.app import app


def test_create_tournament_success():
    client = TestClient(app)
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


def test_create_tournament_failure():
    client = TestClient(app)
    payload = {
        'name': 'Torneio de Exemplo',
        'date_start': '2024-02-05T18:00:00',
        'date_end': '2024-01-29T12:00:00',
    }
    response = client.post('/tournament', json=payload)

    assert response.status_code == 422


def test_register_competitors_success():
    client = TestClient(app)
    tournament_payload = {
        'name': 'Torneio de Exemplo',
        'date_start': '2024-01-29T12:00:00',
        'date_end': '2024-02-05T18:00:00',
    }
    tournament_response = client.post('/tournament', json=tournament_payload)
    tournament_id = tournament_response.json().get('id', '')
    competitor_payload = {
        'names': ['Competidor Exemplo'],
    }

    response = client.post(
        f'/tournament/{int(tournament_id)}/competitor', json=competitor_payload
    )

    assert response.status_code == 201
    assert response.json() is None


def test_register_competitors_failure():
    client = TestClient(app)
    tournament_payload = {
        'name': 'Torneio de Exemplo',
        'date_start': '2024-01-29T12:00:00',
        'date_end': '2023-02-05T18:00:00',
    }
    tournament_response = client.post('/tournament', json=tournament_payload)
    tournament_id = tournament_response.json().get('id', '')

    competitor_payload = {
        'names': ['Competidor Exemplo'],
    }

    response = client.post(
        f'/tournament/{tournament_id}/competitor', json=competitor_payload
    )
    print(response.json())
    assert response.status_code == 404
