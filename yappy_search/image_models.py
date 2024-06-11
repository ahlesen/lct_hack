import av
from PIL import Image
from transformers import AutoModelForVision2Seq, AutoProcessor, Idefics2ForConditionalGeneration, BitsAndBytesConfig
import torch

from yappy_search.config import ConfigImageCaptioning


class ImageCaptioning:
    def __init__(self, config: ConfigImageCaptioning, device: str, w_quant:bool=True, ):
        if w_quant:
            self.processor = AutoProcessor.from_pretrained(
                config.model_name_image_caption,
                do_image_splitting=False
            )

            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_use_double_quant=True,
                bnb_4bit_compute_dtype=torch.float16
            )
            self.model = Idefics2ForConditionalGeneration.from_pretrained(
                config.model_name_image_caption,
                torch_dtype=torch.float16,    
                quantization_config=quantization_config,
            )
        else:
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
        self.image_chat_template = config.image_chat_template

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
            self.image_chat_template,
            add_generation_prompt=True,
        )
        # ! тут пока берем в анализ только 1 фрейм
        inputs = self.processor(text=prompt, images=pil_images[:1], return_tensors="pt")
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        # generated_ids = self.model.generate(**inputs, **self.gen_kwargs)
        generated_ids = self.model.generate(**inputs, max_new_tokens= self.gen_kwargs["max_length"])
        generated_texts = self.processor.batch_decode(
            generated_ids, skip_special_tokens=True
        )
        return "|".join([text.strip() for text in generated_texts])
