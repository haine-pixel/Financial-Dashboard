import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()
news_api=os.getenv("THENEWSAPI_KEY")

def get_news_data():
    selected_category = st.session_state["selected_category"]
    response = requests.get(f"https://api.thenewsapi.com/v1/news/all?categories={selected_category}&api_token={news_api}&language=en&")
    data = response.json()
    st.session_state.news_data = data


st.page_link("Homepage.py",label="Home")
st.title("News Aggregator")
category_container = st.container()
cat_col_1,cat_col_2,cat_col_3,cat_col_4,cat_col_5,cat_col_6 = category_container.columns(6)
with cat_col_1:
    general = st.button("General")
with cat_col_2:
    science = st.button("Science")
with cat_col_3:
    business = st.button("Business")
with cat_col_4:
    healthcare = st.button("Healthcare")
with cat_col_5:
    tech = st.button("Technology")
with cat_col_6:
    politics = st.button("Politics")

if general:
    st.session_state.selected_category ="general"
    get_news_data()
if science:
    st.session_state.selected_category ="science"
    get_news_data()
if business:
    st.session_state.selected_category ="business"
    get_news_data()
if healthcare:
    st.session_state.selected_category ="health"
    get_news_data()
if tech:
    st.session_state.selected_category ="tech"
    get_news_data()
if politics:
    st.session_state.selected_category ="politics"
    get_news_data()
    

if "selected_category" in st.session_state:
    selected_category = st.session_state["selected_category"]
    st.header(f"{selected_category.title()}")
    st.divider()
if "news_data" in st.session_state:
    data = st.session_state["news_data"]
    news_data = data["data"]
    for id, items in enumerate(news_data):
        if id%3 ==0:
            cols = st.columns(3)
        with cols[id%3]:
            with st.container(border=True):
                st.markdown(f"<a href='{items['url']}' style='color: white; text-decoration: none;'><h3>{items['title']}</h3></a>", unsafe_allow_html=True)
                st.text(items["description"])
                st.image(items["image_url"],width=440)
                st.text(f"Source: {items['source']}")

