import streamlit as st
import bcrypt
import json
from pathlib import Path
from datetime import datetime , date
from alpha_vantage.timeseries import TimeSeries
import os
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


load_dotenv()
alpha_key = os.getenv("ALPHA_VANTAGE_KEY")
ts = TimeSeries(key=alpha_key, output_format='pandas')

@st.cache_data
def get_ticker_data(ticker_name):
    data,meta_data = ts.get_daily(ticker_name,outputsize="compact")
    return data, meta_data
    
def clear_text():
    st.session_state["saved_name"] = st.session_state["add_stock_name"]
    st.session_state["saved_amount"] = st.session_state["add_stock_amount"]
    st.session_state["saved_value"] = st.session_state["add_stock_value"]
    st.session_state["add_stock_name"] = ""
    st.session_state["add_stock_amount"] = ""
    st.session_state["add_stock_value"] = ""
#setting up of page    
st.set_page_config(layout='wide')
st.page_link("Homepage.py",label="Home")
st.title("Portfolio Tracker")
file_path = Path(__file__).parent.parent.parent / "data" / "sample.json"
file_path.parent.mkdir(parents=True, exist_ok=True)
if file_path.exists():
    with open(file_path,"r") as f:
        data = json.load(f)
else:
    with open(file_path,"w") as f:
        json.dump({},f)
        data = {}
        
if "login" not in st.session_state:
    st.session_state["login"] = False

#login page
if not st.session_state["login"]:

    user_name = st.text_input("Username")
    user_pass = st.text_input("Password",type="password")
    register_button = st.button("Register")
    login_button = st.button("Login")
# registration of user
    if register_button:
        if user_name not in data:
            bytes = user_pass.encode('utf-8')
            salt = bcrypt.gensalt()
            hash = bcrypt.hashpw(bytes,salt)
            hash = hash.decode('utf-8')
            data[f"{user_name}"] ={
                    "password":hash,
                    "stock_data":{}
            }
            json_str = json.dumps(data,indent=3)
            with open(file_path,"w") as f:
                f.write(json_str)
            st.write("Registration successful.")
        else:
            st.write("Username is in use.")

#login logic
    if login_button:
            if user_name in data:
                userBytes = user_pass.encode('utf-8')
                hash = data[f"{user_name}"]["password"].encode('utf-8')
                result = bcrypt.checkpw(userBytes,hash)
                if result:
                    st.session_state["login"] = True
                    st.session_state["user_name"] = user_name
                    st.rerun()
                else:
                    st.write("login failed, please ensure username and password is correct")
                    login = False
            else:
                st.write("Username not found, Please register")

else:
    logout_button = st.button("Log out")
    if logout_button:
        st.session_state["login"] = False
        st.rerun()
        
# Code for input of stock data
    search_container = st.container()
    scol1,scol2,scol3,scol4 = search_container.columns([5,2,2,1],vertical_alignment="bottom",)
    with scol1:
        add_stock_name = st.text_input("Stock Ticker:",key="add_stock_name")
    with scol2:
        add_stock_amount = st.text_input("Amount of Stock:",key="add_stock_amount")
    with scol3:
        add_stock_value = st.text_input("Price of Stock",key="add_stock_value")
    with scol4:
        add_stock_button = st.button("Add Stock", on_click=clear_text)
    if add_stock_button:
        stock_data = data[st.session_state["user_name"]]["stock_data"]
        if st.session_state.saved_name not in stock_data:
            stock_data[st.session_state.saved_name] = {}
        stock_data[st.session_state.saved_name][str(datetime.today().strftime("%Y-%m-%d %H:%M:%S"))] = {
        "amount": st.session_state.saved_amount,
        "price": st.session_state.saved_value
        }
        json_str = json.dumps(data,indent=3)
        with open(file_path,"w") as f:
            f.write(json_str)

#Code for Stock Information
    st.divider()
    top_container = st.container()
    tcol1,tcol2,tcol3,tcol4 = top_container.columns(4,border=True)
    
#calculation for portfolio data
    personal_stock_data = data[st.session_state.user_name]["stock_data"]
    total_stock_value = 0
    total_profit = 0
    total_amount_invested = 0
    total_number_of_stocks_held = 0
    personal_stock_data_values = []
    personal_stock_data_labels = []
    personal_stock_data_gains = []
    graph_data = {}
    for stocks in personal_stock_data:
        x_stock_value = 0
        x_stock_gain = 0
        ticker_data,meta_data = get_ticker_data(stocks)
        latest_price = ticker_data["4. close"].values[0]
        for key, values in personal_stock_data[stocks].items():
            amount = float(values["amount"])
            price = float(values["price"])
            total_stock_value += float(amount * latest_price)
            total_profit += ((latest_price-price)*amount)
            total_amount_invested += (amount * price)
            total_number_of_stocks_held += amount
            x_stock_value += float(amount*latest_price)
            x_stock_gain += ((latest_price-price)*amount)
        personal_stock_data_values.append(x_stock_value)
        personal_stock_data_labels.append(stocks)
        personal_stock_data_gains.append(x_stock_gain)
    graph_data ={
        "stock_name": personal_stock_data_labels,
        "allocation": personal_stock_data_values,
        "gains": personal_stock_data_gains
    }
    
    graph_df = pd.DataFrame(graph_data)
    
    with tcol1:
        st.write(f"Total Stock Value: ${total_stock_value:.2f}")
    with tcol2:
        st.write(f"Total Profits: ${total_profit:.2f}")
    with tcol3:
        st.write(f"Total Amount Invested: ${total_amount_invested:.2f}")
    with tcol4:
        st.write(f"Number of Stocks Held: {int(total_number_of_stocks_held)}")
        
    
    bottom_container = st.container()
    bcol1,bcol2 = bottom_container.columns(2,border=True)
    with bcol1:
        st.write("Portfolio Pie Chart")
        fig, ax = plt.subplots()
        cmap_colors = plt.cm.Pastel2.colors 
        ax.pie(personal_stock_data_values, labels=personal_stock_data_labels,textprops={'color': 'white'}, autopct='%1.1f%%', startangle=90,colors=cmap_colors)
        ax.axis('equal')
        fig.patch.set_facecolor('none')
        st.pyplot(fig)
        
    with bcol2:
        st.write("Portfolio information: Value/Invested, Gains, Allocation")
        y = np.arange(len(personal_stock_data_labels))
        height = 0.35
        fig, ax = plt.subplots(figsize=(10, 6))

        rects1 = ax.barh(y + height/2, personal_stock_data_gains, height, label='Gains', color='#1f77b4')

        rects2 = ax.barh(y - height/2, personal_stock_data_values, height, label='Allocation', color='#ff7f0e')

        ax.set_yticks(y)
        ax.set_yticklabels(personal_stock_data_labels,color="white")
        ax.legend()

        ax.bar_label(rects1, padding=3,color ="white")
        ax.bar_label(rects2, padding=3,color ="white")
        for spine in ax.spines.values():
            spine.set_visible(False)
        fig.patch.set_facecolor('none')
        ax.patch.set_facecolor('none')
        plt.tight_layout()

        st.pyplot(fig)
   

