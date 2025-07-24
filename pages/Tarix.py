import streamlit as st
import pandas as pd
from datetime import datetime
from app import transliterate_to_cyrillic, get_base64_image
from theme_manager import apply_theme
from translate import tr, languages, language_selector_inline
from utils import load_history, save_history

apply_theme()
lang = st.session_state.get("lang", "uz")
st.set_page_config(page_title="📜 " + tr("history_title", lang), layout="centered")
st.title("📜 " + tr("history_title", lang))


# Fayldan tarixni o‘qish
if "history" not in st.session_state:
    st.session_state["history"] = load_history()

# CSV yuklash
try:
    apteka_df = pd.read_csv("apteka.csv")
    apteka_df.columns = apteka_df.columns.str.strip()
except Exception:
    st.error(tr("csv_load_error", lang))
    apteka_df = pd.DataFrame()

def get_price_from_apteka(nomi: str):
    if apteka_df.empty or not isinstance(nomi, str):
        return None
    apteka_df['Dori nomi'] = apteka_df['Dori nomi'].astype(str).str.strip().str.lower()
    nomi_lower = nomi.strip().lower()
    row = apteka_df[apteka_df['Dori nomi'] == nomi_lower]
    if not row.empty:
        for col in ['Narxi (taxminiy)', 'Narxi', 'Narx']:
            if col in apteka_df.columns:
                try:
                    return int(str(row.iloc[0][col]).replace(" ", "").replace(",", ""))
                except:
                    return None
    return None

# Tarixni yuklab olish
if "history" not in st.session_state:
    st.session_state["history"] = load_history()

# Faqat rasm/ovozli tarix
filtered_history = [
    item for item in st.session_state.history
    if item.get("type") in ["image", "voice"]
]

if not filtered_history:
    st.info(tr("no_history", lang))
    st.stop()

# Piktogrammalar
drug_icon = get_base64_image("images/drug_icon.png")
price_icon = get_base64_image("images/price_icon.png")
clock_icon = get_base64_image("images/clock_icon.png")

# ✅ Sahifalash
items_per_page = 7
current_page = st.session_state.get("cheap_page", 0)
start_idx = current_page * items_per_page
end_idx = start_idx + items_per_page
total_pages = (len(filtered_history) - 1) // items_per_page + 1
paged_history = filtered_history[::-1][start_idx:end_idx]

# Tarix ko‘rsatish
for idx, item in enumerate(paged_history):
    result = item.get("result", [])
    nomi = result[0] if result else tr("unknown", lang)
    vaqt = item.get("vaqt", datetime.now())
    narx_apteka = get_price_from_apteka(nomi)
    narx = narx_apteka if narx_apteka else item.get("tanlangan_narx", tr("unknown", lang))
    narx_formatted = f"{int(narx):,}".replace(",", " ") if isinstance(narx, (int, float)) else str(narx)

    with st.container():
        st.markdown("<div style='margin-top: 30px; margin-bottom: 30px;'></div>", unsafe_allow_html=True)  # ⬅️ margin: yuqoridan va pastdan 10px

        cols = st.columns([1, 6, 1])
        with cols[0]:
            st.markdown(f"<img src='data:image/png;base64,{drug_icon}' width='42'>", unsafe_allow_html=True)
        with cols[1]:
            st.markdown(f"""
                <div style="color:#ffffff;font-size:18px;font-weight:600">{nomi}</div>
                <div style="color:#00cc44;">
                    <img src='data:image/png;base64,{price_icon}' width='16'/> {narx_formatted} {tr("currency", lang)}
                </div>
                <div style="color:#bbbbbb;font-size:12px;">
                    <img src='data:image/png;base64,{clock_icon}' width='14'/> {vaqt.strftime("%Y-%m-%d %H:%M:%S")}
                </div>
            """, unsafe_allow_html=True)
        with cols[2]:    
            if st.button("❌", key=f"del_{idx}_{start_idx}"):
                st.session_state.history.pop(start_idx + idx)  # Indeksni to‘g‘rilash!
                save_history(st.session_state["history"])     # 👉 BU YER QO‘SHILDI
                st.rerun()


# Sahifa tugmalari
col1, col2, col3, col4, col5, col6 = st.columns([2.1, 1, 2, 0.5, 1.7, 1])

with col2:
    if st.button("⬅️", key="prev_btn") and current_page > 0:
        st.session_state["cheap_page"] -= 1
        st.rerun()

with col3:
    st.markdown(
        f"<div style='text-align: center; font-size: 18px;'><b>{current_page + 1} / {total_pages}</b></div>",
        unsafe_allow_html=True
    )

with col5:
    if st.button("➡️", key="next_btn") and current_page < total_pages - 1:
        st.session_state["cheap_page"] += 1
        st.rerun()

# Asosiy sahifaga qaytish
center_col = st.columns(5)[2]
with center_col:
    if st.button("🏠 " + tr("home", lang)):
        st.switch_page("app.py")
