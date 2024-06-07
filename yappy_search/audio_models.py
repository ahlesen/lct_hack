import asyncio
import os

import whisper
from moviepy.editor import VideoFileClip
from shazamio import Shazam


class AudioTranscription:
    def __init__(self, model_name: str = "small", language: str = "ru"):
        self.model = whisper.load_model(model_name)
        self.language = language

    def extract_audio(self, video_path: str, output_dir: str):
        video_clip = VideoFileClip(video_path)
        audio_file_path = os.path.join(
            output_dir, os.path.basename(video_path).replace(".mp4", ".mp3")
        )
        video_clip.audio.write_audiofile(audio_file_path, verbose=False, logger=None)
        return audio_file_path

    def transcribe(self, audio_path: str):
        result = self.model.transcribe(audio_path, language=self.language)
        return result["text"]


class SongRecognition:
    def __init__(self):
        self.shazam = Shazam()

    async def recognize_audio(self, audio_path: str):
        result = await self.shazam.recognize_song(audio_path)
        if result and "track" in result:
            track = result["track"]
            return {
                "title": track["title"],
                "subtitle": track["subtitle"],
                "url": track["url"],
            }
        return "Song not recognized"
