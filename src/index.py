import os
from typing import Dict, Any
from loguru import logger


def index_one_document(input: Dict[str, str],
                       elastic_client,) -> None:
    
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

    elastic_client.index_one_document(document)


def index_documents_jsonl(path_to_jsonl: str, elastic_client) -> None:
    if not elastic_client.index_is_alive():
        raise Exception("Index is not alive.")

    if not os.path.isfile(path_to_jsonl):
        raise(f"File is not exist: {path_to_jsonl}")
    
    elastic_client.bulk_documents(path_to_documents=path_to_jsonl)
    elastic_client.count_documents_in_index()


def create_index(path_to_index_json: str, elastic_client) -> None:
    if not elastic_client.index_is_alive():
        elastic_client.create_index(path_to_index_json=path_to_index_json)
    else:
        logger.info("Index is already exists.")
