import streamlit as st
import pandas as pd
import requests
import re
import time
from datetime import datetime
from math import radians, sin, cos, sqrt, atan2
from streamlit_javascript import st_javascript
from imageapp import clean_drug_name, is_cyrillic, transliterate_ru_to_lat
from  translate import tr, languages, language_selector_inline
from streamlit_extras.switch_page_button import switch_page
from theme_manager import apply_theme
apply_theme()
# 🏁 Tilni boshlash
lang = st.session_state.get("lang", "uz")

st.set_page_config(page_title=tr("title", lang))
#st.title(tr("cheap_pharmacy", lang))
 
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


# CSV yuklash
apteka_df = pd.read_csv("APTEKA.csv")
apteka_df.columns = apteka_df.columns.str.strip()

# Savatchani boshlash
if "cart" not in st.session_state:
    st.session_state["cart"] = []

# OCR dan olingan dori nomi mavjudligini tekshirish
if "info" not in st.session_state or "name" not in st.session_state["info"]:
    st.error("❗ " + tr("drug_not_detected", lang))
    st.stop()

# Dori nomini tozalash
raw_name = st.session_state["info"]["name"]
dori_nomi = raw_name[0] if isinstance(raw_name, tuple) else raw_name
dori_nomi = clean_drug_name(dori_nomi.lower().strip())
if is_cyrillic(dori_nomi):
    dori_nomi = transliterate_ru_to_lat(dori_nomi)

# Dori bo‘yicha mos qatorlarni olish
mos_qatorlar = apteka_df[apteka_df["Dori nomi"].str.lower().str.strip() == dori_nomi].copy()

if mos_qatorlar.empty:
    st.warning(f"❗ {tr('not_found_exact', lang).format(dori=dori_nomi)}")
    
    if st.button(tr("new_search", lang)):
        st.session_state.clear()
        st.switch_page("pages/home.py")
    st.stop()

# Narxni raqamga aylantirish
def to_number(x):
    try:
        return int(str(x).replace(" ", "").split(".")[0])
    except:
        return float('inf')

mos_qatorlar["clean_narx"] = mos_qatorlar["Narxi (taxminiy)"].apply(to_number)

# 📡 Joylashuvni olish
# 🌍 Lokatsiyani aniqlash tugmasi
# 🌍 Lokatsiyani aniqlash tugmasi
if st.button(tr("get_location", lang)):
    coords = st_javascript("""
        async () => await new Promise((resolve) => {
            if (!navigator.geolocation) {
                resolve({});
            } else {
                navigator.geolocation.getCurrentPosition(
                    (pos)=>resolve({lat:pos.coords.latitude, lon:pos.coords.longitude}),
                    (err)=>resolve({})
                );
            }
        });
    """)

    if isinstance(coords, dict) and "lat" in coords:
        lat, lon = coords["lat"], coords["lon"]
        st.session_state["user_lat"] = lat
        st.session_state["user_lon"] = lon

        try:
            url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
            data = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}).json()
            location_name = data.get("display_name", "Nomaʼlum joy")
            st.session_state["user_location_name"] = location_name
            st.success(f"📍 Aniqlangan manzil: {location_name}")
        except:
            st.warning("❗ Lokatsiyani aniqlab bo‘lmadi. Qo‘lda kiriting.")
    else:
        # 🌐 IP orqali aniqlash fallback
        try:
            ipinfo = requests.get("https://ipinfo.io/json").json()
            loc = ipinfo.get("loc", "")
            if loc:
                lat, lon = map(float, loc.split(","))
                st.session_state["user_lat"] = lat
                st.session_state["user_lon"] = lon

                url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
                data = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}).json()
                location_name = data.get("display_name", "Nomaʼlum joy")
                st.session_state["user_location_name"] = location_name
                #st.success(f"🌍 IP orqali manzil: {location_name}")
        except:
            st.error("❗ Lokatsiyani aniqlab bo‘lmadi.")




    # 🌐 Reverse geocoding orqali manzil nomini aniqlash
    lat = st.session_state.get("user_lat")
    lon = st.session_state.get("user_lon")

    if lat and lon:
        try:
            res = requests.get(
                f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json",
                headers={"User-Agent": "location-app"},
                timeout=10
            )
            data = res.json()
            location_name = data.get("display_name", "Nomaʼlum joy")
            st.session_state["user_location_name"] = location_name
            #st.success(f"📍 Aniqlangan manzil: {location_name}")
        except Exception as e:
            st.error(f"Joy nomini aniqlab bo‘lmadi: {e}")
            st.session_state["user_location_name"] = "Nomaʼlum"

