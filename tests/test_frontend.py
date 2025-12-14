import pytest
from unittest.mock import patch
from frontend.app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_index(client):
    r = client.get("/")
    assert r.status_code == 200


@patch("frontend.app.requests.get")
def test_search_person(mock_get, client):
    mock_get.return_value.json.return_value = [
        {"nconst": "nm0001", "primary_name": "Test Actor"}
    ]

    r = client.get("/search?q=test&mode=person")
    assert r.status_code == 200


@patch("frontend.app.requests.get")
def test_person_detail(mock_get, client):
    mock_get.return_value.json.return_value = {
        "nconst": "nm0001",
        "primary_name": "Test Actor",
        "birth_year": 1980,
        "death_year": None,
        "primary_profession": "actor,director",
        "known_for_titles": "tt0001,tt0002"
    }

    r = client.get("/person/nm0001")
    assert r.status_code == 200

@patch("frontend.app.requests.get")
def test_title_detail(mock_get, client):
    mock_get.return_value.json.return_value = {
        "tconst": "tt0001",
        "primary_title": "Test Movie",
        "original_title": "Test Movie",
        "title_type": "movie",
        "start_year": 2020,
        "end_year": None,
        "runtime_minutes": 120,
        "genres": "Drama,Action",
        "average_rating": 8.2,
        "num_votes": 12345
    }

    r = client.get("/title/tt0001")
    assert r.status_code == 200
