import os

import requests
from moviepy.editor import VideoFileClip
from requests.exceptions import Timeout, RequestException



# Функция для скачивания видео с тайм-аутом
def download_video(url: str, output_path: str, timeout: int = 60) -> requests.models.Response:
    """Функция для скачивания видео с тайм-аутом"""
    try:
        response = requests.get(url, stream=True, timeout=timeout)
        if response.status_code == 200:
            with open(output_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return response
        else:
            print(f"Failed to download {url}")
    except (Timeout, RequestException) as e:
        print(f"Error downloading {url}: {e}")

def extract_audio(video_path: str, output_dir: str):
    video_clip = VideoFileClip(video_path)
    audio_file_path = os.path.join(
        output_dir, os.path.basename(video_path).replace(".mp4", ".mp3")
    )
    video_clip.audio.write_audiofile(audio_file_path, verbose=False, logger=None)
    return audio_file_path