"""Вспомогательные методы для обработки данных.

Этот модуль содержит функции для создания JSONL документов из
данных Pandas DataFrame или Parquet файлов.
В частонсти метод по формирования docuemnts.json на 40к примерах (25к)
"""

import os
import uuid
from typing import Any, Dict, Optional

import jsonlines
import pandas as pd

from src.elastic.elastic_api import ElasticIndex
from src.engine.utils import (
    embedding_text_processing_passage,
    fts_text_processing_passage,
)
from src.index import create_index, index_jsonl


async def process_all_documents_from_csv(
    input_data_path: str,
    output_data_path: str,
    video_processor: Any,
    embedding_model: Any,
    morph_model: Any,
) -> None:
    """Функция для обогащения исходного csv файла и создания Паркет файла.

    :param input_data_path: Путь до csv файла с полями link и description.
    :param output_data_path: Путь до pq файла с готовыми полями для индексации.
    :param video_processor: Модель для обработки видео.
    :param embedding_model: Модель для генерации эмбеддингов.
    :param morph_model: Модель для морфологического анализа текста.
    """
    data = pd.read_csv(input_data_path)[["link", "description"]]
    data.fillna("", inplace=True)
    all_documents = []
    for row in data.iterrows():
        raw_description = row[1]["description"]
        video_url = row[1]["link"]

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
        all_documents.append(document)
    processed_data = pd.DataFrame(all_documents)
    processed_data.to_parquet(output_data_path)


def create_documents_jsonl(
    data: Optional[pd.DataFrame] = None,
    path_to_pq: Optional[str] = None,
    path_to_save: str = "../data/documents.jsonl",
):
    """Создать JSONL документы из DataFrame или Parquet файла.

    :param data: DataFrame с данными. Если не указан, будет использован path_to_pq.
    :type data: Optional[pd.DataFrame]
    :param path_to_pq: Путь к Parquet файлу с данными. Если не указан, будет использован data.
    :type path_to_pq: Optional[str]
    :param path_to_save: Путь для сохранения JSONL документов.
    :type path_to_save: str
    :raises Exception: Если не указаны ни data, ни path_to_pq.
    """
    if data is None and path_to_pq is None:
        raise Exception
    if data is None:
        data = pd.read_parquet(path_to_pq)

    if os.path.isfile(path_to_save):
        os.remove(path_to_save)

    with jsonlines.open(path_to_save, mode="a") as writer:
        for _, row in data.iterrows():
            sample = {}
            sample["_id"] = row["video_url"]
            sample["video_url"] = row["video_url"]
            sample["full_text"] = row["full_text"]
            sample["embedding"] = row["embedding"]
            sample["text_hashtags"] = row["text_hashtags"]
            sample["video_hashtags"] = row["video_hashtags"]
            sample["audio_transcription"] = row["audio_transcription"]
            sample["audio_hashtags"] = row["audio_hashtags"]
            sample["song_name"] = row["song_name"]
            sample["song_author"] = row["song_author"]
            sample["song_name_transliterated"] = row["song_name_transliterated"]
            sample["song_author_transliterated"] = row["song_author_transliterated"]
            writer.write(sample)


def create_suggests_jsonl(
    data: Optional[pd.DataFrame] = None,
    path_to_pq: Optional[str] = None,
    path_to_save: str = "../data/suggests.jsonl",
):
    """Создать JSONL документы из DataFrame или Parquet файла. Для пословных подсказок.

    :param data: DataFrame с данными. Если не указан, будет использован path_to_pq.
    :type data: Optional[pd.DataFrame]
    :param path_to_pq: Путь к Parquet файлу с данными. Если не указан, будет использован data.
    :type path_to_pq: Optional[str]
    :param path_to_save: Путь для сохранения JSONL документов.
    :type path_to_save: str
    :raises Exception: Если не указаны ни data, ни path_to_pq.
    """
    if data is None and path_to_pq is None:
        raise Exception
    if data is None:
        data = pd.read_parquet(path_to_pq)

    sdelay = (
        data["song_author"] + data["song_name"] + data["song_author_transliterated"]
    )  # TODO: СДЕЛАЙ!!!!

    set_of_suggest_candidates = set(list(data["text_hashtags"] + ...))
    final_suggests = set()
    for sentence in set_of_suggest_candidates:
        candidates = {token for token in sentence.split(" ") if len(token) > 3}
        final_suggests.update(candidates)

    if os.path.isfile(path_to_save):
        os.remove(path_to_save)

    with jsonlines.open(path_to_save, mode="a") as writer:
        for suggest in final_suggests:
            writer.write({"_id": uuid.uuid4().hex, "suggest": suggest})


def entrypoint():
    elastic_client = ElasticIndex(
        index_name=os.environ.get("INDEX_NAME"),
        elastic_host_port=os.environ.get(
            "ELASTIC_PORT"
        ),  # Убедись что используешь правильный порт
        elastic_password=os.environ.get("ELATIC_PASSWORD"),
        elastic_ca_certs_path="./src/elastic/certs/http_ca.crt",
    )

    suggest_elastic_client = ElasticIndex(
        index_name=os.environ.get("SUGGEST_INDEX_NAME"),
        elastic_host_port=os.environ.get(
            "ELASTIC_PORT"
        ),  # Убедись что используешь правильный порт
        elastic_password=os.environ.get("ELATIC_PASSWORD"),
        elastic_ca_certs_path="./src/elastic/certs/suggest_http_ca.crt",
    )

    elastic_client.delete_index()
    suggest_elastic_client.delete_index()

    create_index(
        path_to_index_json="./src/elastic/settings/index.json", elastic_client=elastic_client
    )
    create_index(
        path_to_index_json="./src/elastic/settings/suggest_index.json",
        elastic_client=suggest_elastic_client,
    )

    index_jsonl(path_to_jsonl="./data/documents.jsonl", elastic_client=elastic_client)
    index_jsonl(path_to_jsonl="./data/suggests.jsonl", elastic_client=suggest_elastic_client)
