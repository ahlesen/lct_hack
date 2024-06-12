from pydantic import BaseModel, HttpUrl
from typing import List

# Схемы для вставки в индекс нового видео

class VideoInsertInput(BaseModel):
    video_link : HttpUrl
    description:None | str = ''

class VideoInsertOutput(BaseModel):
    caption : str
    transcription : str
    shazam_title : str
    shazam_subtitle : str
    shazam_url : str

# Схемы для ответа на запрос пользователя
class VideoSearchInput(BaseModel):
    query: str

class VideoSearchResult(BaseModel):
    video_link: HttpUrl
    description: str


class VideoSearchOutput(BaseModel):
    results: List[VideoSearchResult]