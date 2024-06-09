import av
from PIL import Image
from transformers import AutoModelForVision2Seq, AutoProcessor

from yappy_search.config import ConfigImageCaptioning


class ImageCaptioning:
    def __init__(self, config: ConfigImageCaptioning, device: str):
        self.processor = AutoProcessor.from_pretrained(config.model_name_image_caption)
        self.model = AutoModelForVision2Seq.from_pretrained(config.model_name_image_caption).to(
            device
        )
        self.gen_kwargs = {
            "min_length": config.min_length,
            "max_length": config.max_length,
            "num_beams": config.num_beams,
        }
        self.device = device

    def generate_caption(self, video_path: str):
        container = av.open(video_path)
        ### Делаем нарезку фреймов
        seg_len = container.streams.video[0].frames
        indices = [int(0.25 * seg_len), int(0.5 * seg_len), int(0.75 * seg_len)]
        frames = []

        container.seek(0)
        for i, frame in enumerate(container.decode(video=0)):
            if i in indices:
                frames.append(frame.to_ndarray(format="rgb24"))

        pil_images = [Image.fromarray(frame) for frame in frames]
        ###
        prompt = self.processor.apply_chat_template(
            [
                {
                    "role": "user",
                    "content": [
                        {"type": "image"},
                        {"type": "text", "text": "Что изображено на данной картинке?"},
                    ],
                }
            ],
            add_generation_prompt=True,
        )
        # ! тут пока берем в анализ только 1 фрейм
        inputs = self.processor(text=prompt, images=pil_images[:1], return_tensors="pt")
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        # generated_ids = self.model.generate(**inputs, **self.gen_kwargs)
        generated_ids = self.model.generate(**inputs, max_new_tokens=100)
        generated_texts = self.processor.batch_decode(
            generated_ids, skip_special_tokens=True
        )
        return "|".join([text.strip() for text in generated_texts])
