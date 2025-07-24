import streamlit as st
from translate import init_language, language_selector_inline, tr
from theme_manager import apply_theme 


# Sahifa sozlamasi
st.set_page_config(page_title="Tablet AI", layout="centered")


# Tilni boshlang'ich o'rnatish
if "lang" not in st.session_state:
    st.session_state["lang"] = "uz"  # default til
    
# Tilni tanlash (asosiy selectbox)
language_selector_inline()
lang = st.session_state["lang"]



# 🌈 Glasmorphism va pastel ranglar + animatsiya + NanoClassic uyg‘un dizayni
st.markdown("""
<style>
body {
    background: linear-gradient(145deg, #e0c3fc, #8ec5fc, #a1c4fd, #d4fc79);
    font-family: 'Segoe UI', sans-serif;
    margin: 0;
    padding: 0;
}

.glass-container {
    background: rgba(255, 255, 255, 0.12);
    border-radius: 20px;
    padding: 40px 30px;
    max-width: 650px;
    margin: 80px auto;
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.25);
    text-align: center;
    color: #fff;
    animation: fadeIn 0.8s ease-in-out;
    border: 1px solid rgba(255,255,255,0.3);
}

h1 {
    font-size: 38px;
    margin-bottom: 12px;
    color: #ffffff;
    text-shadow: 1px 1px 2px #000;
}

p {
    font-size: 19px;
    margin-bottom: 25px;
    color: white;
}

.button-row {
    display: flex;
    flex-wrap: wrap;
    gap: 15px;
    justify-content: center;
    margin-top: 25px;
}

button {
    background-color: rgba(255, 255, 255, 0.3);
    border: 2px solid #ffffff;
    padding: 14px 30px;
    font-size: 18px;
    font-weight: 600;
    border-radius: 12px;
    cursor: pointer;
    color: #ffffff;
    #text-shadow: 1px 1px 2px #000;
    transition: all 0.3s ease;
}

button:hover {
    background-color: rgba(255, 255, 255, 0.6);
    color: #222;
}

@keyframes fadeIn {
    from {opacity: 0; transform: translateY(20px);}
    to {opacity: 1; transform: translateY(0);}
}
</style>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="glass-container">
    <h1>{tr("title", lang)}</h1>
    <p>{tr("desc", lang)}</p>
</div>
""", unsafe_allow_html=True)

# 🔘 3 ta tugma (image / voice / manual), tarjima bilan
col1, col2, col3 = st.columns(3)

with col1:
    if st.button(tr("upload_image", lang)):
        st.session_state["mode"] = "image"
        st.switch_page("app.py")

with col2:
    if st.button(tr("voice_input", lang)):
        st.session_state["mode"] = "voice"
        st.switch_page("app.py")

with col3:
    if st.button(tr("manual_input", lang)):
        st.session_state["mode"] = "manual"
        st.switch_page("app.py")
apply_theme()