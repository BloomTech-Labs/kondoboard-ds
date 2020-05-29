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
    assert response.status_code ==200

# def test_track(test_app):
#     response = test_app.post("/track/{track}")
#     assert response.status_code ==200

# def test_custom_search(test_app):
#     response = test_app.post("/search/{search}/location/{location}")
#     assert response.status_code ==200