"""Финальная модель работы."""

from __future__ import annotations

import asyncio
import os
from typing import Optional

import torch

from src.engine.audio_models import AudioTranscription, SongRecognition
from src.engine.config import ConfigVideoProcessor
from src.engine.image_models import ImageCaptioning
from src.engine.utils import download_video, extract_audio_with_check


class VideoProcessor:
    """Класс для обработки видео, извлечения аудио и генерации подписей."""

    def __init__(self, config: ConfigVideoProcessor, device: torch.device):
        """Инициализация класса VideoProcessor.

        :param config: Конфигурация для обработки видео.
        :param device: Устройство для вычислений (например, "cuda" или "cpu").
        """
        self.config = config
        self.image_captioning = ImageCaptioning(
            model_name_image_caption=config.model_name_image_caption, device=device
        )
        self.audio_transcription = AudioTranscription(
            model_name=config.model_name_audio_whisper,
            device=device,
            batch_size=config.batch_size,
            max_new_tokens=config.max_new_tokens,
            chunk_length_s=config.chunk_length_s,
        )
        self.song_recognition = SongRecognition(timeout=config.timeout)
        self.device = device

    def process_video_from_video(
        self,
        video_path: str,
    ) -> dict[str, str]:
        """Обработать видео файл и извлечь из него информацию.

        :param video_path: Путь к видео файлу.
        :return: Словарь с информацией о видео, включая подписи и транскрипции.
        """
        captions = self.image_captioning.generate_caption(video_path)
        audio_path = extract_audio_with_check(video_path, self.config.audio_output_dir)
        if audio_path is None:
            raise ValueError(f"Failed to extract audio from {video_path}")
        transcription = self.audio_transcription.transcribe(audio_path)

        loop = asyncio.get_event_loop()
        recognition = loop.run_until_complete(
            self.song_recognition.recognize_audio_with_timeout(audio_path)
        )

        return {
            "captions": captions,
            "transcription": transcription,
            "shazam title": recognition["title"],
            "shazam subtitle": recognition["subtitle"],
            "shazam url": recognition["url"],
        }

    def process_video_from_link(self, video_url: str, verbose: bool = False) -> dict[str, str]:
        """Скачать и обработать видео по ссылке.

        :param video_url: URL видео.
        :param verbose: Включить подробный вывод.
        :return: Словарь с информацией о видео, включая подписи и транскрипции.
        """
        # скачать видео
        video_name = f"{'_'.join(video_url.split('media')[1].split('/'))}"
        video_path = os.path.join(self.config.video_dir, video_name)
        if verbose:
            print(f"video_path:{video_path}")
        if not os.path.isfile(video_path):
            download_video(video_url, video_path)
        # из видео получаем аудио
        audio_file_path: Optional[str] = os.path.join(
            self.config.audio_output_dir,
            os.path.basename(video_path).replace(".mp4", ".mp3"),
        )
        if verbose:
            print(f"audio_file_path:{audio_file_path}")
        if not os.path.isfile(audio_file_path):  # type: ignore[arg-type]
            audio_file_path = extract_audio_with_check(video_path, self.config.audio_output_dir)
        captions = self.image_captioning.generate_caption(video_path)
        if verbose:
            print(f"caption:{captions}")
        transcription = self.audio_transcription.transcribe(audio_file_path)  # type:ignore
        if verbose:
            print(f"transcription:{transcription}")

        loop = asyncio.get_event_loop()
        recognition = loop.run_until_complete(
            self.song_recognition.recognize_audio_with_timeout(audio_file_path)
        )
        if verbose:
            print(f"recognition:{recognition}")
        if verbose:
            print(f"remove files: video_path{video_path}|audio_file_path{audio_file_path}")
            os.remove(video_path)
            os.remove(audio_file_path)  # type: ignore[arg-type]

        return {
            "captions": captions,
            "transcription": transcription,
            "shazam title": recognition["title"],
            "shazam subtitle": recognition["subtitle"],
            "shazam url": recognition["url"],
        }


if __name__ == "__main__":
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    config = ConfigVideoProcessor()
    processor = VideoProcessor(config=config, device=device)
    video_url: str = (
        "https://cdn-st.rutubelist.ru/media/b0/e9/ef285e0241139fc611318ed33071/fhd.mp4"
    )
    results = processor.process_video_from_video(video_url)
    print(results)
