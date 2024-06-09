from typing import List
from joblib import Parallel, delayed
from pymorphy3.analyzer import MorphAnalyzer


TARGET_POS = {"NOUN", "ADJF"} # сущ-е и полное прилагательное


def str_get_tags_morph(text: str, morph: MorphAnalyzer) -> str:
    text_split = text.split(" ")
    morph_results = [morph.parse(token)[0] for token in text_split]
    
    relevant_tokens = []
    for result in morph_results:
        if result.tag.POS in TARGET_POS:  # хз как доставать LATN
            relevant_tokens += [result.normal_form] # достаем нормальную форму
            
    return " ".join(relevant_tokens)


def batch_get_tags_morph(texts: List[str]) -> List[str]:
    morph = MorphAnalyzer(lang='ru')
    parallel = Parallel(n_jobs=-1, return_as="generator")
    
    output_generator = parallel(delayed(str_get_tags_morph)(text, morph) for text in texts)
    
    return list(output_generator)


if __name__ == "__main__":
    input_texts = ['#fashion #мода #красота #стиль #образ #модныйлук',
                   '#уходзакожей #уходзасобой #бьютирутина #бьюти #ноготочки #маникюр #прическа #укладка #уход #бьютирутина',
                   '#красивыедевушки #танец #грудь #boobs',
                   '#мульт , #мультики , #мультик , #мультфильм , #мультфильмы , #симпсоны , #грифины , #трикота , #дисней',
                   '#лайфхаки , #эксперименты , #roblox , #игрушки , #diy , #танцы']
    
    morph = MorphAnalyzer(lang='ru')

    cleaned_tags = batch_get_tags_morph(input_texts)