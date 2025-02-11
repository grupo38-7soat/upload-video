import datetime
import json
import os

import boto3
from fastapi import File, UploadFile, APIRouter, Form, Header
from fastapi.responses import JSONResponse
from constants.settings import AWS_REGION, AWS_S3_BUCKET_NAME

from utils.exceptions import handle_default_error_exception
from utils.delete_folder import delete_folder

from src.services.auth import JWTService
from src.talkers.talkers import Talker

file_upload_router = APIRouter()

s3_client = boto3.client(
    service_name='s3',
    region_name=AWS_REGION,
    aws_access_key_id=os.getenv('ACCESS_KEY'),
    aws_secret_access_key=os.getenv('SECRET_KEY')
)

sqs = boto3.client(
    service_name='sqs',
    region_name=AWS_REGION,
    aws_access_key_id=os.getenv('ACCESS_KEY'),
    aws_secret_access_key=os.getenv('SECRET_KEY')
)


@file_upload_router.post("/upload")
async def upload_file(
    token_jwt: str = Header(),
    file: UploadFile = File(...),
    start_time_for_cut_frames: int = Form(...),
    end_time_for_cut_frames: int = Form(...),
    skip_frame: int = Form(...)
):
    # Decode do JWT
    token = JWTService()
    user_id = token.decode_jwt(token_jwt)

    if not user_id:
        handle_default_error_exception('Erro ao obter os dados do usuário.')

    # Chama a API de consulta de usuário
    talker = Talker()
    find_user = await talker.retrieve_user(user_id)

    if not find_user:
        handle_default_error_exception('Usário não encontrado!')

    file_location = f"./uploaded_files/{file.filename}"
    os.makedirs(os.path.dirname(file_location), exist_ok=True)

    try:
        # Salvar o arquivo temporariamente
        with open(file_location, "wb") as f:
            content = await file.read()
            f.write(content)

        # Upload para S3 (sem await)
        upload_to_s3(file_location, file.filename)

        # Enviar mensagem para SQS (sem await)
        message_id = send_message_to_sqs(user_id, file.filename, start_time_for_cut_frames, end_time_for_cut_frames, skip_frame)

        # Responder antes de apagar o arquivo
        return JSONResponse(content={
            "message": f"Vídeo {file.filename} importado com sucesso. MessageId: {message_id}",
            "status_code": 200
        })

    except Exception as e:
        print(f"Erro no upload do arquivo {file.filename}. Mensagem: {e}")
        handle_default_error_exception(f"Erro no upload do arquivo {file.filename}. Mensagem: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

    finally:
        # Só apaga a pasta se o upload foi bem-sucedido
        if os.path.exists(file_location):
            delete_folder(['uploaded_files'])


# Funções não precisam ser assíncronas porque boto3 é síncrono
def upload_to_s3(file_location: str, filename: str):
    s3_client.upload_file(file_location, AWS_S3_BUCKET_NAME, f'uploads/{filename}')


def send_message_to_sqs(user: str, filename: str, start_time_for_cut_frames: int, end_time_for_cut_frames: int, skip_frame: int):
    dt = datetime.datetime.now()
    message = {
        "user_id": user,
        "video_name": filename,
        "start_time_for_cut_frames": start_time_for_cut_frames,
        "end_time_for_cut_frames": end_time_for_cut_frames,
        "skip_frame": skip_frame,
        "start_time": dt.strftime("%Y-%m-%d %H:%M:%S")
    }
    message_body = json.dumps(message)
    response = sqs.send_message(
        QueueUrl=os.getenv('QUEUE_URL'),
        MessageBody=message_body
    )
    return response.get('MessageId')
