import datetime
import json

import boto3
from fastapi import File, UploadFile, APIRouter
from fastapi.responses import JSONResponse
import os

from src.settings import AWS_REGION, AWS_S3_BUCKET_NAME, QUEUE_URL
from src.utils.exceptions import handle_default_error_exception

file_upload_router = APIRouter()

s3_client = boto3.client(
    service_name='s3',
    region_name=AWS_REGION,
    aws_access_key_id='AKIA3CMCCVYVNOZBNY5X',
    aws_secret_access_key='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'
)

sqs = boto3.client(
    service_name='sqs',
    region_name=AWS_REGION,
    aws_access_key_id='AKIA3CMCCVYVNOZBNY5X',
    aws_secret_access_key='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'
)


@file_upload_router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_location = f"./uploaded_files/{file.filename}"

    os.makedirs(os.path.dirname(file_location), exist_ok=True)

    with open(file_location, "wb") as f:
        f.write(await file.read())

        try:
            s3_client.upload_file(file_location, AWS_S3_BUCKET_NAME, file.filename)

            dt = datetime.datetime.now()

            message = {
                "user": "user",
                "video_name": file.filename,
                "start_time": dt.strftime("%Y-%m-%d %H:%M:%S")
            }

            message_body = json.dumps(message)

            # Envia a mensagem para a fila SQS
            response = sqs.send_message(
                QueueUrl=QUEUE_URL,
                MessageBody=message_body  # Send the JSON string as the message body
            )

            return JSONResponse(content={"message": f"Vídeo {file.filename} importado com sucesso. MessageId: {response.get('MessageId')}, status_code=200)"})

        except Exception as e:
            handle_default_error_exception(f"Erro no upload do arquivo {file.filename}. Mensagem: {e}")
