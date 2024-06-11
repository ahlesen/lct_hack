import whisper
from shazamio import Shazam


class AudioTranscription:
    def __init__(self, model_name: str = "small", language: str = "ru"):
        self.model = whisper.load_model(model_name)
        self.language = language


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
