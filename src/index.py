"""Индексация elastic."""

import os
from typing import Any, Dict

import torch
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
    # отправляю метод, где реализовано
    # 1. Скачивание входного видео и его обработка
    # 1.1. Отправка видео для: video_caption -->  --> video_hashtags минус
    # 1.2. Отправка видео для: whisper --> llama --> audio_hashtags минус
    # 1.3. Отправка видео для: shazam --> [song_name, song_author]

    # отправка текстовых данных для предобработки, чтобы положить в поля эластика
    # 2. Препроцессинг текстовых данных
    # 2.1. description --> clean_description
    # 2.2. song_name --> clean_song_name
    # 2.3. song_author --> clean_song_author
    # ...

    # конкатенация текстовых полей для формирования эмбеддинга
    # 3. Конкат текста и прогон через E5_base
    # 3.1. [description + song_name + song_author + ...] --> embedding
    # пока сделал так, чтобы была совместимость по api & ipynb
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


if __name__ == "__main__":
    from elastic.elastic_api import ElasticIndex
    from engine.config import ConfigVideoProcessor
    from engine.embedding import Embedding
    from engine.model import VideoProcessor
    from engine.morph import Morph

    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    config = ConfigVideoProcessor()

    video_processor = VideoProcessor(config=config, device=device)
    embedding_model = Embedding(device=device)
    morph_model = Morph()

    elastic_client = ElasticIndex(
        index_name=os.environ.get("INDEX_NAME"),
        elastic_host_port="8201",  # Убедись что используешь правильный порт
        elastic_password="bqv9w9KGzu7VyVTtV1Ho",
        elastic_ca_certs_path="./src/elastic/certs/http_ca.crt",
    )

    input = {
        "link": (
            "https://cdn-st.rutubelist.ru/media/87/43/b11df3f344d0af773aac81e410ee/fhd.mp4"
        ),  # noqa: E501
        "description": "",
    }

    index_one_document(
        input=input,
        elastic_client=elastic_client,
        video_processor=video_processor,
        embedding_model=embedding_model,
        morph_model=morph_model,
    )
