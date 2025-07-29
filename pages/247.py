import streamlit as st
import pandas as pd
import uuid
from streamlit_extras.switch_page_button import switch_page
from datetime import datetime
from translate import tr, languages, language_selector_inline
import re
from geopy.distance import geodesic
from math import radians, sin, cos, atan2, sqrt
import streamlit.components.v1 as components

from theme_manager import apply_theme
apply_theme()



# 🌐 Tilni tanlash (agar kerak bo‘lsa)
lang = st.session_state.get("lang", "uz")
import base64

# Button bilan `switch_page()` qo‘llash
col1, col2 = st.columns([8, 1])
with col2:
    if st.button("🛒", key="cart_button", help="Savatga o'tish"):
        st.switch_page("pages/savat.py")

# 🔘 3 ta tugma (image / voice / manual), tarjima bilan
col1, col2, col3 = st.columns(3)

with col1:
    if st.button(tr("upload_image", lang), use_container_width=True):
        st.session_state["mode"] = "image"
        st.switch_page("app.py")

with col2:
    if st.button(tr("voice_input", lang), use_container_width=True):
        st.session_state["mode"] = "voice"
        st.switch_page("app.py")

with col3:
    if st.button(tr("manual_input", lang), use_container_width=True):
        st.session_state["mode"] = "manual"
        st.switch_page("app.py")

# --- Tugmalarni chiqarish ---
with st.container():
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("📍 Yaqin", key="yaqin", use_container_width=True):
            st.switch_page("pages/locatsiya.py")
    with col2:
        if st.button("💸 Arzon", key="arzon", use_container_width=True):
            st.switch_page("pages/arzon.py")
    with col3:
        if st.button("🌙 24/7", key="kechaku", use_container_width=True):
            st.switch_page("pages/247.py")


# 📥 CSV faylni yuklash
df = pd.read_csv("APTEKA.csv")
# ✅ Savatni boshlash (agar yo‘q bo‘lsa)
if "cart" not in st.session_state:
    st.session_state["cart"] = []

# 🔍 24/7 kalit so‘zlar
kalit_sozlar = ["24/7", "doimiy", "kruglosutochno", "24-soat", "24 soat", "har kuni 24", "24 soat davomida ochiq"]

# ✅ Ish vaqti ustunini topish
for ustun_nomi in ["ish_vaqti", "Ish vaqti", "vaqti", "ishvaqti"]:
    if ustun_nomi in df.columns:
        ish_vaqti_ustun = ustun_nomi
        break
else:
    st.error("❌ CSV faylda ish vaqti ustuni topilmadi.")
    st.stop()

# ✅ 24/7 ishlaydiganlar
df_247 = df[df[ish_vaqti_ustun].astype(str).str.lower().apply(
    lambda x: any(k in x for k in kalit_sozlar)
)]
dori_raw = st.session_state.get("tanlangan_dori", {})
if isinstance(dori_raw, dict):
    dori_nomi = dori_raw.get("Dori nomi", "").lower()
else:
    dori_nomi = str(dori_raw).lower()


if not dori_nomi:
    st.warning("❗ Dori tanlanmagan.")
    st.stop()
df_247 = df_247[df_247["Dori nomi"].str.lower() == dori_nomi]


st.subheader("🟢 24/7 ishlaydigan dorixonalar")

if df_247.empty:
    st.warning("❗ 24/7 ishlaydigan dorixonalar topilmadi.")
    st.stop()

if "user_lat" in st.session_state and "user_lon" in st.session_state:
    user_lat = st.session_state["user_lat"]
    user_lon = st.session_state["user_lon"]

    def haversine(lat1, lon1, lat2, lon2):
        R = 6371
        dlat = radians(lat2 - lat1)
        dlon = radians(lon2 - lon1)
        a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
        return 2 * R * atan2(sqrt(a), sqrt(1 - a))

    # 👉 Faqat df_247 ni lokatsiyaga qarab tartiblash
    df_247 = df_247.dropna(subset=["Latitude", "Longitude"]).copy()
    df_247["masofa_km"] = df_247.apply(
        lambda row: haversine(user_lat, user_lon, row["Latitude"], row["Longitude"]),
        axis=1
    )

    # 👉 Eng yaqinidan boshlab sortirovka
    df_247 = df_247.sort_values("masofa_km", ascending=True)
