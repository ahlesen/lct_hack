from pydantic import BaseModel


class ConfigImageCaptioning(BaseModel):
    min_length: int = 0
    max_length: int = 200
    num_beams: int = 4
    model_name_image_caption: str = "GeorgeBredis/ruIdefics2-ruLLaVA-merged"

    model_name_audio_whisper: str = "small"
    model_name_audio_lang: str = "ru"

    image_chat_template : list[dict[str,str]] = [
        {
            "role": "user",
            "content": [
                {"type": "image"},
                {"type": "text", "text": "Что изображено на данной картинке?"},
            ],
        }
    ]
