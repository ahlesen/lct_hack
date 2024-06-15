"""Модуль для взаимодействия с ElasticSearch.

Этот модуль содержит класс ElasticIndex, который предоставляет методы для создания индекса,
индексирования документов и выполнения других операций с индексами ElasticSearch.
"""

import json
from typing import Any, Dict

import jsonlines
from elasticsearch import Elasticsearch
from elasticsearch.helpers import streaming_bulk
from src.base_logger import logger
from tqdm import tqdm


class ElasticIndex:
    """Класс для взаимодействия с индексами ElasticSearch.

    Этот класс предоставляет методы для создания индекса, удаления индекса,
    проверки состояния индекса,индексирования отдельных документов и
    пакетного индексирования документов.
    """

    def __init__(
        self,
        index_name: str,
        elastic_host_port: str,
        elastic_password: str,
        elastic_ca_certs_path: str,
    ):
        """Инициализация клиента ElasticSearch.

        :param index_name: Имя индекса.
        :type index_name: str
        :param elastic_host_port: Порт для подключения к ElasticSearch.
        :type elastic_host_port: str
        :param elastic_password: Пароль для подключения к ElasticSearch.
        :type elastic_password: str
        :param elastic_ca_certs_path: Путь к сертификатам CA.
        :type elastic_ca_certs_path: str
        """
        self.index_name = index_name
        self.local_client = Elasticsearch(
            hosts=f"https://localhost:{elastic_host_port}",
            retry_on_timeout=True,
            timeout=10000,
            ca_certs=elastic_ca_certs_path,
            basic_auth=("elastic", elastic_password),
        )

    def create_index(self, path_to_index_json: str):
        """Создать индекс в ElasticSearch.

        :param path_to_index_json: Путь к файлу JSON с настройками и маппингом индекса.
        :type path_to_index_json: str
        """
        index_json = self._get_index_json(path_to_index_json)

        # self.delete_index()
        self.local_client.indices.create(
            index=self.index_name,
            settings=index_json["settings"],
            mappings=index_json["mappings"],
            request_timeout=5000,
        )
        if self.index_is_alive():
            logger.info(f"Index with name '{self.index_name}' is created.")
        else:
            raise Exception("Index is not created.")

    @staticmethod
    def _get_index_json(path_to_index_json: str) -> dict:
        """Загрузить настройки и маппинг индекса из JSON файла.

        :param path_to_index_json: Путь к файлу JSON с настройками и маппингом индекса.
        :type path_to_index_json: str
        :return: Словарь с настройками и маппингом индекса.
        :rtype: dict
        """
        with open(path_to_index_json, "r") as f:
            index = json.load(f)
        return index

    def _count_documents_in_jsonl(self, path_to_documents: str):
        """Подсчитать количество документов в JSONL файле.

        :param path_to_documents: Путь к JSONL файлу с документами.
        :type path_to_documents: str
        :return: Количество документов в JSONL файле.
        :rtype: int
        """
        with jsonlines.open(path_to_documents) as reader:
            count = 0
            for _ in reader:
                count += 1
        return count

    def count_documents_in_index(self):
        """Подсчитать количество документов в индексе."""
        self.local_client.indices.refresh(index=self.index_name)
        response = self.local_client.cat.count(index=self.index_name, params={"format": "json"})
        logger.info(f"Count of documents: {response[0]['count']}")

    def delete_index(self):
        """Удалить индекс из ElasticSearch.

        Если индекс существует, он будет удален.
        """
        if self.index_is_alive():
            self.local_client.indices.delete(index=self.index_name)

    def index_is_alive(self):
        """Проверить, существует ли индекс в ElasticSearch.

        :return: True, если индекс существует, иначе False.
        :rtype: bool
        """
        return self.local_client.indices.exists(index=self.index_name)

    def index_one_document(self, document: Dict[str, Any]):
        """Индексировать один документ в ElasticSearch.

        :param document: Документ для индексирования.
        :type document: dict
        """
        document_id = document["_id"]
        del document["_id"]
        self.local_client.index(index=self.index_name, document=document, id=document_id)

    def _generate_documents(self, path_to_documents: str):
        """Генератор документов из JSONL файла.

        :param path_to_documents: Путь к JSONL файлу с документами.
        :type path_to_documents: str
        :yield: Документ из JSONL файла с добавленным _id.
        :rtype: dict
        """
        with jsonlines.open(path_to_documents) as reader:
            for _, document in enumerate(reader):
                yield document

    def index_batch_documents(self, path_to_documents: str):
        """Индексировать документы из JSONL файла в пакетном режиме.

        :param path_to_documents: Путь к JSONL файлу с документами.
        :type path_to_documents: str
        """
        count = self._count_documents_in_jsonl(path_to_documents)
        progress = tqdm(unit="docs", total=count)
        for document in self._generate_documents(path_to_documents=path_to_documents):
            self.index_one_document(document=document)
            progress.update(1)
        self.local_client.indices.refresh()

    def bulk_documents(self, path_to_documents: str):
        """Индексировать документы из JSONL файла в режиме bulk.

        :param path_to_documents: Путь к JSONL файлу с документами.
        :type path_to_documents: str
        :raises Exception: Если индекс не существует.
        """
        if not self.index_is_alive():
            raise Exception(
                (
                    "Index doesn't exist. Create one: api.create_index(index_name: str, "
                    "path_to_index_json: str).)"
                )
            )

        count = self._count_documents_in_jsonl(path_to_documents)
        logger.info(f"Indexing documents... Overall documents: {count}")
        progress = tqdm(unit="docs", total=count)
        successes = 0
        for ok, document in streaming_bulk(
            client=self.local_client,
            index=self.index_name,
            actions=self._generate_documents(path_to_documents=path_to_documents),
            max_retries=5,
            chunk_size=500,  # 500, 1000
            refresh=True,
            raise_on_error=True,
            raise_on_exception=True,
            request_timeout=10000,
        ):
            progress.update(1)
            successes += ok
        logger.info("Indexed %d/%d documents" % (successes, count))
        self.local_client.indices.refresh()
