# pages/order.py

import streamlit as st
import csv
from datetime import datetime
from theme_manager import apply_theme
from translate import tr, init_language  # Tarjimani yuklaymiz

# --- Tilni boshlang‘ich holatda sozlash
init_language()
lang = st.session_state.get("lang", "uz")

# --- Sahifa sozlamalari va tema
st.set_page_config(page_title=tr("order_completed_title", lang), layout="centered")
apply_theme()

# --- Sarlavha
st.title(tr("order_completed_title", lang))

# --- Sessionda kerakli kalitlar mavjudligini tekshirish
req_keys = [
    "order_id", "name", "phone", "drug_name", "drug_price",
    "delivery_fee", "logistics_fee", "smart_service", "total", "location"
]
if not all(k in st.session_state for k in req_keys):
    st.error(tr("not_enough_data", lang))
    st.stop()

# --- Sessiondan qiymatlarni olish
order_id      = st.session_state["order_id"]
name          = st.session_state["name"]
phone         = st.session_state["phone"]
location      = st.session_state["location"]
drug_name     = st.session_state["drug_name"]
drug_price    = st.session_state["drug_price"]
delivery_fee  = st.session_state["delivery_fee"]
logistics_fee = st.session_state["logistics_fee"]
smart_service = st.session_state["smart_service"]
profit        = logistics_fee + smart_service
total         = st.session_state["total"]
currency      = tr("currency", lang)
now           = datetime.now().strftime("%Y-%m-%d %H:%M")

# --- Buyurtma CSV faylga yoziladi
# --- Buyurtma CSV faylga yoziladi — faqat bir marta
if not st.session_state.get("order_saved_flag", False):
    import os
    import csv

    file_path = "order21.csv"

    if not os.path.exists(file_path):
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "order_id", "ism", "telefon", "dorilar", "dori_narxi",
                "delivery_fee", "logistics_fee", "smart_service",
                "tablet_profit","umumiy_narx",  "manzil", "sana"
            ])

    with open(file_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            order_id, name, phone, drug_name, drug_price,
            delivery_fee, logistics_fee, smart_service,
            total, profit, location, now
        ])

    st.session_state["order_saved_flag"] = True

# ✅ Buyurtma saqlandi xabari
st.success(tr("order_saved", lang))

# --- Buyurtma tafsilotlari
st.markdown("---")
st.info(f"""
🆔 **{tr('order_id', lang)}:** `{order_id}`  
👤 **{tr('user', lang)}:** {name}  
 **{tr('phone', lang)}:** {phone}  
📍 **{tr('address', lang)}:** {location}  
💊 **{tr('drug', lang)}:** {drug_name}  
 **{tr('total_pay', lang)}:** {total:,} {currency}
""")

# --- Yangi buyurtma tugmasi
col_center = st.columns([1, 2, 1])[1]
with col_center:
    if st.button(tr("new_order", lang), use_container_width=True, key="new_order_btn"):
        st.session_state.clear()
        st.switch_page("pages/home.py")
