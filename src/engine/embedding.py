from typing import List
from transformers import AutoTokenizer, AutoModel
import torch.nn.functional as F
from torch import Tensor
from transformers import AutoTokenizer, AutoModel


def e5_embedding(texts: List[str], model, tokenizer) -> List[List[float]]:
    """Each input text should start with "query: " or "passage: ", even for non-English texts."""
    def _average_pool(last_hidden_states: Tensor,
                     attention_mask: Tensor) -> Tensor:
        last_hidden = last_hidden_states.masked_fill(~attention_mask[..., None].bool(), 0.0)
        return last_hidden.sum(dim=1) / attention_mask.sum(dim=1)[..., None]
    
    # Tokenize the input texts
    batch_dict = tokenizer(texts, max_length=512, padding=True, truncation=True, return_tensors='pt')
    
    outputs = model(**{k: v.to(model.device) for k, v in batch_dict.items()})
    embeddings = _average_pool(outputs.last_hidden_state, batch_dict['attention_mask'])
    
    # normalize embeddings
    embeddings = F.normalize(embeddings, p=2, dim=1)

    return embeddings.detach().cpu().tolist()


if __name__ == "__main__":
    input_texts = ['passage: #fashion #мода #красота #стиль #образ #модныйлук',
                   'passage: #уходзакожей #уходзасобой #бьютирутина #бьюти #ноготочки #маникюр #прическа #укладка #уход #бьютирутина',
                   'passage: #красивыедевушки #танец #грудь #boobs',
                   'passage: #мульт , #мультики , #мультик , #мультфильм , #мультфильмы , #симпсоны , #грифины , #трикота , #дисней',
                   'passage: #лайфхаки , #эксперименты , #roblox , #игрушки , #diy , #танцы']
    
    tokenizer = AutoTokenizer.from_pretrained('intfloat/multilingual-e5-base')
    model = AutoModel.from_pretrained('intfloat/multilingual-e5-base')

    embs = e5_embedding(input_texts, model, tokenizer)