else:
    st.warning("❗ Masofa bo‘yicha saralash uchun lokatsiya kerak.")

def clean_key(text):
        return re.sub(r'[^a-z0-9]', '', text.lower())
# ✅ Sahifalash
items_per_page = 7
total_pages = (len(df_247) - 1) // items_per_page + 1

if "cheap_page" not in st.session_state:
    st.session_state["cheap_page"] = 0

start_idx = st.session_state["cheap_page"] * items_per_page
end_idx = start_idx + items_per_page
page_df = df_247.iloc[start_idx:end_idx]
total = 0
from geopy.geocoders import Nominatim

def get_address_from_coords(lat, lon):
    try:
        geolocator = Nominatim(user_agent="tablet_app")
        location = geolocator.reverse((lat, lon), language="uz")
        if location:
            return location.address
        return "Manzil topilmadi"
    except Exception as e:
        return f"Xatolik: {e}"
    

for i, row in page_df.iterrows():
    dori_nomi = row.get("Dori nomi", "Nomaʼlum")
    narx_str = str(row.get("Narxi (taxminiy)", "0"))
    apteka = row.get("Apteka nomi", "Nomaʼlum")
    telefon_raw = row.get("Telefon", "")
    ish_vaqti = str(row.get(ish_vaqti_ustun, "")).strip()

    # Narxni tozalash
    narx_raw = row.get("Narxi (taxminiy)", row.get("Narxi", "0"))
    narx_str = str(narx_raw)
    try:
        narx = int(narx_str.replace(" ", "").replace("so‘m", "").replace(",", ""))
    except:
        narx = 0

    narx_formatted = f"{narx:,}".replace(",", " ")
    total += narx
        # Telefon
    try:
        telefon = str(int(float(telefon_raw)))
    except:
        telefon = "Nomaʼlum"

    # Vaqt label
    if any(k in ish_vaqti.lower() for k in kalit_sozlar):
        vaqt_label = "🕐 Doimiy (24/7)"
    else:
        vaqt_label = f"🕐 Ish vaqti: {ish_vaqti}"
    
     # Lat va Lon dan manzil olish
    lat = row.get("Latitude")
    lon = row.get("Longitude")
    manzil = get_address_from_coords(lat, lon) if lat and lon else "Manzil mavjud emas"

    # Agar sizda Latitude va Longitude mavjud bo‘lsa:
    from geopy.distance import geodesic
    foydalanuvchi_location = (41.3111, 69.2797)  # Toshkent markazi misolida
    apteka_location = (row["Latitude"], row["Longitude"])
    masofa = geodesic(foydalanuvchi_location, apteka_location).km
    yaroqlik_muddati = row.get("Yaroqlik muddati", "kiritilmagan")
    omborda_mavjud = row.get("Omborda mavjudligi", "aniqlanmagan")
    
    import base64
    def get_base64_image(image_path):
        try:
            with open(image_path, "rb") as f:
                return base64.b64encode(f.read()).decode()
        except:
            return ""
    drug_icon = get_base64_image("images/drug_icon.png")
    with st.container(border=True):
        st.markdown(f"""
        <div style="display: flex; align-items: center;
                        border-radius: 10px; padding: 20px;
                        font-size: 18px; margin-bottom: 10px;
                        ">
            <div style="display: flex; flex-direction: column; align-items: center; margin-right: 20px;">
            <img src="data:image/png;base64,{drug_icon}" width="60" height="60" style="margin-right: 10px; border-radius: 10px;">
            <div style="font-size: 22px; font-weight: bold; margin-top: 20px; 
            text-align: center; width: 80px;">
            {narx_formatted}
            </div>
            </div>
            <div>
               <b style="font-size: 20px; ">{dori_nomi}</b></br>
                <div style="font-size: 14px;">
                    <b>Dorixona:</b> {apteka} 
                    <span style="margin-left: 16px;">📍 {masofa:.2f} km</span><br>
                    📅 <b>Yaroqlilik muddati:</b> <i>{yaroqlik_muddati}</i>
                    <span style="margin-left:15px;">
                        📦 <i>{omborda_mavjud} ta qadoq mavjud</i>
                    </span><br>
                   📌 <b>Manzil:</b> <i>{manzil}</i><br>
            </div>
        """, unsafe_allow_html=True)
        
        key = f"buy_{clean_key(dori_nomi)}_{clean_key(apteka)}_{i}"
        #buy_key = f"{i}_buy"

        col1, col2, col3, col4,col5 = st.columns(5)
 
        with col1:
            if st.button("💳", key=f"buy_{key}"):
                item = {
                    "dori_nomi": row.get("Dori nomi", "Nomaʼlum"),
                    "narx": int(row.get("clean_narx", 0)),
                    "dorixona": row.get("Apteka nomi", "Nomaʼlum"),
                    "lat": row.get("Latitude"),
                    "lon": row.get("Longitude"),
                    "vaqt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "yaroqlik_muddati": row.get("Yaroqlik muddati", "kiritilmagan"),
                    "omborda_mavjud": row.get("Omborda mavjudligi", "aniqlanmagan"),
                    "masofa_km": float(row.get("masofa_km", 0))
                }
                if "cart" not in st.session_state:
                    st.session_state["cart"] = []
                st.session_state["cart"].append(item)
                # st.session_state["tanlangan_dori"] = row.to_dict()
                st.switch_page("pages/pay.py")
        with col3:
                st.markdown(f"""
                    <a href="tel:{telefon}" target="_blank">
                        <button style="
                            background:#12202D;
                            color:white;
                            border:none;
                            padding:10px 14px;
                            border-radius:18px;
                            font-size:16px;
                            cursor:pointer;
                            width:100%;
                        ">
                            📞
                        </button>
                    </a>
                """, unsafe_allow_html=True)
        with col5:
            if st.button("🛒", key=f"savat_{i}"):
                item = {
                    "dori_nomi": row.get("Dori nomi", "Nomaʼlum"),
                    "narx": int(row.get("clean_narx", 0)),
                    "dorixona": row.get("Apteka nomi", "Nomaʼlum"),
                    "lat": row.get("Latitude"),
                    "lon": row.get("Longitude"),
                    "vaqt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "yaroqlik_muddati": row.get("Yaroqlik muddati", "kiritilmagan"),
                    "omborda_mavjud": row.get("Omborda mavjudligi", "aniqlanmagan"),
                    "masofa_km": float(row.get("masofa_km", 0))
                }
             
                if "cart" not in st.session_state:
                    st.session_state["cart"] = []
                st.session_state["cart"].append(item)
                st.success("✅ Savatga qo‘shildi!")

# Sahifa tugmalari uchun ustunlar
col1, col2, col3, col4, col5,col6 = st.columns([2.1,1, 2, 0.5, 1.7, 1])

with col2:
    if st.button("⬅️", key="prev_btn") and st.session_state["cheap_page"] > 0:
        st.session_state["cheap_page"] -= 1
        st.rerun()

with col3:
    st.markdown(
        f"<div style='text-align: center; font-size: 18px;'><b>{st.session_state['cheap_page'] + 1} / {total_pages}</b></div>",
        unsafe_allow_html=True
    )

with col5:
    if st.button("➡️", key="next_btn") and st.session_state["cheap_page"] < total_pages - 1:
        st.session_state["cheap_page"] += 1
        st.rerun()


