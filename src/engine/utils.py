"""Вспомогательный функционал."""

from __future__ import annotations

import os
import re
from typing import Any, Dict, Optional

import requests
from moviepy.editor import VideoFileClip
from pydub import AudioSegment

english_stopwords = [
    "i",
    "me",
    "my",
    "myself",
    "we",
    "our",
    "ours",
    "ourselves",
    "you",
    "your",
    "yours",
    "yourself",
    "yourselves",
    "he",
    "him",
    "his",
    "himself",
    "she",
    "her",
    "hers",
    "herself",
    "it",
    "its",
    "itself",
    "they",
    "them",
    "their",
    "theirs",
    "themselves",
    "what",
    "which",
    "who",
    "whom",
    "this",
    "that",
    "these",
    "those",
    "am",
    "is",
    "are",
    "was",
    "were",
    "be",
    "been",
    "being",
    "have",
    "has",
    "had",
    "having",
    "do",
    "does",
    "did",
    "doing",
    "a",
    "an",
    "the",
    "and",
    "but",
    "if",
    "or",
    "because",
    "as",
    "until",
    "while",
    "of",
    "at",
    "by",
    "for",
    "with",
    "about",
    "against",
    "between",
    "into",
    "through",
    "during",
    "before",
    "after",
    "above",
    "below",
    "to",
    "from",
    "up",
    "down",
    "in",
    "out",
    "on",
    "off",
    "over",
    "under",
    "again",
    "further",
    "then",
    "once",
    "here",
    "there",
    "when",
    "where",
    "why",
    "how",
    "all",
    "any",
    "both",
    "each",
    "few",
    "more",
    "most",
    "other",
    "some",
    "such",
    "no",
    "nor",
    "not",
    "only",
    "own",
    "same",
    "so",
    "than",
    "too",
    "very",
    "s",
    "t",
    "can",
    "will",
    "just",
    "don",
    "should",
    "now",
]


