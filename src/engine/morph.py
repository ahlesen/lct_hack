"""Модуль для морфологического анализа текстов."""
from typing import List

from joblib import Parallel, delayed
from pymorphy3.analyzer import MorphAnalyzer


class Morph:
    """Класс для морфологического анализа и извлечения тегов из текстов."""

    def __init__(self) -> None:
        """Инициализация морфологического анализатора."""
        self.target_pos = {"NOUN", "ADJF"}  # сущ-е и полное прилагательное
        self.morph = MorphAnalyzer(lang="ru")

    def str_get_tags_morph(self, text: str) -> str:
        """Получение морфологических тегов для строки текста.

        :param text: Входной текст.
        :return: Строка с релевантными нормализованными формами.
        """
        text_split = text.split(" ")
        morph_results = [self.morph.parse(token)[0] for token in text_split]

        relevant_tokens = []
        for result in morph_results:
            if result.tag.POS in self.target_pos:  # хз как доставать LATN
                relevant_tokens += [result.normal_form]  # достаем нормальную форму

        return " ".join(relevant_tokens)

    def batch_get_tags_morph(self, texts: List[str]) -> List[str]:
        """Обработка списка текстов для получения морфологических тегов.

        :param texts: Список текстов.
        :return: Список строк с релевантными нормализованными формами.
        """
        parallel = Parallel(n_jobs=-1, return_as="generator")
        output_generator = parallel(delayed(self.str_get_tags_morph)(text) for text in texts)
        return list(output_generator)


if __name__ == "__main__":
    input_texts = [
        "#fashion #мода #красота #стиль #образ #модныйлук",
        (
            "#уходзакожей #уходзасобой #бьютирутина #бьюти #ноготочки #маникюр "
            "#прическа #укладка #уход #бьютирутина"
        ),
        "#красивыедевушки #танец #грудь #boobs",
        (
            "#мульт , #мультики , #мультик , #мультфильм , #мультфильмы , #симпсоны "
            ", #грифины , #трикота , #дисней"
        ),
        "#лайфхаки , #эксперименты , #roblox , #игрушки , #diy , #танцы",
    ]

    morph = Morph()

    cleaned_tags = morph.batch_get_tags_morph(input_texts)
    print(cleaned_tags)
