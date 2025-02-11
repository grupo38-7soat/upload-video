from unittest.mock import patch
import jwt
from src.services.auth import JWTService
from src.talkers.talkers import Talker

t = JWTService()


def test_decode_jwt_valid_token():
    # Simulando um token JWT válido
    token = jwt.encode({"id": "user123"}, "secret", algorithm="HS256")
    user_id = t.decode_jwt(token)

    assert user_id == "user123"


@patch("src.talkers.talkers")
async def test_retrieve_user_success(mock_get):
    # Mockando a resposta da API de usuários
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"id": "user123", "name": "John Doe"}

    t = Talker()

    user = await t.retrieve_user("user123")

    assert user == {"id": "user123", "name": "John Doe"}


@patch("src.talkers.talkers")
async def test_retrieve_user_failure(mock_get):
    # Mockando falha na requisição
    mock_get.return_value.status_code = 500
    mock_get.return_value.text = "Erro interno"

    t = Talker()

    user = await t.retrieve_user("user123")

    assert user == {"Erro": "Erro interno"}