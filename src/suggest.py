"""Модуль для выполнения запросов к ElasticSearch.

Этот модуль содержит функции для поиска саджестов в ElasticSearch
на основе пользовательского запроса.
"""

from typing import Any
from src.index import create_index, index_jsonl


def search_suggests(user_query: str, elastic_client: Any):
    """Выполнить поиск саджестов в ElasticSearch.

    :param user_query: Пользовательский запрос для подбора саджестов.
    :type user_query: str
    :param elastic_client: Клиент для взаимодействия с ElasticSearch.
    :type elastic_client: Any
    :return: Словарь с одним полем саджестов.
    :rtype: dict
    """
    body = {
        ...
    }
    try:
        response = elastic_client.local_client.search(index=elastic_client.index_name, body=body)[
            'hits'
        ]['hits']
        completions = [doc['completion'] for doc in response]
        res = {"suggests": completions}
    except Exception as e:
        # more smart exception can be here
        raise e

    return res


if __name__ == "__main__":
    import os
    from elastic.elastic_api import ElasticIndex

    suggest_elastic_client = ElasticIndex(
        index_name="suggest",
        elastic_host_port="8201",  # Убедись что используешь правильный порт
        elastic_password="bqv9w9KGzu7VyVTtV1Ho",
        elastic_ca_certs_path="./src/elastic/certs/suggest_http_ca.crt",
    )

    create_index(path_to_index_json="./src/elastic/settings/suggest_index.json", 
                 elastic_client=suggest_elastic_client)
    
    index_jsonl(path_to_jsonl="./data/suggests.jsonl", 
                elastic_client=suggest_elastic_client)
    
