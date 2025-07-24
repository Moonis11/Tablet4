import streamlit as st
from theme_manager import apply_theme
from translate import tr
from streamlit_extras.switch_page_button import switch_page

apply_theme()

st.set_page_config(page_title=tr("cart_page", st.session_state.get("lang", "uz")), layout="centered")

lang = st.session_state.get("lang", "uz")
st.title(tr("your_cart", lang))

cart = st.session_state.get("cart", [])

# 🔴 Agar cart bo‘sh bo‘lsa
if not cart:
    st.warning(tr("empty_cart", lang))
    if st.button(tr("new_order", lang)):
        st.session_state.clear()
        switch_page("pages/home.py")
    st.stop()

# Narx jamlash
total = 0
remove_indices = []

def format_distance(km):
    return f"{km:.1f} km"

# 🔁 Har bir mahsulot uchun ko‘rsatish
for idx, item in enumerate(cart):
    with st.container():
        col1, col2 = st.columns([4, 1.5])
        with col1:
            dorixona = item.get("dorixona", tr("unknown", lang))
            if isinstance(dorixona, set):
                dorixona_nomi = list(dorixona)[0]
            else:
                dorixona_nomi = dorixona

            masofa = item.get("masofa_km")
            location_text = format_distance(masofa) if masofa else tr("unknown", lang)

            narx = item.get("narx", 0)
            total += narx

            st.markdown(f"""
                <div class='glass'>
                <strong>{idx+1}. {item.get("dori_nomi", "Nomaʼlum").capitalize()}</strong><br>
                💰 {tr("price", lang)}: {narx:,} {tr("currency", lang)}<br>
                🏥 {tr("pharmacy", lang)}: {dorixona_nomi}<br>
                {tr("distance", lang)}: {location_text}<br>
                📅 {tr("expiry_date", lang)}: {item.get("yaroqlik_muddati", tr("unknown", lang))}<br>
                📦 {tr("in_stock", lang)}: {item.get("omborda_mavjud", tr("unknown", lang))}<br>
                </div>
            """, unsafe_allow_html=True)

        with col2:
            if st.button("❌", key=f"remove_{idx}"):
                cart.pop(idx)
                st.session_state["cart"] = cart
                st.rerun()  # s

# ❌ O‘chirish (oxiridan boshlab)
for i in sorted(remove_indices, reverse=True):
    cart.pop(i)

st.session_state["cart"] = cart

# Umumiy narx
st.markdown(f"### ✔️ {tr('total', lang)}: **{total:,} {tr('currency', lang)}**")

col1, col2 = st.columns(2)
with col1:
    if st.button("⬅️ " + tr("go_home", lang)):
        switch_page("pages/home")

with col2:
    if st.button("✅ " + tr("go_payment", lang)):
        switch_page("pages/pay.py")
