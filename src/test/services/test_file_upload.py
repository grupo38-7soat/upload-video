import pytest
from unittest import mock
from fastapi.testclient import TestClient
from src.app import upload_video_router
from src.model.upload_video import UploadVideoInput, UploadVideoOutput
from src.utils.exceptions import handle_default_error_exception, handle_not_found_exception


# Mockando as dependências
@pytest.fixture
def mock_s3_client():
    with mock.patch('boto3.client') as mock_s3:
        yield mock_s3.return_value


@pytest.fixture
def mock_shutil_copy():
    with mock.patch('shutil.copy') as mock_copy:
        yield mock_copy


@pytest.fixture
def mock_os_remove():
    with mock.patch('os.remove') as mock_remove:
        yield mock_remove


@pytest.fixture
def mock_list_files():
    with mock.patch('src.services.upload_video.list_files') as mock_list:
        yield mock_list


@pytest.fixture
def client():
    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(upload_video_router)
    return TestClient(app)


def test_upload_video_to_s3_success(
        client, mock_s3_client, mock_shutil_copy, mock_os_remove, mock_list_files
):
    # Mockando a resposta de upload
    mock_s3_client.upload_file = mock.MagicMock()

    # Mockando o comportamento de listagem de arquivos
    mock_list_files.return_value = ['./tmp/mock_video.mp4']

    # Simulando a entrada de vídeo
    video_input = UploadVideoInput(user="user123", video_name="mock_video.mp4", path="./tmp/mock_video.mp4")

    # Chamada para o endpoint
    response = client.post("/uploadvideo", json=video_input.dict())

    assert response.status_code == 200
    assert response.json() == {'bucket_url': 's3://your_bucket/user123-mock_video.mp4'}

    # Verificando se a função de upload do S3 foi chamada
    mock_s3_client.upload_file.assert_called_once_with('./tmp/mock_video.mp4', 'your_bucket', 'user123-mock_video.mp4')

    # Verificando se o arquivo temporário foi removido após o upload
    mock_os_remove.assert_called_once_with('./tmp/mock_video.mp4')


def test_upload_video_missing_user(client):
    # Testando falta do campo 'user'
    video_input = UploadVideoInput(user='', video_name="mock_video.mp4", path="./videos")

    response = client.post("/uploadvideo", json=video_input.dict())

    assert response.status_code == 400  # Espera erro de validação
    assert "Campo user é obrigatório!" in response.text


def test_upload_video_file_not_found(
        client, mock_shutil_copy, mock_list_files, mock_s3_client
):
    # Simulando erro de arquivo não encontrado
    mock_list_files.return_value = []

    video_input = UploadVideoInput(user="user123", video_name="mock_video.mp4", path="./teste/tmp/mock_video.mp4")

    response = client.post("/uploadvideo", json=video_input.dict())

    assert response.status_code == 400  # Espera erro 400 para arquivo não encontrado
    assert "Erro no upload do arquivo mock_video.mp4." in response.text


def test_upload_video_handle_exception(client, mock_s3_client, mock_shutil_copy, mock_list_files):
    # Simulando uma exceção no upload
    mock_s3_client.upload_file = mock.MagicMock(side_effect=Exception("Erro inesperado"))

    mock_list_files.return_value = ['./test/tmp/mock_video.mp4']

    video_input = UploadVideoInput(user="user123", video_name="mock_video.mp4", path="./videos")

    response = client.post("/uploadvideo", json=video_input.dict())

    assert response.status_code == 400  # Espera erro 500 (erro no upload)
    assert "Erro no upload do arquivo mock_video.mp4" in response.text
