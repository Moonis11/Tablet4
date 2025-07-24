# cart_utils.py
import streamlit as st

def init_cart():
    if "cart" not in st.session_state:
        st.session_state["cart"] = []

def add_to_cart(item):
    init_cart()
    st.session_state["cart"].append(item)

def get_cart():
    init_cart()
    return st.session_state["cart"]

def remove_from_cart(index):
    init_cart()
    if 0 <= index < len(st.session_state["cart"]):
        st.session_state["cart"].pop(index)

def clear_cart():
    st.session_state["cart"] = []
