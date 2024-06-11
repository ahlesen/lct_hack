import av
from PIL import Image
from transformers import Blip2ForConditionalGeneration, Blip2Processor
import cv2


class ImageCaptioning:
    def __init__(self, model_name_image_caption:str, device: str):
        if device.type == 'cpu':
            self.processor = Blip2Processor.from_pretrained(model_name_image_caption)
            self.model = Blip2ForConditionalGeneration.from_pretrained(
                model_name_image_caption,  device_map="auto"
            )
        
        else:
            self.processor = Blip2Processor.from_pretrained(model_name_image_caption)
            self.model = Blip2ForConditionalGeneration.from_pretrained(
                model_name_image_caption, load_in_8bit=True, device_map="auto"
            )
        self.device = device

        

    @staticmethod
    def extract_frames(video_path:str, num_frames:int=3):
        cap = cv2.VideoCapture(video_path)
        frames = []
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        if num_frames == 1:
            # Если требуется один кадр, выбираем из середины видео
            middle_frame = total_frames // 2
            cap.set(cv2.CAP_PROP_POS_FRAMES, middle_frame)
            ret, frame = cap.read()
            if ret:
                frames.append(frame)
        else:
            # Иначе выбираем num_frames кадров с равными интервалами
            interval = total_frames // num_frames
            for i in range(0, total_frames, interval):
                cap.set(cv2.CAP_PROP_POS_FRAMES, i)
                ret, frame = cap.read()
                if ret:
                    frames.append(frame)
                if len(frames) == num_frames:
                    break

        return frames
    
    def generate_caption(self, video_path:str)->str:
        frames = self.extract_frames(video_path)
        inputs = self.processor(images=frames, return_tensors="pt").to(self.device)
        outputs = self.model.generate(**inputs)
        caption = self.processor.decode(outputs[0], skip_special_tokens=True)
        return caption


