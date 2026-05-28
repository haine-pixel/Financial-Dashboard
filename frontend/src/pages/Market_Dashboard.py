import streamlit as st
import plotly.graph_objects as go
from alpha_vantage.timeseries import TimeSeries
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()
alpha_key = os.getenv("ALPHA_VANTAGE_KEY")
ts = TimeSeries(key=alpha_key, output_format='pandas')

st.page_link("Homepage.py",label="Home")
st.title("Market Dashboard")

ticker_name = st.text_input(label="Ticker Name")
time_period = st.selectbox("Time Period",["1d","5d","1mo","3mo","6mo","1y","2y","5y"])

dashboard_button = st.button(label="Search",key="dashboard_button")

if dashboard_button:
    if ticker_name:
        try:
            data, meta_data = ts.get_daily(ticker_name,outputsize='compact')
            if data.shape[0] == 0:
                st.error("Rate limited, try again later.")
            else:
                fig = go.Figure(data = [go.Candlestick(x=data.index,open=data["1. open"],high=data["2. high"],low=data["3. low"],close=data["4. close"])])
                st.plotly_chart(fig)
        except Exception as e:
            st.error(f"Could not fetch data: {e}")
    else:
        st.error("Please input ticker name.")

        