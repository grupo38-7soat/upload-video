import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from fastapi import APIRouter
from fastapi.responses import UJSONResponse

from model.upload_video import UploadVideoInput, UploadVideoOutput
from src.settings import AWS_REGION, AWS_SECRET_KEY, AWS_ACCESS_KEY, AWS_S3_BUCKET_NAME
from src.utils.exceptions import handle_default_error_exception, handle_not_found_exception, \
    handle_unauthorized_exception

upload_video_router = APIRouter()


@upload_video_router.post('/uploadvideo', response_class=UJSONResponse)
async def upload_video_to_s3(input: UploadVideoInput):

    s3_client = boto3.client(
        service_name='s3',
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY
    )

    if input.object_name is None:
        input.object_name = input.video_name

    try:
        s3_client.upload_file(input.video_name, AWS_S3_BUCKET_NAME, input.object_name)
        return UploadVideoOutput(**{'video_name': input.video_name, 'bucket_name': AWS_S3_BUCKET_NAME})

    except FileNotFoundError:
        handle_not_found_exception('Arquivo não encontrado.')
    except NoCredentialsError:
        handle_unauthorized_exception('Credenciais inválidas.')
    except PartialCredentialsError:
        handle_unauthorized_exception('As crendenciais da AWS estão incompletas.')
    except Exception as e:
        handle_default_error_exception(f'Erro no upload: {e}')





