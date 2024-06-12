from typing import Any
from src.engine.utils import _basic_text_preprocessing

def search_documents(user_query: str, elastic_client: Any):
    preprocessed_query = _basic_text_preprocessing(user_query)

    body = {
                "_source": False,
                "from": 0,
                "query": {
                  "function_score": {
                    "query": {
                      "bool": {
                        "must": {
                          "dis_max": {
                            "queries": [
                              {
                                "bool": {
                                  "must": {
                                    "multi_match": {
                                      "fields": [
                                        "text_hashtags^1.0"
                                      ],
                                      "operator": "AND",
                                      "query": preprocessed_query,
                                      "type": "most_fields"
                                    }
                                  }
                                }
                              }
                            ]
                          }
                        }
                      }
                    }
                  }
                },
                "size": 10,
                "timeout": "500ms"
              }
    try:
        response = elastic_client.local_client.search(index=elastic_client.index_name, body=body)['hits']['hits']
        document_ids = [doc['_id'] for doc in response]
        document_scores = [doc['_score'] for doc in response]
        res = {'ids':document_ids, 'scores':document_scores}
    except Exception as e:
        # more smart exception can be here
        raise e

    return res
