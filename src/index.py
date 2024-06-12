import os
from typing import Any, Dict

import torch
from loguru import logger

from src.engine.utils import (
    embedding_text_processing_passage,
    fts_text_processing_passage,
)


def index_one_document(
    input: Dict[str, str],
    elastic_client: Any,
    video_processor: Any,
    embedding_model: Any,
    morph_model: Any,
) -> None:
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

    video_url = input["link"]
    raw_description = input["description"]

    result_dict: Dict[str, str] = video_processor.process_video_from_link(video_url=video_url)

    raw_video_hastags = result_dict["captions"]
    raw_audio_transcription = result_dict["transcription"]
    raw_song_name = result_dict["shazam_title"]
    raw_song_author = result_dict["shazam_subtitle"]

    text_to_embedd: str = embedding_text_processing_passage(
        morph=morph_model,
        raw_description=raw_description,
        raw_song_name=raw_song_name,
        raw_song_author=raw_song_author,
        raw_audio_transcription=raw_audio_transcription,
        raw_video_hashtags=raw_video_hastags,
    )

    text_to_fts: Dict[str, str] = fts_text_processing_passage(
        morph=morph_model,
        raw_description=raw_description,
        raw_song_name=raw_song_name,
        raw_song_author=raw_song_author,
        raw_audio_transcription=raw_audio_transcription,
        raw_video_hashtags=raw_video_hastags,
    )

    embedding = embedding_model(texts=[text_to_embedd])[0]

    document = {
        "video_url": video_url,
        "embedding": embedding,
        "text_hashtags": text_to_fts["clean_description"],
        "song_name": text_to_fts["clean_song_name"],
        "song_author": text_to_fts["clean_song_author"],
        "video_hastags": text_to_fts["clean_video_hashtags"],
        "audio_hastags": text_to_fts["clean_audio_transcription"],
    }

    # print(document)

    elastic_client.index_one_document(document)


def index_documents_jsonl(path_to_jsonl: str, elastic_client: Any) -> None:
    if not elastic_client.index_is_alive():
        raise Exception("Index is not alive.")

    if not os.path.isfile(path_to_jsonl):
        raise (f"File is not exist: {path_to_jsonl}")

    elastic_client.bulk_documents(path_to_documents=path_to_jsonl)
    elastic_client.count_documents_in_index()


def create_index(path_to_index_json: str, elastic_client: Any) -> None:
    if not elastic_client.index_is_alive():
        elastic_client.create_index(path_to_index_json=path_to_index_json)
    else:
        logger.info("Index is already exists.")


if __name__ == "__main__":
    from elastic.elastic_api import ElasticIndex
    from engine.config import ConfigVideoProcessor
    from engine.embedding import Embedding
    from engine.model import VideoProcessor
    from engine.morph import Morph

    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    config = ConfigVideoProcessor()

    video_processor = VideoProcessor(config=config, device=device)
    embedding_model = Embedding(device=device)
    morph_model = Morph()

    elastic_client = ElasticIndex(
        index_name=os.environ.get("INDEX_NAME"),
        elastic_host_port="8201",  # Убедись что используешь правильный порт
        elastic_password="LMjaNYeQujhtOHwjYFn6",
        elastic_ca_certs_path="./src/elastic/certs/http_ca.crt",
    )

    # input = {
    #     "link": "https://cdn-st.rutubelist.ru/media/b0/e9/ef285e0241139fc611318ed33071/fhd.mp4",
    #     "description": "#нарезкистримов , #dota2 , #cs2 , #fifa23 , #minecraft , #майнкрафт , #геншин , #genshin"
    # }

    input = {
        "link": "https://cdn-st.rutubelist.ru/media/87/43/b11df3f344d0af773aac81e410ee/fhd.mp4",
        "description": "",
    }

    index_one_document(
        input=input,
        elastic_client=elastic_client,
        video_processor=video_processor,
        embedding_model=embedding_model,
        morph_model=morph_model,
    )
