"""Схемы данных для вставки в индекс нового видео и ответа на запрос пользователя.

Этот модуль содержит схемы данных, используемые для валидации и структурирования данных
при взаимодействии с API для вставки нового видео в индекс и поиска видео по запросу.
"""

from typing import List, Union

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


# class VideoInsertOutput(BaseModel):
#     """Выходные данные после вставки видео в индекс.

#     :param caption: Подпись к видео.
#     :type caption: str
#     :param transcription: Транскрипция аудио из видео.
#     :type transcription: str
#     :param shazam_title: Название песни, найденной в видео.
#     :type shazam_title: str
#     :param shazam_subtitle: Автор песни, найденной в видео.
#     :type shazam_subtitle: str
#     :param shazam_url: Ссылка на песню.
#     :type shazam_url: str
#     """

#     caption: str
#     transcription: str
#     shazam_title: str
#     shazam_subtitle: str
#     shazam_url: str


class Text(BaseModel):
    """Схема данных для поиска видео по текстовому запросу."""

    text: str = Field(..., example="технологии")
