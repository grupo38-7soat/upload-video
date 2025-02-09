from fastapi import FastAPI
from src import __version__

from src.services.upload_video import upload_video_to_s3, upload_video_router
from src.settings import AWS_S3_BUCKET_NAME, BASE_PATH

app = FastAPI(
    title="Upload de Vídeos",
    version=__version__,
    description="Serviço Upload de Vídeos",
    docs_url=f"{BASE_PATH}/docs",
    redoc_url=f"{BASE_PATH}/redocs",
    openapi_url=f"{BASE_PATH}/openapi.json"
)

app.include_router(upload_video_router, prefix=BASE_PATH)

if __name__ == '__main__':
    upload_video_to_s3('src/images/girafa.jpeg', '123', AWS_S3_BUCKET_NAME)
