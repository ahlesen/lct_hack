from __future__ import annotations
import os

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
