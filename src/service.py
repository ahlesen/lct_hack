"""Методы API."""

import os
from pathlib import Path
from typing import List

import torch
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Query, Request, Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from src.base_logger import logger
from src.elastic.elastic_api import ElasticIndex
from src.engine.config import ConfigVideoProcessor
from src.engine.embedding import Embedding
from src.engine.model import VideoProcessor
from src.engine.morph import Morph
from src.index import index_one_document
from src.schemas import Text, Video
from src.search import search_documents, search_suggests  # noqa: F401
from src.utils import entrypoint

current_file_path = Path(__file__)
dotenv_path = current_file_path.parent.parent / '.env'
load_dotenv(dotenv_path)

DEVICE = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
CONFIG = ConfigVideoProcessor()


processor_model = VideoProcessor(config=CONFIG, device=DEVICE)
embedding_model = Embedding(device=DEVICE)
morph_model = Morph()
elastic_client, suggest_elastic_client = entrypoint()

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
    "/index",
    tags=["index"],
    summary="Add video to index",
    description="Добавляет новое видео в хранилище - индекс",
    # response_model=Video
)
async def add_index(input: Video):
    """Добавить видео в индекс.

    :param input: Входные данные с ссылкой на видео и описанием.
    :return: Результат процесса индексации.
    """
    # try:
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


@router.get(
    "/search",
    tags=["search"],
    summary="Search by query",
    description="Получить список релевантных видео по запросу",
)
def search_video(
    # input: Text,
    text: str = Query(..., description="Текст, по которому осуществляется запрос")
    # response_model=List[Video]
):
    # def make_search(input: VideoSearchInput) -> List[VideoSearchResult]:
    """Поиск наиболее релевантных видео на основе текстового запроса.

    :param input: Входные данные с поисковым запросом.
    :return: Список видео, соответствующих критериям поиска.
    """
    # try:
    # что надо на самом деле
    print(f"search:{text}")
    docs = search_documents(
        user_query=text, elastic_client=elastic_client, embedding_model=embedding_model
    )
    return docs
    # except Exception as e:
    #     logger.error(f"Error during Search: {e}")
    #     raise HTTPException(status_code=500, detail="Search failed")


@router.get(
    "/suggest",
    tags=["suggest"],
    summary="Suggest by query",
    description="Получить список поисковых подсказок по запросу",
)
def make_suggest(
    # input: Text,
    text: str = Query(..., description="Текст, по которому осуществляется запрос")
):
    # def make_search(input: VideoSearchInput) -> List[VideoSearchResult]:
    """Поиск подсказок на основе текстового запроса.

    :param input: Входные данные с поисковым запросом.
    :return: Список подсказок, соответствующих запросу.
    """
    # try:
    docs = search_suggests(user_query=text, elastic_client=suggest_elastic_client)
    return docs
    # except Exception as e:
    #     logger.error(f"Error during Suggest: {e}")
    #     raise HTTPException(status_code=500, detail="Suggest failed")