def download_video(
    url: str, output_path: str, max_retries: int = 5, timeout: int = 60
) -> Optional[requests.models.Response]:
    """Скачать видео с указанного URL с заданным количеством повторных попыток.

    :param url: URL для скачивания видео.
    :param output_path: Путь для сохранения скачанного видео.
    :param max_retries: Максимальное количество повторных попыток при ошибках скачивания.
    :param timeout: Таймаут для запроса.
    :return: Ответ запроса или None в случае ошибки.
    """
    retries = 0
    while retries < max_retries:
        try:
            response = requests.get(url, stream=True, timeout=timeout)
            if response.status_code == 200:
                with open(output_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                return response
            else:
                retries += 1
                print(
                    f"--Failed to download {url}, status code: {response.status_code}| "
                    + f"retries = {retries}"
                )
        except (
            requests.exceptions.RequestException,
            requests.exceptions.ChunkedEncodingError,
        ) as e:
            print(f"Error downloading {url}, attempt {retries + 1} of {max_retries}: {e}")
            retries += 1
            if retries == max_retries:
                print(
                    f"!!Final Fail of downloading {url} after {max_retries} attempts| "
                    + f"retries = {retries}"
                )
    return None


def extract_audio_with_check(video_path: str, output_dir: str) -> Optional[str]:
    """Извлечь аудио из видео файла с проверкой на наличие аудио.

    :param video_path: Путь к видео файлу.
    :param output_dir: Директория для сохранения извлеченного аудио.
    :return: Путь к сохраненному аудио файлу.
    """
    try:
        video_clip = VideoFileClip(video_path)
        audio_file_path = os.path.join(
            output_dir, os.path.basename(video_path).replace(".mp4", ".mp3")
        )
        if video_clip.audio is None:
            print(f"No audio found in {video_path}. Creating empty audio file.")
            silent_audio = AudioSegment.silent(duration=1000)
            silent_audio.export(audio_file_path, format="mp3")
        else:
            video_clip.audio.write_audiofile(audio_file_path, verbose=False, logger=None)
        return audio_file_path
    except Exception as e:
        print(f"Failed to extract audio from {video_path}: {e}")
        return None


def embedding_text_processing_passage(
    morph: Any,
    raw_description: str,
    raw_song_name: Optional[str] = None,
    raw_song_author: Optional[str] = None,
    raw_audio_transcription: Optional[str] = None,
    raw_video_hashtags: Optional[str] = None,
) -> str:
    """Обработать текст для эмбеддинга.

    :param morph: Класс морфологии.
    :param raw_description: Описание текста.
    :param raw_song_name: Название песни.
    :param raw_song_author: Автор песни.
    :param raw_audio_transcription: Транскрипция аудио.
    :param raw_video_hashtags: Хэштеги видео.
    :return: Обработанный текст для эмбеддинга.
    """
    result_text_field = "passage: " + _basic_text_preprocessing(raw_description)
    if raw_song_name is not None:
        clean_song_name = _basic_text_preprocessing(raw_song_name)
        result_text_field = result_text_field + " " + clean_song_name
    if raw_song_author is not None:
        clean_song_author = _basic_text_preprocessing(raw_song_author)
        result_text_field = result_text_field + " " + clean_song_author
    if raw_audio_transcription is not None:
        clean_audio_hashtags = _advanced_text_preprocessing(raw_audio_transcription, morph)
        result_text_field = result_text_field + " " + clean_audio_hashtags
    if raw_video_hashtags is not None:
        clean_video_hashtags = _basic_text_from_image_preprocessing(raw_video_hashtags)
        result_text_field = result_text_field + " " + clean_video_hashtags

    return result_text_field


def embedding_text_processing_query(user_query: str):
    """Перевести текст в запрос.

    :param user_query: Пользовательский запрос.
    :return: Текст с запросом.
    """
    return "query: " + _basic_text_preprocessing(user_query)


def fts_text_processing_passage(
    morph: Any,
    raw_description: str,
    raw_song_name: str,
    raw_song_author: str,
    raw_song_name_transliterated: str,
    raw_song_author_transliterated: str,
    raw_audio_transcription: Optional[str] = None,
    raw_video_hashtags: Optional[str] = None,
) -> Dict[str, str]:
    """Обработать текст для FTS.

    :param morph: Класс морфологии.
    :param raw_description: Описание текста.
    :param raw_song_name: Название песни.
    :param raw_song_author: Автор песни.
    :param raw_song_name_transliterated: Название песни - транслитерация.
    :param raw_song_author_transliterated: Автор песни - транслитерация.
    :param raw_audio_transcription: Транскрипция аудио.
    :param raw_video_hashtags: Хэштеги видео.
    :return: Обработанный список текстов для FTS.
    """
    clean_description = _basic_text_preprocessing(raw_description)
    clean_song_name = _basic_text_preprocessing(raw_song_name)
    clean_song_author = _basic_text_preprocessing(raw_song_author)
    clean_song_name_transliterated = _basic_text_preprocessing(raw_song_name_transliterated)
    clean_song_author_transliterated = _basic_text_preprocessing(raw_song_author_transliterated)
    full_text = (
        clean_description
        + " "
        + clean_song_name
        + " "
        + clean_song_author
        + " "
        + clean_song_name_transliterated
        + " "
        + clean_song_author_transliterated
    )
    if raw_audio_transcription is not None:
        clean_audio_hashtags = _advanced_text_preprocessing(raw_audio_transcription, morph)
        clean_audio_transcription = _basic_text_preprocessing(raw_audio_transcription)
        full_text = full_text + " " + clean_audio_transcription
    if raw_video_hashtags is not None:
        clean_video_hashtags = _basic_text_from_image_preprocessing(raw_video_hashtags)
        full_text = full_text + " " + clean_video_hashtags

    return {
        "full_text": full_text,
        "clean_description": clean_description,
        "clean_song_name": clean_song_name,
        "clean_song_author": clean_song_author,
        "clean_song_name_transliterated": clean_song_name_transliterated,
        "clean_song_author_transliterated": clean_song_author_transliterated,
        "clean_audio_transcription": clean_audio_transcription,
        "clean_audio_hashtags": clean_audio_hashtags,
        "clean_video_hashtags": clean_video_hashtags,
    }


def fts_text_processing_query(user_query: str):
    """Перевести текст в запрос.

    :param user_query: Пользовательский запрос.
    :return: Текст с запросом.
    """
    return _basic_text_preprocessing(user_query)


def _basic_text_preprocessing(text: str) -> str:
    text = text.lower()
    text = text.replace('ё', 'е')
    text = re.sub('[^a-zA-Zа-яА-Я0-9,.# ]+', '', text)
    text = re.sub('[,.#]', ' ', text)
    return ' '.join(text.split())


def _basic_text_from_image_preprocessing(text: str) -> str:
    text = text.lower()
    text = re.sub('[^a-z0-9,. ]+', ' ', text)
    text = re.sub('[,.]', ' ', text)
    return ' '.join([word for word in set(text.split()) if word not in english_stopwords])


def _advanced_text_preprocessing(text: str, morph: Any) -> str:
    text = text.lower()
    text = text.replace('ё', 'е')
    text = re.sub('[^а-я0-9,. ]+', ' ', text)
    text = re.sub('[,.]', ' ', text)
    processed_text: str = morph.str_get_tags_morph_custom(text)
    return processed_text
