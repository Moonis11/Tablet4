# theme_manager.py

import streamlit as st

# theme.py

def get_theme_css(mode="dark"):
    if mode == "dark":
        background = "#0d1117"
        text_color = "#f0f0f0"
        box_bg = "rgba(255, 255, 255, 0.08)"
        border_color = "#30363d"
        hover_bg = "#274669"
    else:
        background = "#f2f6fe"
        text_color = "#5976AA"
        box_bg = "#8dbd7f"
        border_color = "#2A7E27"
        hover_bg = +"#5fe213"
        

    return f"""
    <style>
    html, body, .stApp {{
        background-color: {background} !important;
        color: {text_color} !important;
        font-family: Consolas, 'Courier New', monospace;
        font-weight = bold !important;
    }}

    .stButton > button {{
        background-color: {box_bg};
        color: {text_color};
        border: 2px solid {border_color};
        border-radius: 30px;
        padding: 8px 10px;
    }}
    .stButton > button:hover {{
        background: {hover_bg} !important;
        color: {text_color} !important;
        border: 2px solid {border_color} !important;
        cursor: pointer;
    }}


    .glass, .order-box, .info-box {{
        background-color: {box_bg};
        color: {text_color};
        border: 1px solid {border_color};
        border-radius: 16px;
        padding: 10px;
        margin-bottom: 18px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
        font-size = 16px
    }}

    .stTextInput > div > input,
    .stTextArea > div > textarea {{
        background: {box_bg};
        color: {text_color};
        border: 1px solid {border_color};
        border-radius: 8px;
        padding: 8px;
    }}

       /* 🔽 Input, textarea styling */
    input, textarea {{
        background-color: {box_bg} !important;
        color: {text_color} !important;
        border: 1px solid {border_color} !important;
        font-weight: bold !important;
        font-family: Consolas, monospace !important;
    }}

    input:focus, textarea:focus {{
        border-color: {hover_bg} !important;
        outline: none !important;
    }}

    /* 🔽 Streamlit components */
    .stTextInput > div > input,
    .stTextArea > div > textarea {{
        background-color: {box_bg} !important;
        color: {text_color} !important;
        border: 1px solid {border_color} !important;
        border-radius: 8px;
        padding: 8px;
        font-family: Consolas, monospace !important;
        font-weight: bold !important;
    }}

    .stSelectbox div[role="combobox"] {{
        background-color: {background} !important;
        color: {text_color} !important;
    }}

    .stSidebar, .stSidebarContent {{
        background-color: {background};
        color: {text_color};
    }}
    /* Barcha tugmalar (shu jumladan form submit) uchun */
    .stbutton > button {{
        background-color: {box_bg} !important;
        color: {text_color} !important;
        border: 2px solid {border_color} !important;
        border-radius: 20px !important;
        padding: 5px 10px !important;
        font-weight: bold !important;
        font-family: 'Consolas', monospace !important;
        transition: all 0.3s ease;
    }}

    .stbutton > button:hover {{
        background-color: {hover_bg} !important;
        color: {text_color} !important;
        cursor: pointer;
        box-shadow: 0 0 10px rgba(0,0,0,0.2);
    }}
    st.form_submit_button{{
        background-color: {hover_bg} !important;
        color: {text_color} !important;
        cursor: pointer;
        box-shadow: 0 0 10px rgba(0,0,0,0.2);
    }}
        .custom-container {{
         background-color: #ffffff !important;
        color: #000000 !important;
        padding: 20px;
        border-radius: 20px;
        font-size: 18px;
        display: flex;
        align-items: center;
        margin-bottom: 15px;
    }}
    
    </style>
    """



def apply_theme():
    if "theme_mode" not in st.session_state:
        st.session_state["theme_mode"] = "dark"

    with st.sidebar:
        theme = st.radio("🎨 Rejimni tanlang", ["dark", "light"],
                         index=0 if st.session_state["theme_mode"] == "dark" else 1)
        if theme != st.session_state["theme_mode"]:
            st.session_state["theme_mode"] = theme
            st.rerun()

    st.markdown(get_theme_css(st.session_state["theme_mode"]), unsafe_allow_html=True)
