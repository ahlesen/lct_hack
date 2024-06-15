"""Приложение."""

import streamlit as st
from streamlit_searchbox import st_searchbox

# Данные для примеров
result_search = {
    "ids": [
        "https://cdn-st.rutubelist.ru/media/39/6c/b31bc6864bef9d8a96814f1822ca/fhd.mp4",
        "https://cdn-st.rutubelist.ru/media/87/43/b11df3f344d0af773aac81e410ee/fhd.mp4",
        "https://cdn-st.rutubelist.ru/media/e9/e0/b47a9df14a5e97942715e5e705c0/fhd.mp4",
        'https://cdn-st.rutubelist.ru/media/f8/48/d756d2ed496aa8b93cf5c654cddc/fhd.mp4',
        'https://cdn-st.rutubelist.ru/media/f8/48/d756d2ed496aa8b93cf5c654cddc/fhd.mp4',
        'https://cdn-st.rutubelist.ru/media/f8/48/d756d2ed496aa8b93cf5c654cddc/fhd.mp4',
        'https://cdn-st.rutubelist.ru/media/f8/48/d756d2ed496aa8b93cf5c654cddc/fhd.mp4',
        'https://cdn-st.rutubelist.ru/media/f8/48/d756d2ed496aa8b93cf5c654cddc/fhd.mp4',
        'https://cdn-st.rutubelist.ru/media/f8/48/d756d2ed496aa8b93cf5c654cddc/fhd.mp4',
        'https://cdn-st.rutubelist.ru/media/f8/48/d756d2ed496aa8b93cf5c654cddc/fhd.mp4',
    ],
    "scores": [
        86.33928,
        83.73211,
        82.40643,
        82.13883,
        82.12804,
        81.77384,
        81.77384,
        81.77384,
        81.77384,
        81.77384,
    ],
}

result_suggest = {
    "ids": [
        'молоко',
        'деньги',
        'чатгпт',
        'морген',
        'Ильназ',
    ],
}


def search_function(query):
    suggestions = [s for s in result_suggest["ids"] if query.lower() in s.lower()]
    return suggestions


# Интерфейс Streamlit
st.title("Поиск видео в Yappy от lyam")

# Поле поиска с подсказками
query = st_searchbox(
    search_function,
    key="search_query",
    placeholder="Введите запрос",
    label="Search video",
    clear_on_submit=False,
)

col1, col2, col3 = st.columns([1, 1, 2])
with col1:
    search_button = st.button("Search")
with col2:
    suggest_button = st.button("Suggest")
with col3:
    pass

# Обработка нажатия кнопки Search
if search_button and query:
    st.subheader("Результаты поиска")
    cols = st.columns(2)  # Создаем две колонки для размещения видео
    for idx, video_url in enumerate(result_search["ids"]):
        with cols[idx % 2]:  # Размещаем видео попеременно в колонках
            st.video(video_url, format="video/mp4", start_time=0)
            st.write(f"Score: {result_search['scores'][idx]}")
            st.write(f"[Link to video]({video_url})")

# Обработка нажатия кнопки Suggest
if suggest_button:
    st.subheader("Предложения")
    suggestions = result_suggest["ids"]
    st.write(", ".join(suggestions))
