# import os
# import pytest
# import datetime
# import json
# from unittest.mock import patch, MagicMock
# from fastapi.testclient import TestClient
# from app import app  # Importe o FastAPI app corretamente
#
# client = TestClient(app)  # Cliente para testar a API
#
#
# # Mock do boto3 para evitar chamadas reais ao AWS S3 e SQS
# @pytest.fixture
# def mock_boto3():
#     with patch("boto3.client") as mock:
#         yield mock
#
# # Teste: Falha no upload (exceção no S3)
# def test_upload_s3_failure(mock_boto3, tmpdir):
#     mock_s3 = MagicMock()
#     mock_sqs = MagicMock()
#     mock_boto3.side_effect = lambda service_name, **kwargs: mock_s3 if service_name == "s3" else mock_sqs
#
#     mock_s3.upload_file.side_effect = Exception("Erro no upload do S3")
#
#     file_path = tmpdir.join("test_video.mp4")
#     file_path.write("conteúdo fictício do vídeo")
#
#     with open(file_path, "rb") as file:
#         response = client.post(
#             "/upload",
#             files={"file": ("test_video.mp4", file, "video/mp4")},
#             data={
#                 "user": "johndoe",
#                 "start_time_for_cut_frames": "10",
#                 "end_time_for_cut_frames": "30",
#                 "skip_frame": "5"
#             }
#         )
#
#     assert response.status_code == 400
#
#
# # Teste: Falha ao enviar mensagem para SQS
# def test_upload_sqs_failure(mock_boto3, tmpdir):
#     mock_s3 = MagicMock()
#     mock_sqs = MagicMock()
#     mock_boto3.side_effect = lambda service_name, **kwargs: mock_s3 if service_name == "s3" else mock_sqs
#
#     mock_sqs.send_message.side_effect = Exception("Erro ao enviar mensagem para SQS")
#
#     file_path = tmpdir.join("test_video.mp4")
#     file_path.write("conteúdo fictício do vídeo")
#
#     with open(file_path, "rb") as file:
#         response = client.post(
#             "/upload",
#             files={"file": ("test_video.mp4", file, "video/mp4")},
#             data={
#                 "user": "johndoe",
#                 "start_time_for_cut_frames": "10",
#                 "end_time_for_cut_frames": "30",
#                 "skip_frame": "5"
#             }
#         )
#
#     assert response.status_code == 400


import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from src.services.file_upload import file_upload_router

# Criando um cliente de teste
client = TestClient(file_upload_router)


# Teste para o endpoint de upload
@pytest.fixture
def mock_jwt_service():
    with patch('src.services.file_upload.JWTService') as MockJWTService:
        yield MockJWTService


@pytest.fixture
def mock_talker():
    with patch('src.services.file_upload.Talker') as MockTalker:
        yield MockTalker


@pytest.fixture
def mock_s3_client():
    with patch('src.services.file_upload.s3_client') as MockS3Client:
        yield MockS3Client


@pytest.fixture
def mock_sqs():
    with patch('src.services.file_upload.sqs') as MockSQS:
        yield MockSQS


def test_upload_file_success(mock_jwt_service, mock_talker, mock_s3_client, mock_sqs):
    # Mock do JWTService
    mock_jwt_service().decode_jwt.return_value = "user_id"

    # Mock do Talker retornando usuário válido
    mock_talker().retrieve_user.return_value = {"id": "user_id"}

    # Mock do S3 (upload bem-sucedido)
    mock_s3_client.upload_file.return_value = None

    # Mock do SQS (mensagem enviada com sucesso)
    mock_sqs.send_message.return_value = {"MessageId": "12345"}

    # Simulando o envio de um arquivo
    with patch('src.services.file_upload.UploadFile') as mock_file:
        mock_file.filename = "video.mp4"
        mock_file.read.return_value = b"fake content"

        response = client.post("/upload",
                               headers={"token_jwt": "fake-jwt-token"},
                               files={"file": ("video.mp4", mock_file.read())},
                               data={"start_time_for_cut_frames": 0, "end_time_for_cut_frames": 10, "skip_frame": 2},
                               )

        # Verificando se a resposta foi bem-sucedida
        assert response.status_code == 200
        assert "Vídeo video.mp4 importado com sucesso." in response.json().get("message")
        assert "MessageId" in response.json()


def test_upload_file_user_not_found(mock_jwt_service, mock_talker, mock_s3_client, mock_sqs):
    # Mock do JWTService
    mock_jwt_service().decode_jwt.return_value = "user_id"

    # Mock do Talker retornando usuário não encontrado
    mock_talker().retrieve_user.return_value = None

    # Enviando requisição sem arquivo, mas com os dados necessários
    response = client.post("/upload",
                           data={"start_time_for_cut_frames": 0, "end_time_for_cut_frames": 10, "skip_frame": 2},
                           headers={"token_jwt": "fake-jwt-token"})

    # Verificando se o erro foi tratado corretamente
    assert response.status_code == 400
    assert "Usário não encontrado!" in response.json().get("detail")


def test_upload_file_error_s3(mock_jwt_service, mock_talker, mock_s3_client, mock_sqs):
    # Mock do JWTService
    mock_jwt_service().decode_jwt.return_value = "user_id"

    # Mock do Talker retornando usuário válido
    mock_talker().retrieve_user.return_value = {"id": "user_id"}

    # Simulando erro ao tentar fazer upload para o S3
    mock_s3_client.upload_file.side_effect = Exception("Erro ao fazer upload para o S3")

    response = client.post("/upload",
                           data={"start_time_for_cut_frames": 0, "end_time_for_cut_frames": 10, "skip_frame": 2},
                           headers={"token_jwt": "fake-jwt-token"})

    # Verificando se o erro foi tratado corretamente
    assert response.status_code == 500
    assert "Erro no upload do arquivo" in response.json().get("error")


def test_upload_file_error_sqs(mock_jwt_service, mock_talker, mock_s3_client, mock_sqs):
    # Mock do JWTService
    mock_jwt_service().decode_jwt.return_value = "user_id"

    # Mock do Talker retornando usuário válido
    mock_talker().retrieve_user.return_value = {"id": "user_id"}

    # Mock do S3 (upload bem-sucedido)
    mock_s3_client.upload_file.return_value = None

    # Simulando erro ao tentar enviar mensagem para o SQS
    mock_sqs.send_message.side_effect = Exception("Erro ao enviar mensagem para o SQS")

    response = client.post("/upload",
                           data={"start_time_for_cut_frames": 0, "end_time_for_cut_frames": 10, "skip_frame": 2},
                           headers={"token_jwt": "fake-jwt-token"})

    # Verificando se o erro foi tratado corretamente
    assert response.status_code == 500
    assert "Erro no upload do arquivo" in response.json().get("error")
