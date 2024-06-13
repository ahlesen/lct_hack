"""Модуль для выполнения запросов к ElasticSearch.

Этот модуль содержит функции для поиска документов в ElasticSearch
на основе пользовательского запроса.
"""

from typing import Any

from src.engine.utils import (
    embedding_text_processing_query,
    fts_text_processing_query,
)


def search_documents(user_query: str, elastic_client: Any):
    """Выполнить поиск документов в ElasticSearch.

    :param user_query: Пользовательский запрос для поиска.
    :type user_query: str
    :param elastic_client: Клиент для взаимодействия с ElasticSearch.
    :type elastic_client: Any
    :return: Словарь с идентификаторами документов и их оценками релевантности.
    :rtype: dict
    """
    preprocessed_query = fts_text_processing_query(user_query)
    query_embedding = embedding_text_processing_query(user_query)[0]

    body = {
        "_source": False,
        "from": 0,
        "size": 10,
        "timeout": "500ms",
        "query": {
            "bool": {
                "should": [
                    {
                        "multi_match": {
                            "fields": [
                                "full_text^3",
                                "full_text.morph^3",
                                "full_text.synonyms^3",
                            ],
                            "operator": "AND",
                            "query": preprocessed_query,
                            "type": "most_fields",
                        }
                    },
                    {
                        "multi_match": {
                            "fields": [
                                "audio_hashtags^0.1",
                                "audio_transcription^0.1",
                                "text_hashtags^0.1",
                                "audio_hashtags.morph^0.1",
                                "audio_hashtags.synonyms^0.1",
                                "text_hashtags.morph^0.1",
                                "text_hashtags.synonyms^0.1",
                                "song_name^0.1",
                                "song_author^0.1",
                                "video_hashtags^0.1",
                            ],
                            "operator": "OR",
                            "query": preprocessed_query,
                            "type": "most_fields",
                        }
                    },
                    {
                        "script_score": {
                            "query": {"match_all": {}},
                            "script": {
                                "source": """
                        double score = cosineSimilarity(params.query_vector, 'embedding');
                        return score > 0.8 ? score*100 : 0;
                    """,
                                "params": {
                                    "query_vector": query_embedding,
                                },
                            },
                        }
                    },
                ],
                "minimum_should_match": 1,
            }
        },
    }
    try:
        response = elastic_client.local_client.search(index=elastic_client.index_name, body=body)[
            'hits'
        ]['hits']
        document_ids = [doc['_id'] for doc in response]
        document_scores = [doc['_score'] for doc in response]
        res = {'ids': document_ids, 'scores': document_scores}
    except Exception as e:
        # more smart exception can be here
        raise e

    return res
