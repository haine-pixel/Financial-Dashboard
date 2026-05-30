import streamlit as st
import plotly.graph_objects as go
from alpha_vantage.timeseries import TimeSeries
import pandas as pd
import os
from dotenv import load_dotenv

st.set_page_config(layout='wide')
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
toggle_container = st.container(border = False)
toggle_column1, toggle_column2, toggle_column3 = toggle_container.columns(3)

with toggle_column1:
    ma20 = st.toggle("MA20")
with toggle_column2:
    rsi_toggle = st.toggle("RSI")
with toggle_column3:
    macd = st.toggle("MACD")


if rsi_toggle:
    col1, col2 = st.columns([1, 1])
else:
    col1 = st.container()
    col2 = None
with col1:
    if dashboard_button:
        if ticker_name:
            try:
                data, metadata = get_ticker_data(time_period, ticker_name)
                st.session_state.ticker_data = data
            except Exception as e:
                st.error(f"Could not fetch data: {e}")
        else:
            st.error("Please input ticker name.")
    
    if 'ticker_data' in st.session_state:
        data = st.session_state['ticker_data']
        if data.shape[0] == 0:
            st.error("Rate limited, try again later.")
        else:
            x = time_period_dict[time_period]
            graph_data = data.head(x)[::-1]
            fig = go.Figure(data = [go.Candlestick(x=graph_data.index,open=graph_data["1. open"],high=graph_data["2. high"],low=graph_data["3. low"],close=graph_data["4. close"],name="")])
            if ma20:
                ma20_value = graph_data["4. close"].rolling(window = 20).mean()  
                fig.add_traces([go.Scatter(x=graph_data.index,y=ma20_value,name = "")])
                fig.update_layout(showlegend = False)
            st.plotly_chart(fig)       
    if rsi_toggle and col2:
        with col2:
            delta = graph_data["4. close"].diff()
            average_gain = delta.clip(lower=0).rolling(14).mean()
            average_loss = -delta.clip(upper=0).rolling(14).mean()
            rsi = 100 - (100/(1+(average_gain/average_loss)))
            fig1 = go.Figure(data = [go.Scatter(x=graph_data.index,y=rsi,name= "RSI")])
            st.plotly_chart(fig1)
