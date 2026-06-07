import streamlit as st
import bcrypt
import json
from pathlib import Path
from datetime import datetime , date

def clear_text():
    st.session_state["saved_name"] = st.session_state["add_stock_name"]
    st.session_state["saved_amount"] = st.session_state["add_stock_amount"]
    st.session_state["saved_value"] = st.session_state["add_stock_value"]
    st.session_state["add_stock_name"] = ""
    st.session_state["add_stock_amount"] = ""
    st.session_state["add_stock_value"] = ""
    
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
    
if not st.session_state["login"]:

    user_name = st.text_input("Username")
    user_pass = st.text_input("Password",type="password")
    register_button = st.button("Register")
    login_button = st.button("Login")
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
            
            
    st.divider()
    top_container = st.container()
    tcol1,tcol2,tcol3,tcol4 = top_container.columns(4,border=True)
    with tcol1:
        st.write("Total Stock Value")
    with tcol2:
        st.write("Total Profit")
    with tcol3:
        st.write("Placeholder")
    with tcol4:
        st.write("Placeholder")
    bottom_container = st.container()
    bcol1,bcol2 = bottom_container.columns(2,border=True)
    with bcol1:
        st.write("Portfolio Pie Chart")
    with bcol2:
        st.write("Portfolio information: Value/Invested, Gains, Allocation")
        
    