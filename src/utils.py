"""Вспомогательные методы для обработки данных.

Этот модуль содержит функции для создания JSONL документов из
данных Pandas DataFrame или Parquet файлов.
В частонсти метод по формирования docuemnts.json на 40к примерах (25к)
"""

import os
import uuid
from typing import Optional

import jsonlines
import pandas as pd

from src.elastic.elastic_api import ElasticIndex
from src.index import create_index, index_jsonl


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

    with jsonlines.open(path_to_save, mode="a") as writer:
        for _, row in data.iterrows():
            sample = {}
            sample["doc_id"] = row["index orig"]
            sample["embedding"] = row["embedding"]
            sample["text_hashtags"] = row["text_hashtags"]
            sample["video_hashtags"] = row["video_hashtags"]
            sample["audio_transcription"] = row["audio_transcription"]
            sample["audio_hashtags"] = row["audio_hashtags"]
            sample["song_name"] = row["song_name"]
            sample["song_author"] = row["song_author"]
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

    set_of_suggest_candidates = set(
        list(data["text_hashtags"] + data["song_author"] + data["song_name"])
    )
    final_suggests = set()
    for sentence in set_of_suggest_candidates:
        candidates = {token for token in sentence.split(" ") if len(token) > 3}
        final_suggests.update(candidates)

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
