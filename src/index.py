"""Индексация elastic."""

import os
from typing import Any, Dict

from loguru import logger

from src.engine.utils import (
    embedding_text_processing_passage,
    fts_text_processing_passage,
)


async def index_one_document(
    input: Dict[str, str],
    elastic_client: Any,
    video_processor: Any,
    embedding_model: Any,
    morph_model: Any,
) -> None:
    """Индексировать один документ в ElasticSearch.

    :param input: Входные данные, содержащие ссылку на видео и описание.
    :param elastic_client: Клиент для взаимодействия с ElasticSearch.
    :param video_processor: Модель для обработки видео.
    :param embedding_model: Модель для генерации эмбеддингов.
    :param morph_model: Модель для морфологического анализа текста.
    :return: Словарь с проиндексированным документом.
    """
    try:
        video_url = input["link"]
        raw_description = input["description"]
    except Exception as exp:  # noqa: F841
        video_url = input.video_link
        raw_description = input.description

    result_dict: Dict[str, str] = await video_processor.process_video_from_link(
        video_url=video_url
    )

    raw_video_hashtags = result_dict["captions"]
    raw_audio_transcription = result_dict["transcription"]
    raw_song_name = result_dict["shazam_title"]
    raw_song_author = result_dict["shazam_subtitle"]
    raw_song_name_transliterated = result_dict["shazam_title_transliterated"]
    raw_song_author_transliterated = result_dict["shazam_subtitle_transliterated"]

    text_to_embedd: str = embedding_text_processing_passage(
        morph=morph_model,
        raw_description=raw_description,
        raw_audio_transcription=raw_audio_transcription,
        raw_video_hashtags=raw_video_hashtags,
    )

    text_to_fts: Dict[str, str] = fts_text_processing_passage(
        morph=morph_model,
        raw_description=raw_description,
        raw_song_name=raw_song_name,
        raw_song_author=raw_song_author,
        raw_song_name_transliterated=raw_song_name_transliterated,
        raw_song_author_transliterated=raw_song_author_transliterated,
        raw_audio_transcription=raw_audio_transcription,
        raw_video_hashtags=raw_video_hashtags,
    )

    embedding = embedding_model(texts=[text_to_embedd])[0]

    document = {
        "_id": video_url,
        "video_url": video_url,
        "embedding": embedding,
        "full_text": text_to_fts["full_text"],
        "text_hashtags": text_to_fts["clean_description"],
        "song_name": text_to_fts["clean_song_name"],
        "song_author": text_to_fts["clean_song_author"],
        "song_name_transliterated": text_to_fts["clean_song_name_transliterated"],
        "song_author_transliterated": text_to_fts["clean_song_author_transliterated"],
        "video_hashtags": text_to_fts["clean_video_hashtags"],
        "audio_hashtags": text_to_fts["clean_audio_hashtags"],
        "audio_transcription": text_to_fts["clean_audio_transcription"],
    }

    print(f"document2elastic:{document}")

    elastic_client.index_one_document(document)
    return document


def index_jsonl(path_to_jsonl: str, elastic_client: Any) -> None:
    """Индексировать документы из JSONL файла в ElasticSearch.

    :param path_to_jsonl: Путь к файлу в формате JSONL, содержащему документы.
    :param elastic_client: Клиент для взаимодействия с ElasticSearch.
    """
    if not elastic_client.index_is_alive():
        raise Exception("Index is not alive.")

    if not os.path.isfile(path_to_jsonl):
        raise (f"File is not exist: {path_to_jsonl}")

    elastic_client.bulk_documents(path_to_documents=path_to_jsonl)
    elastic_client.count_documents_in_index()


def create_index(path_to_index_json: str, elastic_client: Any) -> None:
    """Создать индекс в ElasticSearch.

    :param path_to_index_json: Путь к файлу JSON, содержащему описание индекса.
    :param elastic_client: Клиент для взаимодействия с ElasticSearch.
    """
    if not elastic_client.index_is_alive():
        elastic_client.create_index(path_to_index_json=path_to_index_json)
    else:
        logger.info("Index is already exists.")
