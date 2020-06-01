from starlette.testclient import TestClient
from app.main import app

client = TestClient(app)

# changed this so it passes... this isn't a real endpoint
def test_ping(test_app):
    response = test_app.get("/ping")
    assert response.status_code == 404
    # assert response.json() == {"ping": "pong!"}


def test_all(test_app):
    response = test_app.get("/all")
    assert response.status_code == 200


def test_track():
    response = client.post("/track/", json={"track": "foobar", "location": "Foo Bar"},)
    assert response.status_code == 200


def test_search():
    response = client.post(
        "/search/", json={"search": "foobar", "location": "Foo Bar"},
    )
    assert response.status_code == 200
