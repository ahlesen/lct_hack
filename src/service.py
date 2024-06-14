"""Методы API."""

import os
from pathlib import Path
from typing import List

import torch
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Request, Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from src.base_logger import logger
from src.elastic.elastic_api import ElasticIndex
from src.engine.config import ConfigVideoProcessor
from src.engine.embedding import Embedding
from src.engine.model import VideoProcessor
from src.engine.morph import Morph
from src.index import index_one_document
from src.schemas import VideoInsertInput, VideoSearchInput, VideoSearchResult
from src.search import search_documents  # noqa: F401

current_file_path = Path(__file__)
dotenv_path = current_file_path.parent.parent / '.env'
load_dotenv(dotenv_path)

DEVICE = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
CONFIG = ConfigVideoProcessor()


processor_model = VideoProcessor(config=CONFIG, device=DEVICE)
embedding_model = Embedding(device=DEVICE)
morph_model = Morph()
elastic_client = ElasticIndex(
    index_name=os.environ.get("INDEX_NAME"),
    elastic_host_port=os.environ.get("ELASTIC_PORT"),  # Убедись что используешь правильный порт
    elastic_password=os.environ.get("ELATIC_PASSWORD"),
    elastic_ca_certs_path="./src/elastic/certs/http_ca.crt",
)

suggest_elastic_client = ElasticIndex(
    index_name=os.environ.get("SUGGEST_INDEX_NAME"),
    elastic_host_port=os.environ.get("ELASTIC_PORT"),  # Убедись что используешь правильный порт
    elastic_password=os.environ.get("ELATIC_PASSWORD"),
    elastic_ca_certs_path="./src/elastic/certs/suggest_http_ca.crt",
)  # НАПИСАТЬ РУЧКУ САДЖЕСТЕРА

router = APIRouter()


@router.get(
    "/monitoring/status",
    response_class=Response,
    status_code=status.HTTP_200_OK,
    include_in_schema=False,
    responses={
        200: {"description": "Success"},
        500: {"description": "Internal server error"},
    },
)
async def liveness_probe(_: Request) -> JSONResponse:
    """Точка проверки жизни для Kubernetes.

    :return: JSON-ответ, указывающий, что сервис жив.
    """
    return JSONResponse(jsonable_encoder({"alive": True}), status_code=status.HTTP_200_OK)


@router.get(
    "/monitoring/ready",
    response_class=Response,
    status_code=status.HTTP_200_OK,
    include_in_schema=False,
    responses={
        200: {"description": "Success"},
        500: {"description": "Internal server error"},
    },
)
async def readiness_probe(_: Request) -> JSONResponse:
    """Точка проверки готовности для Kubernetes.

    :return: JSON-ответ, указывающий, что сервис готов.
    """
    return JSONResponse(jsonable_encoder({"ready": True}), status_code=status.HTTP_200_OK)


@router.post(
    "/add_video_to_index",
    tags=["ADD2INDEX"],
    summary="Add video to index",
    description="Добавить видео в индекс",
)
async def add_video_to_index(input: VideoInsertInput):
    """Добавить видео в индекс.

    :param input: Входные данные с ссылкой на видео и описанием.
    :return: Результат процесса индексации.
    """
    # try:
    ## это проба для проверки API               # noqa: E266
    # pred = await processor_model.process_video_from_link(input.video_link)
    # result =  VideoInsertOutput(
    #     caption = pred['captions'],
    #     transcription = pred['transcription'],
    #     shazam_title = pred['shazam_title'],
    #     shazam_subtitle = pred['shazam_subtitle'],
    #     shazam_url = pred['shazam_url'],
    # )
    # return result
    # что надо на самом деле, ждем
    print(input)
    document_res = await index_one_document(
        input=input,
        elastic_client=elastic_client,
        video_processor=processor_model,
        embedding_model=embedding_model,
        morph_model=morph_model,
    )
    return document_res
    # except Exception as e:
    #     logger.error(f"Error during add_video_to_index: {e}")
    #     raise HTTPException(status_code=500, detail="add_video_to_index failed")


@router.post(
    "/search",
    tags=["SEARCH"],
    summary="Search by query",
    description="Получить список релевантных видео по запросу",
)
def make_search(input: VideoSearchInput):
    # def make_search(input: VideoSearchInput) -> List[VideoSearchResult]:
    """Поиск видео на основе текстового запроса.

    :param input: Входные данные с поисковым запросом.
    :return: Список видео, соответствующих критериям поиска.
    """
    # try:
    # res_example = [
    #     {
    #         "video_link": "https://cdn-st.rutubelist.ru/media/87/43/b11df3f344d0af773aac81e410ee/fhd.mp4",  # noqa: E501
    #         "description": "#нарезкистримов , #dota2 , #cs2 , #fifa23 , #minecraft , #майнкрафт , #геншин , #genshin",  # noqa: E501
    #     },
    #     {
    #         "video_link": "https://cdn-st.rutubelist.ru/media/39/6c/b31bc6864bef9d8a96814f1822ca/fhd.mp4",  # noqa: E501
    #         "description": "🤫НЕ ВВОДИ ЭТУ КОМАНДУ В РОБЛОКС ! #shorts #roblox #роблокс",
    #     },
    #     {
    #         "video_link": "https://cdn-st.rutubelist.ru/media/e9/e0/b47a9df14a5e97942715e5e705c0/fhd.mp4",  # noqa: E501
    #         "description": "#boobs , #красивыедевушки , #ass",
    #     },
    # ]
    # return res_example
    # что надо на самом деле
    docs = search_documents(
        user_query=input.query, elastic_client=elastic_client, embedding_model=embedding_model
    )
    return docs
    # except Exception as e:
    #     logger.error(f"Error during Search: {e}")
    #     raise HTTPException(status_code=500, detail="Search failed")
