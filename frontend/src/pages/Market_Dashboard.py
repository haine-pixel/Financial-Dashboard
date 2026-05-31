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

def draw_macd_graph(data):
    macd_multiplier_values = {
    "12": 2/13,
    "26": 2/27
    }
    ema_values = {
        "9": float(0),
        "12":float(data["4. close"].head(int(12)).mean()),
        "26":float(data["4. close"].head(int(26)).mean()),
    }
    macd_point_list = []
    signal_point_list = []
    histogram_point_list = []
    for x in data["4. close"]:
        for key,values in macd_multiplier_values.items():
            
            base_value = ema_values[key]
            new_value = x
            base_value = (new_value*values)+(base_value*(1-values))
            ema_values[key] = float(base_value)
        macd_point = float(ema_values["12"]) - float(ema_values["26"])
        macd_point_list.append(macd_point)
    for y in macd_point_list:
        if ema_values["9"] == 0:
            base_signal_value = 0
        else:
            base_signal_value = ema_values["9"]
        new_signal_value = y
        if base_signal_value == 0:
            base_signal_value = new_signal_value
        else:
            base_signal_value = (float(new_signal_value*0.2) + float(base_signal_value*0.8))
        ema_values["9"] = base_signal_value
        signal_point_list.append(base_signal_value)
    histogram_point_list = [a-b for a,b in zip(macd_point_list,signal_point_list)]
    fig2 = go.Figure(data = [go.Bar(x=data.index,y=histogram_point_list,name="hist")])
    fig2.add_traces([go.Scatter(x=data.index,y=signal_point_list,name = "Signal Line")])
    fig2.add_traces([go.Scatter(x=data.index,y=macd_point_list,name= "MACD Line")])
    fig2.update_layout(dragmode='pan',title="MACD")
    st.plotly_chart(fig2,config={"scrollZoom":True})

def draw_rsi_graph(data,toggle_column,column):        
    with toggle_column:
        toggle70 = st.toggle("overbought line")
        toggle30 = st.toggle("oversold line")
    with column:
        delta = data["4. close"].diff()
        average_gain = delta.clip(lower=0).rolling(14).mean()
        average_loss = -delta.clip(upper=0).rolling(14).mean()
        rsi = 100 - (100/(1+(average_gain/average_loss)))
        fig1 = go.Figure(data = [go.Scatter(x=data.index,y=rsi,name= "RSI")])
        if toggle70:
            fig1.add_hline(y=70,line_color='green')
        if toggle30:
            fig1.add_hline(y=30,line_color='red')
        fig1.update_layout(dragmode='pan',title="RSI")
        st.plotly_chart(fig1,config={"scrollZoom": True})

st.page_link("Homepage.py",label="Home")
st.title("Market Dashboard")

ticker_name = st.text_input(label="Ticker Name")
time_period = st.selectbox("Time Period",["1d","5d","1mo","3mo","6mo","1y","2y","5y"])

dashboard_button = st.button(label="Search",key="dashboard_button")
toggle_container = st.container(border = False)
toggle_column1, toggle_column2, toggle_column3 = toggle_container.columns(3)

ma20=False
rsi_toggle=False

with toggle_column1:
    if time_period in time_period_list[:2]:
        ma20 = st.toggle("MA20",disabled = True, help="Requires at least 1 month of data")
    else:  
        ma20 = st.toggle("MA20")
with toggle_column2:
    if time_period in time_period_list[:2]:
        rsi_toggle = st.toggle("RSI",disabled = True, help="Requires at least 1 month of data")
    else:  
        rsi_toggle = st.toggle("RSI")
with toggle_column3:
    macd = st.toggle("MACD")

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
            fig.update_layout(showlegend = False,dragmode='pan')
        st.plotly_chart(fig,config={"scrollZoom": True})
        if rsi_toggle and not macd:
            draw_rsi_graph(data=graph_data,toggle_column=toggle_column2,column=st.container())
        if macd and not rsi_toggle:
            draw_macd_graph(data=graph_data)
        if rsi_toggle and macd:
            col1, col2 = st.columns([1, 1])          
            draw_rsi_graph(data=graph_data,toggle_column=toggle_column2,column=col1)
            with col2:
                draw_macd_graph(data=graph_data)

