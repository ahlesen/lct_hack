"""Эмбеддер."""

from typing import List

import torch.nn.functional as F
from torch import Tensor
from transformers import AutoModel, AutoTokenizer


class Embedding:
    """Класс для создания эмбеддингов текстов."""

    def __init__(self, device: str) -> None:
        """Инициализация эмбеддера.

        :param device: Устройство для вычислений (например, "cuda" или "cpu").
        """
        self.tokenizer = AutoTokenizer.from_pretrained("intfloat/multilingual-e5-base")
        self.model = AutoModel.from_pretrained("intfloat/multilingual-e5-base").to(device)
        self.max_length = 512

    @staticmethod
    def _average_pool(last_hidden_states: Tensor, attention_mask: Tensor) -> Tensor:
        """Пуллирование скрытых состояний с учетом маски внимания.

        :param last_hidden_states: Последние скрытые состояния.
        :param attention_mask: Маска внимания.
        :return: Усредненные скрытые состояния.
        """
        last_hidden = last_hidden_states.masked_fill(~attention_mask[..., None].bool(), 0.0)
        return last_hidden.sum(dim=1) / attention_mask.sum(dim=1)[..., None]

    def __call__(self, texts: List[str]) -> List[List[float]]:
        """Each input text should start with "query: " or "passage: ",even for non-English texts.

        :param texts: Список текстов для эмбеддинга.
        :return: Список эмбеддингов для каждого текста.
        """
        # Tokenize the input texts
        batch_dict = self.tokenizer(
            texts, max_length=512, padding=True, truncation=True, return_tensors="pt"
        )
        batch_dict = {k: v.to(self.model.device) for k, v in batch_dict.items()}

        outputs = self.model(**batch_dict)
        embeddings = self._average_pool(
            outputs.last_hidden_state, batch_dict["attention_mask"]
        )  # fp32

        # normalize embeddings
        embeddings = F.normalize(embeddings, p=2, dim=1)

        return embeddings.detach().cpu().tolist()


if __name__ == "__main__":
    input_texts = [
        "passage: #fashion #мода #красота #стиль #образ #модныйлук",
        (
            "passage: #уходзакожей #уходзасобой #бьютирутина #бьюти #ноготочки "
            "#маникюр #прическа #укладка #уход #бьютирутина"
        ),
        "passage: #красивыедевушки #танец #грудь #boobs",
        (
            "passage: #мульт , #мультики , #мультик , #мультфильм , #мультфильмы , "
            "#симпсоны , #грифины , #трикота , #дисней"
        ),
        "passage: #лайфхаки , #эксперименты , #roblox , #игрушки , #diy , #танцы",
    ]

    e5_embedding = Embedding("cuda:0")

    embs = e5_embedding(input_texts)
    print(embs)
