# Здесь запрос в эластик
from typing import Any


def search_documents(user_query: str, elastic_client: Any):
    preprocessed_query = ...(user_query)

    body = {...}
    try:
        response = elastic_client.local_client.search(index=elastic_client.index_name, body=body)
    except Exception as e:
        # more smart exception can be here
        raise e

    return response
