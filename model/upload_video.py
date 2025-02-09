from pydantic import BaseModel


class UploadVideoInput(BaseModel):
    user: str
    video_name: str
    path: str


class UploadVideoOutput(BaseModel):
    bucket_url: str
