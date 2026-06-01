import streamlit as st

st.page_link("Homepage.py",label="Home")

st.title("Financial Dashboard")

st.page_link("pages/AI_Market_Summary.py",label= "AI Market Summary")
st.page_link("pages/AI_Sentiment_Analysis.py",label="AI Sentiment Analysis")
st.page_link("pages/Backtesting_Engine.py",label="Backtesting Engine")
st.page_link("pages/Market_Dashboard.py", label = "Market Dashboard")
st.page_link("pages/News_Aggregator.py",label="News Aggregator")
st.page_link("pages/Portfolio_Tracker.py",label="Portfolio Tracker")




