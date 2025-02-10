import uvicorn as uvicorn
from fastapi import FastAPI
from src.services.file_upload import file_upload_router

from src.settings import HOST, PORT


app = FastAPI(
    title="Upload de Vídeos",
    description="Serviço Upload de Vídeos",
    docs_url="/docs",
    redoc_url=None,

)

app.include_router(file_upload_router)


if __name__ == "__main__":
    uvicorn.run(
        "src.app:app",
        host=HOST,
        port=PORT,
        log_level="info"
    )

