from __future__ import annotations

import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline

from shazamio import Shazam
import asyncio


class AudioTranscription:
    def __init__(
            self, 
            model_name: str = "openai/whisper-large-v3",
            device: str = "cuda",
            batch_size: int = 16,
            max_new_tokens: int = 128,
            chunk_length_s: int = 30,
        ):
        torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
        self.model = AutoModelForSpeechSeq2Seq.from_pretrained(
            model_name, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
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
            device=device
        )

    def transcribe(self, audio_path: str)->str:
        result = self.pipe(audio_path)
        return result["text"]


class SongRecognition:
    def __init__(self, timeout:int = 60):
        self.shazam = Shazam()
        self.timeout = timeout

    async def recognize_audio(self, audio_path: str)->dict[str,str]:
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
        try:
            return await asyncio.wait_for(self.recognize_audio(audio_path), self.timeout)
        except asyncio.TimeoutError:
            print(f"Recognition for {audio_path} timed out.")
            return {
                "title": "",
                "subtitle": "",
                "url": "",
            }