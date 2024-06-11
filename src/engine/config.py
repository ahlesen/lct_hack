import os
from pydantic import BaseModel


class ConfigVideoProcessor(BaseModel):
    batch_size: int = 16

    model_name_image_caption: str = "Salesforce/blip2-opt-2.7b"

    video_dir: str = 'data/data_video/'
    audio_output_dir: str = 'data/data_audio/'
    model_name_audio_whisper: str = "openai/whisper-large-v3"
    max_new_tokens: int = 128
    chunk_length_s: int = 30

    timeout:int = 60

    image_chat_template : list[dict[str,str]] = [
        {
            "role": "user",
            "content": [
                {"type": "image"},
                {"type": "text", "text": "Что изображено на данной картинке?"},
            ],
        }
    ]

    def __init__(self, **data):
        super().__init__(**data)
        self.ensure_directories_exist()

    def ensure_directories_exist(self):
        os.makedirs(self.video_dir, exist_ok=True)
        os.makedirs(self.audio_output_dir, exist_ok=True)