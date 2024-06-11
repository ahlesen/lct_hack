import json
from typing import Any, Dict

import jsonlines
from elasticsearch import Elasticsearch
from loguru import logger
from tqdm import tqdm


class ElasticIndex:
    def __init__(
        self,
        index_name: str,
        elastic_host_port: str,
        elastic_password: str,
        elastic_ca_certs_path: str,
    ):
        self.index_name = index_name
        self.local_client = Elasticsearch(
            hosts=f"https://localhost:{elastic_host_port}",
            retry_on_timeout=True,
            timeout=10000,
            ca_certs=elastic_ca_certs_path,
            basic_auth=("elastic", elastic_password),
        )

    def create_index(self, path_to_index_json: str):
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

    @staticmethod
    def _get_index_json(path_to_index_json: str) -> dict:
        with open(path_to_index_json, "r") as f:
            index = json.load(f)
        return index

    def _count_documents_in_jsonl(self, path_to_documents: str):
        with jsonlines.open(path_to_documents) as reader:
            count = 0
            for _ in reader:
                count += 1
        return count

    def count_documents_in_index(self):
        self.local_client.indices.refresh(index=self.index_name)
        response = self.local_client.cat.count(index=self.index_name, params={"format": "json"})
        logger.info(f"Count of documents: {response[0]['count']}")

    def delete_index(self):
        if self.index_is_alive():
            self.local_client.indices.delete(index=self.index_name)

    def index_is_alive(self):
        return self.local_client.indices.exists(index=self.index_name)

    def index_one_document(self, document: Dict[str, Any]):
        self.local_client.index(
            index=self.index_name,
            document=document,
        )

    def _generate_documents(self, path_to_documents: str):
        with jsonlines.open(path_to_documents) as reader:
            for i, document in enumerate(reader):
                yield document

    def bulk_documents(self, path_to_documents: str):
        # if not self.index_is_alive():
        #     raise Exception(
        #         "Index doesn't exist. Create one: api.create_index(index_name: str, path_to_index_json: str).)")

        # count = self._count_documents_in_jsonl(path_to_documents)
        # logger.info(f"Indexing documents... Overall documents: {count}")
        # progress = tqdm(unit="docs", total=count)
        # successes = 0
        # for ok, document in streaming_bulk(client=self.local_client,
        #                                    index=self.index_name,
        #                                    actions=self._generate_documents(path_to_documents=path_to_documents),
        #                                    max_retries=5,
        #                                    chunk_size=500,  # 500, 1000
        #                                    refresh=True,
        #                                    raise_on_error=True,
        #                                    raise_on_exception=True,
        #                                    request_timeout=10000):
        #     progress.update(1)
        #     successes += ok
        # logger.info("Indexed %d/%d documents" % (successes, count))
        # self.local_client.indices.refresh()
        count = self._count_documents_in_jsonl(path_to_documents)
        progress = tqdm(unit="docs", total=count)
        for document in self._generate_documents(path_to_documents=path_to_documents):
            self.index_one_document(document=document)
            progress.update(1)
        self.local_client.indices.refresh()
