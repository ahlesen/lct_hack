from __future__ import annotations
import os
from typing import Optional
import requests


def download_video(
    url: str | os.PathLike, output_path: str | os.PathLike
) -> requests.models.Response:
    """Функция для скачивания видео"""

    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return response
    else:
        print(f"Failed to download {url}")


def embedding_text_processing_passage(raw_description: str,
                                      raw_song_name: str,
                                      raw_song_author: str,
                                      raw_audio_transcription: Optional[str] = None,
                                      raw_video_hashtags: Optional[str] = None) -> str:
    result_text_field = "passage: " + raw_description + " " + raw_song_name + " " + raw_song_author
    if raw_audio_transcription is not None:
        result_text_field = result_text_field + " " + raw_audio_transcription
    if raw_video_hashtags is not None:
        result_text_field = result_text_field + " " + raw_video_hashtags

    return result_text_field

def embedding_text_processing_query(user_query: str):
    return "query: " + user_query