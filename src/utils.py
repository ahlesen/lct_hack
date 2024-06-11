# Здесь вспомогательные методы касательно search.py & index.py
# В частонсти метод по формирования docuemnts.json на 40к примерах (25к)
from typing import Optional

import jsonlines
import pandas as pd


def create_documents_jsonl(
    data: Optional[pd.DataFrame] = None,
    path_to_pq: Optional[str] = None,
    path_to_save: str = "../data/documents.jsonl",
):
    if data is None and path_to_pq is None:
        raise Exception
    if data is None:
        data = pd.read_parquet(path_to_pq)

    with jsonlines.open(path_to_save, mode="a") as writer:
        for idx, row in data.iterrows():
            sample = {}
            sample["doc_id"] = row["index orig"]
            sample["embedding"] = row["embedding"]
            sample["text_hashtags"] = row["description_postprocessed"]
            sample["video_hastags"] = ""
            sample["audio_transcription"] = row["transcription_postprocessed"]
            sample["song_name"] = row["title_shazam_postprocessed"]
            sample["song_author"] = row["subtitle_shazam_postprocessed"]
            writer.write(sample)


class Mopher:

    