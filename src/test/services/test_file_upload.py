import os
import pytest
import datetime
import json
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app import app  # Importe o FastAPI app corretamente

client = TestClient(app)  # Cliente para testar a API


# Mock do boto3 para evitar chamadas reais ao AWS S3 e SQS
@pytest.fixture
def mock_boto3():
    with patch("boto3.client") as mock:
        yield mock

# Teste: Falha no upload (exceção no S3)
def test_upload_s3_failure(mock_boto3, tmpdir):
    mock_s3 = MagicMock()
    mock_sqs = MagicMock()
    mock_boto3.side_effect = lambda service_name, **kwargs: mock_s3 if service_name == "s3" else mock_sqs

    mock_s3.upload_file.side_effect = Exception("Erro no upload do S3")

    file_path = tmpdir.join("test_video.mp4")
    file_path.write("conteúdo fictício do vídeo")

    with open(file_path, "rb") as file:
        response = client.post(
            "/upload",
            files={"file": ("test_video.mp4", file, "video/mp4")},
            data={
                "user": "johndoe",
                "start_time_for_cut_frames": "10",
                "end_time_for_cut_frames": "30",
                "skip_frame": "5"
            }
        )

    assert response.status_code == 400


# Teste: Falha ao enviar mensagem para SQS
def test_upload_sqs_failure(mock_boto3, tmpdir):
    mock_s3 = MagicMock()
    mock_sqs = MagicMock()
    mock_boto3.side_effect = lambda service_name, **kwargs: mock_s3 if service_name == "s3" else mock_sqs

    mock_sqs.send_message.side_effect = Exception("Erro ao enviar mensagem para SQS")

    file_path = tmpdir.join("test_video.mp4")
    file_path.write("conteúdo fictício do vídeo")

    with open(file_path, "rb") as file:
        response = client.post(
            "/upload",
            files={"file": ("test_video.mp4", file, "video/mp4")},
            data={
                "user": "johndoe",
                "start_time_for_cut_frames": "10",
                "end_time_for_cut_frames": "30",
                "skip_frame": "5"
            }
        )

    assert response.status_code == 400
