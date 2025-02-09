from typing import Dict, Any
from pydantic import BaseModel


class UploadVideoInput(BaseModel):
    user: str
    video_name: str
    object_name: str = None


class UploadVideoOutput(BaseModel):
    video: str
    bucket_name: str
