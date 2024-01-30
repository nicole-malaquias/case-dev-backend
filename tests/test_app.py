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
    assert response.json() == {
        'id': 1,
        'name': 'Torneio de Exemplo',
        'date_start': '2024-01-29T12:00:00',
        'date_end': '2024-02-05T18:00:00',
    }


def test_create_tournament_failure():
    client = TestClient(app)
    payload = {
        'name': 'Torneio de Exemplo',
        'date_start': '2024-02-05T18:00:00',
        'date_end': '2024-01-29T12:00:00',
    }
    response = client.post('/tournament', json=payload)

    assert response.status_code == 422
