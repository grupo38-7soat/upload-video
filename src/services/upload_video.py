import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from fastapi import APIRouter

from src.settings import AWS_REGION, AWS_SECRET_KEY, AWS_S3_BUCKET_NAME, AWS_ACCESS_KEY
from src.utils.exceptions import handle_default_error_exception, handle_not_found_exception, \
    handle_unauthorized_exception

upload_video_router = APIRouter()


@upload_video_router.post('/uploadvideo')
def upload_video_to_s3(filename, document, bucket_name, object_name=None):

    s3_client = boto3.client(
        service_name='s3',
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY
    )

    if object_name is None:
        object_name = filename

    try:
        s3_client.upload_file(filename, bucket_name, object_name)
        print(f"Upload realizado com sucesso! {bucket_name}/{object_name}")
    except FileNotFoundError:
        handle_not_found_exception('Arquivo não encontrado.')
    except NoCredentialsError:
        handle_unauthorized_exception('Credenciais inválidas.')
    except PartialCredentialsError:
        handle_unauthorized_exception('As crendenciais da AWS estão incompletas.')
    except Exception as e:
        handle_default_error_exception(f'Erro no upload: {e}')





