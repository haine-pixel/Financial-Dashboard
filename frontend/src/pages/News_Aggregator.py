import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()
news_api=os.getenv("THENEWSAPI_KEY")

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

search = st.button("search")

category_list = ["science"]


if general:
    response = requests.get(f"https://api.thenewsapi.com/v1/news/all?categories=general&api_token={news_api}&language=en&")
    data = response.json()
    news_data = data["data"]
    cols = st.columns(len(news_data))
    for id, items in enumerate(news_data):
        with cols[id]:
                st.header(items["title"])
                st.text(items["description"])
                st.image(items["image_url"],width=440)
                st.text(items["source"])