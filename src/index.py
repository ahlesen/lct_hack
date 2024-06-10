import os
from typing import Dict
from loguru import logger
from src.elastic.elastic_api import ElasticIndex


def index_one_document(input: Dict[str, str]):
    index = ElasticIndex(index_name=os.environ.get("INDEX_NAME"), 
                            elastic_host_port=os.environ.get("ELASTIC_PORT"),
                            elastic_password=os.environ.get("ELASTIC_PASSWORD"),
                            elastic_ca_certs_path="./src/elastic/certs/http_ca.crt",)
    
    
    video_path = input["link"]
    description = input["description"]

    # отправляю метод, где реализовано
    # 1. Скачивание входного видео и его обработка
    # 1.1. Отправка видео для: video_caption -->  --> video_hastags минус
    # 1.2. Отправка видео для: whisper --> llama --> audio_hastags минус
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

    document = {
        "embedding": embedding,
        "description": clean_description,
        "song_name": clean_song_name,
        "song_author": clean_song_author,
        "video_hastags": video_hastags,
        "audio_hastags": audio_hastags,
    }

    index.index_one_document(document)


def index_jsonl_documents(path_to_jsonl: str,
                          elastic_ca_certs_path: str):
    index = ElasticIndex(index_name=os.environ.get("INDEX_NAME"), 
                         elastic_host_port=os.environ.get("ELASTIC_PORT"),
                         elastic_password=os.environ.get("ELASTIC_PASSWORD"),
                         elastic_ca_certs_path=elastic_ca_certs_path,)
    
    if not index.index_is_alive():
        raise Exception("Index is not alive.")

    if not os.path.isfile(path_to_jsonl):
        raise(f"File is not exist: {path_to_jsonl}")
    
    index.bulk_documents(path_to_documents=path_to_jsonl)
    index.count_documents_in_index()


def create_index(elastic_ca_certs_path: str, path_to_index_json: str):
    index = ElasticIndex(index_name=os.environ.get("INDEX_NAME"), 
                            elastic_host_port=os.environ.get("ELASTIC_PORT"),
                            elastic_password=os.environ.get("ELASTIC_PASSWORD"),
                            elastic_ca_certs_path=elastic_ca_certs_path,)
    
    if not index.index_is_alive():
        index.create_index(path_to_index_json=path_to_index_json)
    else:
        logger.info("Index is already exists.")


if __name__ == "__main__":
    index_jsonl_documents(path_to_jsonl="../data/documents.jsonl")