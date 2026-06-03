import streamlit as st
import bcrypt
import json
from pathlib import Path

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
                st.write("Login Successful")
            else:
                st.write("login failed, please ensure username and password is correct")
        else:
            st.write("Username not found, Please register")
