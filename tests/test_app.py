from http import HTTPStatus
from fastapi.testclient import TestClient
from app import app


def test_read_root_dedve_retornar_OK_ola_mundo():
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"message": "Ola, Mundo"}
