import os
from typing import Dict
from loguru import logger
from elastic.elastic_api import ElasticIndex


def index_one_document(input: Dict[str, str]):
    index = ElasticIndex(index_name=os.environ.get("INDEX_NAME"), 
                         elastic_password=os.environ.get("ELASTIC_PASSWORD"),
                         elastic_ca_certs_path="./elastic/certs/http_ca.crt",)
    
    video_path = input["link"]
    description = input["description"]

    # отправляю метод, где реализовано
    # 1. Скачивание входного видео и его обработка
    # 1.1. Отправка видео для: video_caption --> llama --> video_hastags
    # 1.2. Отправка видео для: whisper --> llama --> audio_hastags
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


def index_jsonl_documents(path_to_jsonl: str):
    index = ElasticIndex(index_name=os.environ.get("INDEX_NAME"), 
                            elastic_password=os.environ.get("ELASTIC_PASSWORD"),
                            elastic_ca_certs_path="./elastic/certs/http_ca.crt",)
    
    if not os.path.isfile(path_to_jsonl):
        raise(f"File is not exist: {path_to_jsonl}")
    
    index.bulk_documents(path_to_documents=path_to_jsonl)
    index.count_documents_in_index()