import streamlit as st
import plotly.graph_objects as go
from alpha_vantage.timeseries import TimeSeries
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()
alpha_key = os.getenv("ALPHA_VANTAGE_KEY")
ts = TimeSeries(key=alpha_key, output_format='pandas')
time_period_list = ["1d","5d","1mo","3mo","6mo","1y","2y","5y"]
time_period_dict = {
    "1d": int(1),
    "5d": int(5),
    "1mo": int(30),
    "3mo": int(90),
    "6mo": int(180),
    "1y": int(365),
    "2y": int(730),
    "5y": int(1825)
}

@st.cache_data
def get_ticker_data(time_period,ticker_name):
    if time_period in time_period_list[:4]:
        data, meta_data = ts.get_daily(ticker_name,outputsize='compact')
    else:
        data, meta_data = ts.get_daily(ticker_name,outputsize='full')
    return data, meta_data

st.page_link("Homepage.py",label="Home")
st.title("Market Dashboard")

ticker_name = st.text_input(label="Ticker Name")
time_period = st.selectbox("Time Period",["1d","5d","1mo","3mo","6mo","1y","2y","5y"])

dashboard_button = st.button(label="Search",key="dashboard_button")

if dashboard_button:
    if ticker_name:
        try:
            data,metadata = get_ticker_data(time_period,ticker_name)
            if data.shape[0] == 0:
                st.error("Rate limited, try again later.")
            else:
                x = time_period_dict[time_period]
                graph_data = data.head(x)[::-1]
                fig = go.Figure(data = [go.Candlestick(x=graph_data.index,open=graph_data["1. open"],high=graph_data["2. high"],low=graph_data["3. low"],close=graph_data["4. close"])])
                st.plotly_chart(fig)
        except Exception as e:
            st.error(f"Could not fetch data: {e}")
    else:
        st.error("Please input ticker name.")

        