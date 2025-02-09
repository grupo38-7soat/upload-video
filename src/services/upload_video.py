import fnmatch
import os
import shutil
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from fastapi import APIRouter
from fastapi.responses import UJSONResponse

from model.upload_video import UploadVideoInput, UploadVideoOutput
from src.settings import AWS_REGION, AWS_SECRET_KEY, AWS_ACCESS_KEY, AWS_S3_BUCKET_NAME
from src.utils.exceptions import handle_default_error_exception, handle_not_found_exception, \
    handle_unauthorized_exception

upload_video_router = APIRouter()


@upload_video_router.post('/uploadvideo', response_model=UploadVideoOutput)
async def upload_video_to_s3(input: UploadVideoInput):

    s3_client = boto3.client(
        service_name='s3',
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY
    )

    filename = input.video_name

    try:
        list_files(input.path, filename)
        tmp_file = f'./tmp/{filename}'

        s3_client.upload_file(tmp_file, AWS_S3_BUCKET_NAME, filename)

        bucket_uri = parse_bucket_uri_from_s3(filename)

        os.remove(tmp_file)
        return UploadVideoOutput(**{'bucket_url': bucket_uri})

    except FileNotFoundError:
        handle_not_found_exception('Arquivo não encontrado.')
    except NoCredentialsError:
        handle_unauthorized_exception('Credenciais inválidas.')
    except PartialCredentialsError:
        handle_unauthorized_exception('As crendenciais da AWS estão incompletas.')
    except Exception as e:
        handle_default_error_exception(f'Erro no upload: {e}')


def list_files(path, filename):
    matching_files = search_files_by_path(path, filename)

    if not matching_files:
        handle_not_found_exception('Arquivo não encontrado.')

    if not os.path.exists('./tmp'):
        os.makedirs('./tmp')

    shutil.copy(matching_files[0], './tmp')


def search_files_by_path(root_dir, pattern):
    matching_files = []

    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in fnmatch.filter(filenames, pattern):
            matching_files.append(os.path.join(dirpath, filename))
            break

    return matching_files


def parse_bucket_uri_from_s3(filename):
    parsed_url = str(f's3://{AWS_S3_BUCKET_NAME}/{filename}')
    return parsed_url









