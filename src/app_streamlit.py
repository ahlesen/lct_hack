import streamlit as st
import requests
from typing import Dict

HOST: str = 'http://localhost:8080'
ENDPOINT_SEARCH_URL :str = f'{HOST}/search'
ENDPOINT_SUGGEST_URL :str = f'{HOST}/suggest'
HEADERS : Dict[str,str]  = {
    'accept': 'application/json',
    'Content-Type': 'application/json',
}

# Интерфейс Streamlit
st.title("Поиск видео в Yappy от lyam")

# Поле поиска и кнопки
search_query = st.text_input("Введите запрос")

col1, col2, col3 = st.columns([1, 1, 2])
with col1:
    search_button = st.button("Search")
with col2:
    suggest_button = st.button("Suggest")
with col3:
    pass

# Обработка нажатия кнопки Search
if search_button:
    params = {
        'text': search_query,
    }
    response = requests.get(ENDPOINT_SEARCH_URL, params=params, headers=HEADERS)
    if response.status_code == 200:
        result_search = response.json()
        st.subheader("Результаты поиска")
        cols = st.columns(2)  # Создаем две колонки для размещения видео
        for idx, video_url in enumerate(result_search["ids"]):
            with cols[idx % 2]:  # Размещаем видео попеременно в колонках
                st.video(video_url, format="video/mp4", start_time=0)
                st.write(f"Score: {result_search['scores'][idx]}")
                st.write(f"[Link to video]({video_url})")
    else:
        st.subheader(
            f"Проблемы с поиском, напишите разработчикам | status_code = {response.status_code} | error: {response.text}"
        )


# Обработка нажатия кнопки Suggest
if suggest_button:
    params = {
        'text': search_query,
    }
    response = requests.get(ENDPOINT_SUGGEST_URL, params=params, headers=HEADERS)
    if response.status_code == 200:
        result_suggest = response.json()
        st.subheader("Подсказки")
        suggestions = result_suggest['suggests']
        st.write(", ".join(suggestions))
    else:
        st.subheader(
            f"Проблемы с подсказками, напишите разработчикам | status_code = {response.status_code} | error: {response.text}"
        )