# 👇 Lokatsiyaga asoslangan eng yaqin dorixonani topish
if "user_lat" in st.session_state and "user_lon" in st.session_state:
    user_lat = st.session_state["user_lat"]
    user_lon = st.session_state["user_lon"]

    def haversine(lat1, lon1, lat2, lon2):
        R = 6371
        dlat = radians(lat2 - lat1)
        dlon = radians(lon2 - lon1)
        a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
        return 2 * R * atan2(sqrt(a), sqrt(1 - a))

    mos_qatorlar = mos_qatorlar.dropna(subset=["Latitude", "Longitude"])
    if mos_qatorlar.empty:
        st.warning("❗ Koordinatalar mavjud emas.")
        st.stop()

    mos_qatorlar["masofa_km"] = mos_qatorlar.apply(
        lambda row: haversine(user_lat, user_lon, row["Latitude"], row["Longitude"]),
        axis=1
    )



    # 1️⃣ Avval eng arzonlarni tanlaymiz
    eng_arzon_narx = mos_qatorlar["clean_narx"].min()
    arzonlar = mos_qatorlar[mos_qatorlar["clean_narx"] == eng_arzon_narx]

    # 2️⃣ Arzonlar orasidan eng yaqinini tanlaymiz
    eng_yaqin = arzonlar.sort_values("masofa_km").iloc[0]
    narx = eng_yaqin["clean_narx"]
    

    # 👇 20 ta eng arzon aptekani chiroyli ko‘rinishda chiqarish
#st.subheader(tr("top_cheap_list", lang))  # Istasangiz tarjima faylga qo‘shing

# Masofa va narx bo‘yicha saralash
top_20 = mos_qatorlar.sort_values(["clean_narx", "masofa_km"]).head(20)

# @st.cache_data olib tashlandi
def load_data():
    df = pd.read_csv("APTEKA.csv", encoding="utf-8-sig")
    df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
    df.columns = df.columns.str.strip()

    def to_number(x):
        try:
            return int(str(x).replace(" ", "").split(".")[0])
        except:
            return float('inf')
    df["clean_narx"] = df["Narxi (taxminiy)"].apply(to_number)
    return df

df = load_data()
#st.title("📍 Dori mavjud aptekalar ro'yxati")

def clean_key(text):
    return re.sub(r'[^a-z0-9]', '', text.lower())
# ✅ Sahifalash (Pagination)


if "cheap_page" not in st.session_state:
    st.session_state["cheap_page"] = 0
td = st.session_state.get("tanlangan_dori", {})
if isinstance(td, dict):
    dori_nomi = td.get("Dori nomi", "").strip()
else:
    dori_nomi = str(td).strip()


if not dori_nomi:
    st.warning("❗ Dori nomi tanlanmagan")
    st.stop()

# 🔽 Arzon narxlardan boshlab saralash
filtered_df = df[df["Dori nomi"] == dori_nomi].sort_values("clean_narx", ascending=True)

if filtered_df.empty:
    st.info("Ushbu dori uchun dorixonalar topilmadi.")
    st.stop()

