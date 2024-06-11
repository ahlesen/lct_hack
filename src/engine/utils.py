from __future__ import annotations
import os
from typing import Optional
from moviepy.editor import VideoFileClip
from pydub import AudioSegment
import requests


def download_video(url: str, output_path: str, max_retries: int = 5, timeout:int =60) -> requests.models.Response:
    """Функция для скачивания видео с обработкой ошибок и повторными попытками"""
    retries = 0
    while retries < max_retries:
        try:
            response = requests.get(url, stream=True, timeout=timeout)
            if response.status_code == 200:
                with open(output_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                return response
            else:
                retries += 1
                print(f"--Failed to download {url}, status code: {response.status_code}| retries = {retries}")
        except (requests.exceptions.RequestException, requests.exceptions.ChunkedEncodingError) as e:
            print(f"Error downloading {url}, attempt {retries + 1} of {max_retries}: {e}")
            retries += 1
            if retries == max_retries:
                print(f"!!Final Fail of downloading {url} after {max_retries} attempts| retries = {retries}")
                return None

def extract_audio_with_check(video_path: str, output_dir: str)->str:
    try:
        video_clip = VideoFileClip(video_path)
        audio_file_path = os.path.join(
            output_dir, os.path.basename(video_path).replace(".mp4", ".mp3")
        )
        if video_clip.audio is None:
            print(f"No audio found in {video_path}. Creating empty audio file.")
            silent_audio = AudioSegment.silent(duration=1000)
            silent_audio.export(audio_file_path, format="mp3")
        else:
            video_clip.audio.write_audiofile(audio_file_path, verbose=False, logger=None)
        return audio_file_path
    except Exception as e:
        print(f"Failed to extract audio from {video_path}: {e}")
        return None

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