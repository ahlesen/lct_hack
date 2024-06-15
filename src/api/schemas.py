"""Схемы данных для вставки в индекс нового видео и ответа на запрос пользователя.

Этот модуль содержит схемы данных, используемые для валидации и структурирования данных
при взаимодействии с API для вставки нового видео в индекс и поиска видео по запросу.
"""

from typing import Union

from pydantic import BaseModel, Field, HttpUrl

# Схемы для вставки в индекс нового видео


class Video(BaseModel):
    """Схема данных для вставки нового видео в индекс и в качестве результата поиска видео."""

    link: Union[HttpUrl, str] = Field(
        ...,
        example="https://cdn-st.rutubelist.ru/media/f4/8d/0766c7c04bb1abb8bf57a83fa4e8/fhd.mp4",
    )
    description: str = Field(
        ..., example="#технологии #девайсы #technologies #гаджеты #смартчасы #умныечасы #миф"
    )


class Text(BaseModel):
    """Схема данных для поиска видео по текстовому запросу."""

    text: str = Field(..., example="технологии")
