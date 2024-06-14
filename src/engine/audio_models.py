"""Модели работы с аудио."""

from __future__ import annotations

import asyncio

import torch
from shazamio import Shazam
from transformers import (
    AutoModelForSpeechSeq2Seq,
    AutoProcessor,
    MarianMTModel,
    MarianTokenizer,
    pipeline,
)


class AudioTranscription:
    """Класс для транскрипции аудио с использованием модели Whisper."""

    def __init__(
        self,
        device: torch.device,
        model_name: str = "openai/whisper-large-v3",
        batch_size: int = 16,
        max_new_tokens: int = 128,
        chunk_length_s: int = 30,
    ):
        """Инициализировать модель.

        :param model_name: Имя модели.
        :param device: Устройство для вычислений (например, "cuda" или "cpu").
        :param batch_size: Размер батча.
        :param max_new_tokens: Максимальное количество новых токенов.
        :param chunk_length_s: Длина фрагмента в секундах.
        """
        torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
        self.model = AutoModelForSpeechSeq2Seq.from_pretrained(
            model_name,
            torch_dtype=torch_dtype,
            low_cpu_mem_usage=True,
            use_safetensors=True,
        ).to(device)
        self.processor = AutoProcessor.from_pretrained(model_name)

        self.pipe = pipeline(
            "automatic-speech-recognition",
            model=self.model,
            tokenizer=self.processor.tokenizer,
            feature_extractor=self.processor.feature_extractor,
            max_new_tokens=max_new_tokens,
            chunk_length_s=chunk_length_s,
            batch_size=batch_size,
            return_timestamps=True,
            torch_dtype=torch_dtype,
            device=device,
        )

    def transcribe(self, audio_path: str) -> str:
        """Транскрибировать аудио файл в текст.

        :param audio_path: Путь к аудио файлу.
        :return: Распознанный текст.
        """
        result = self.pipe(audio_path)
        return result["text"]


class SongRecognition:
    """Класс для распознавания песен с использованием Shazam API."""

    def __init__(self, timeout: int = 60):
        """Инициализация класса SongRecognition.

        :param timeout: Таймаут для распознавания в секундах.
        """
        self.shazam = Shazam()
        self.timeout = timeout

    async def recognize_audio(self, audio_path: str) -> dict[str, str]:
        """Распознать песню по аудио файлу.

        :param audio_path: Путь к аудио файлу.
        :return: Словарь с информацией о песне (название, автор, URL).
        """
        result = await self.shazam.recognize_song(audio_path)
        if result and "track" in result:
            track = result["track"]
            return {
                "title": track["title"],
                "subtitle": track["subtitle"],
                "url": track["url"],
            }
        else:
            return {
                "title": "",
                "subtitle": "",
                "url": "",
            }

    # Обертка для выполнения задачи с тайм-аутом
    async def recognize_audio_with_timeout(self, audio_path):
        """Распознать песню с таймаутом.

        :param audio_path: Путь к аудио файлу.
        :return: Словарь с информацией о песне (название, автор, URL).
        """
        try:
            return await asyncio.wait_for(self.recognize_audio(audio_path), self.timeout)
        except asyncio.TimeoutError:
            print(f"Recognition for {audio_path} timed out.")
            return {
                "title": "",
                "subtitle": "",
                "url": "",
            }


class TextTransliteration:
    def __init__(self, model_name="Helsinki-NLP/opus-mt-en-ru"):
        self.model_name = model_name
        self.model = MarianMTModel.from_pretrained(model_name)
        self.tokenizer = MarianTokenizer.from_pretrained(model_name)

    def transliterate_to_russian(self, text):
        batch = self.tokenizer([text], return_tensors="pt")
        translated = self.model.generate(**batch)
        translated_text = self.tokenizer.batch_decode(translated, skip_special_tokens=True)[0]
        return translated_text
