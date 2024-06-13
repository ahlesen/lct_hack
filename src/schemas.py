"""Схемы данных для вставки в индекс нового видео и ответа на запрос пользователя.

Этот модуль содержит схемы данных, используемые для валидации и структурирования данных
при взаимодействии с API для вставки нового видео в индекс и поиска видео по запросу.
"""

from typing import List

from pydantic import BaseModel, HttpUrl

# Схемы для вставки в индекс нового видео


class VideoInsertInput(BaseModel):
    """Входные данные для вставки нового видео в индекс.

    :param video_link: Ссылка на видео.
    :type video_link: HttpUrl
    :param description: Описание видео (опционально).
    :type description: str, optional
    """

    video_link: HttpUrl
    description: None | str = ''


class VideoInsertOutput(BaseModel):
    """Выходные данные после вставки видео в индекс.

    :param caption: Подпись к видео.
    :type caption: str
    :param transcription: Транскрипция аудио из видео.
    :type transcription: str
    :param shazam_title: Название песни, найденной в видео.
    :type shazam_title: str
    :param shazam_subtitle: Автор песни, найденной в видео.
    :type shazam_subtitle: str
    :param shazam_url: Ссылка на песню.
    :type shazam_url: str
    """

    caption: str
    transcription: str
    shazam_title: str
    shazam_subtitle: str
    shazam_url: str


# Схемы для ответа на запрос пользователя
class VideoSearchInput(BaseModel):
    """Входные данные для поиска видео по запросу.

    :param query: Текстовый запрос для поиска видео.
    :type query: str
    """

    query: str


class VideoSearchResult(BaseModel):
    """Результат поиска одного видео.

    :param video_link: Ссылка на найденное видео.
    :type video_link: HttpUrl
    :param description: Описание найденного видео.
    :type description: str
    """

    video_link: HttpUrl
    description: str


class VideoSearchOutput(BaseModel):
    """Выходные данные с результатами поиска видео.

    :param results: Список найденных видео.
    :type results: List[VideoSearchResult]
    """

    results: List[VideoSearchResult]
