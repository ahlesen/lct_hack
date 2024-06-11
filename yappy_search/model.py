import asyncio
import os

import nest_asyncio

nest_asyncio.apply()
from yappy_search.audio_models import AudioTranscription, SongRecognition
from yappy_search.config import ConfigImageCaptioning
from yappy_search.image_models import ImageCaptioning


class VideoProcessor:
    def __init__(self, config: ConfigImageCaptioning, device: str = "cuda", w_image_caption:bool=False):
        self.w_image_caption = w_image_caption
        if self.w_image_caption:
            self.image_captioning = ImageCaptioning(config, device)
        self.audio_transcription = AudioTranscription(
            model_name=config.model_name_audio_whisper,
            language=config.model_name_audio_lang,
        )
        self.song_recognition = SongRecognition()
        self.device = device

    def process_video(self, video_path: str, audio_output_dir: str):
        if self.w_image_caption:
            captions = self.image_captioning.generate_caption(video_path)

        audio_path = self.audio_transcription.extract_audio(
            video_path, audio_output_dir
        )
        transcription = self.audio_transcription.transcribe(audio_path)

        loop = asyncio.get_event_loop()
        recognition = loop.run_until_complete(
            self.song_recognition.recognize_audio(audio_path)
        )
        if self.w_image_caption:
            return {
                "captions": captions,
                "transcription": transcription,
                "recognition": recognition,
            }
        else:
            return {
                "transcription": transcription,
                "recognition": recognition,
            }


def example(video_path: str):
    results = processor.process_video(video_path, audio_output_dir)


if __name__ == "__main__":
    config = ConfigImageCaptioning()
    processor = VideoProcessor(config)

    video_path = "path/to/video.mp4"
    audio_output_dir = "audio_files"
    os.makedirs(audio_output_dir, exist_ok=True)

    results = processor.process_video(video_path, audio_output_dir)