# Agar foydalanuvchi joylashuvi mavjud bo‘lsa, masofani hisoblaymiz
if "user_lat" in st.session_state and "user_lon" in st.session_state:
    user_lat = st.session_state["user_lat"]
    user_lon = st.session_state["user_lon"]

    def haversine(lat1, lon1, lat2, lon2):
        R = 6371
        dlat = radians(lat2 - lat1)
        dlon = radians(lon2 - lon1)
        a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
        return 2 * R * atan2(sqrt(a), sqrt(1 - a))

    filtered_df = filtered_df.dropna(subset=["Latitude", "Longitude"])
    filtered_df["masofa_km"] = filtered_df.apply(
        lambda row: haversine(user_lat, user_lon, row["Latitude"], row["Longitude"]),
        axis=1
    )
else:
    filtered_df["masofa_km"] = None

# ✅ Sahifalash (Pagination)
items_per_page = 7
total_pages = (len(filtered_df) - 1) // items_per_page + 1

# Joriy sahifa dorilarini ko‘rsatish
start_idx = st.session_state["cheap_page"] * items_per_page
end_idx = start_idx + items_per_page
page_df = filtered_df.iloc[start_idx:end_idx]

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
    narx = int(row.get("clean_narx", 0))
    narx_formatted = f"{narx:,.0f}".replace(",", " ")

    # Lat va Lon dan manzil olish
    lat = row.get("Latitude")
    lon = row.get("Longitude")
    manzil = get_address_from_coords(lat, lon) if lat and lon else "Manzil mavjud emas"

    apteka = row.get("Apteka nomi", "Nomaʼlum")
    telefon_raw = row.get("Telefon", "")
    masofa = float(row.get("masofa_km", 0))
    vaqt = datetime.now().strftime("%H:%M:%S")

    try:
        telefon = str(int(float(str(telefon_raw).replace(" ", "").replace("-", ""))))
    except:
        telefon = "Nomaʼlum"
    ish_vaqti = row.get("ish_vaqti", "Ma'lumot yo'q")
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
                    <span style="margin-left: 16px;">⏰ {ish_vaqti}</span>
                    <span style="margin-left: 16px;">📍 {masofa:.2f} km</span><br>
                    📅 <b>Yaroqlilik muddati:</b> <i>{yaroqlik_muddati}</i>
                    <span style="margin-left:15px;">
                        📦 <i>{omborda_mavjud} ta qadoq mavjud</i>
                    </span><br>
                   📌 <b>Manzil:</b> <i>{manzil}</i><br>
            </div>
        """, unsafe_allow_html=True)

        key = f"buy_{clean_key(dori_nomi)}_{clean_key(apteka)}_{i}"
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

# Telefonni tozalash
try:
    telefon_raw = eng_yaqin.get("Telefon", "")
    try:
        telefon = str(int(float(telefon_raw)))
    except:
        telefon = "Nomaʼlum"

    currency = tr("currency", lang)
    price_label = tr("price", lang)


except NameError:
    st.warning("❗ " + tr("please_detect_location", lang))



# col2, col3 = st.columns(2)

# with col2:
#     st.markdown(f"<div style='text-align:center;'>", unsafe_allow_html=True)
#     if st.button(tr("to_cart", lang), use_container_width=True):
#         st.switch_page("pages/savat.py")
#     st.markdown("</div>", unsafe_allow_html=True)

# with col3:
#     st.markdown(f"<div style='text-align:center;'>", unsafe_allow_html=True)
#     if st.button(tr("go_payment", lang), use_container_width=True):
#         st.switch_page("pages/pay.py")
#     st.markdown("</div>", unsafe_allow_html=True)


# # Bosh sahifa tugmasi
# st.markdown("---")
# col_a, col_b, col_c = st.columns([1, 2, 1])
# with col_b:
#     st.markdown(f"<div style='text-align:center;'>", unsafe_allow_html=True)
#     if st.button(tr("go_home", lang), use_container_width=True):
#         st.switch_page("pages/home.py")
#     st.markdown("</div>", unsafe_allow_html=True)
