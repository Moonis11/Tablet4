import streamlit as st
import pandas as pd
import requests
from math import radians, sin, cos, sqrt, atan2
from datetime import datetime
from streamlit_javascript import st_javascript
from theme_manager import apply_theme
from imageapp import transliterate_ru_to_lat
from difflib import get_close_matches
import re
from translate import tr, languages, language_selector_inline
from streamlit_extras.switch_page_button import switch_page

apply_theme()

# 🏁 Tilni boshlash
lang = st.session_state.get("lang", "uz")

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

# 🏁 Tilni boshlash
lang = st.session_state.get("lang", "uz")

st.set_page_config(page_title=tr("title", lang))
#st.title(tr("close_pharmacy", lang))

apteka_df = pd.read_csv("APTEKA.csv")
apteka_df.columns = apteka_df.columns.str.strip()

if "cart" not in st.session_state:
    st.session_state["cart"] = []

if "info" not in st.session_state or "name" not in st.session_state["info"]:
    st.error(tr("not_detected", lang))
    st.stop()

# === OCR nomi tozalash + transliteratsiya
def is_cyrillic(text):
    return bool(re.search('[\u0400-\u04FF]', text))

raw_name = st.session_state["info"]["name"][0] if isinstance(st.session_state["info"]["name"], tuple) else st.session_state["info"]["name"]
clean_name = raw_name.lower().strip()
if is_cyrillic(clean_name):
    clean_name = transliterate_ru_to_lat(clean_name)
clean_name = clean_name.strip()

# === Fuzzy matching
candidate_names = apteka_df["Dori nomi"].astype(str).str.lower().str.strip().tolist()
match = get_close_matches(clean_name, candidate_names, n=1, cutoff=0.7)
dori_nomi = match[0] if match else clean_name

mos_qatorlar = apteka_df[apteka_df["Dori nomi"].str.lower().str.strip() == dori_nomi].copy()

# Narxni tozalash
def to_number(x):
    try:
        return int(str(x).replace(" ", "").split(".")[0])
    except:
        return float('inf')

mos_qatorlar["clean_narx"] = mos_qatorlar["Narxi (taxminiy)"].apply(to_number)

# === Lokatsiya olish
import requests
from streamlit_javascript import st_javascript

# 🌍 Lokatsiyani aniqlash (GPS → IP fallback)
if "user_location_name" not in st.session_state:
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

        # 📍 Geocode qilish
        try:
            url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
            data = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}).json()
            location_name = data.get("display_name", "Nomaʼlum joy")
            st.session_state["user_location_name"] = location_name
            st.success(f"📍 Aniqlangan manzil: {location_name}")
        except Exception as e:
            st.warning("❗ Lokatsiyani aniqlab bo‘lmadi. Qo‘lda kiriting.")
    else:
        st.warning("❗ Lokatsiya topilmadi. IP orqali aniqlashga urinilmoqda...")

        try:
            ipinfo = requests.get("https://ipinfo.io/json").json()
            loc = ipinfo.get("loc", "")
            if loc:
                lat, lon = map(float, loc.split(","))
                st.session_state["user_lat"] = lat
                st.session_state["user_lon"] = lon

                # 🔄 IP orqali geocode
                url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
                data = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}).json()
                location_name = data.get("display_name", "Nomaʼlum joy")
                st.session_state["user_location_name"] = location_name
                st.success(f"🌍 IP orqali manzil: {location_name}")
        except:
            st.error("❗ Lokatsiyani aniqlab bo‘lmadi.")


# === Eng yaqin dorixonani aniqlash
if "user_lat" in st.session_state and "user_lon" in st.session_state:
    user_lat, user_lon = st.session_state["user_lat"], st.session_state["user_lon"]

    def haversine(lat1, lon1, lat2, lon2):
        R = 6371
        dlat = radians(lat2 - lat1)
        dlon = radians(lon2 - lon1)
        a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        return R * c

    mos_qatorlar = mos_qatorlar.dropna(subset=["Latitude", "Longitude"])
    if mos_qatorlar.empty:
        st.warning("❗ Dorixonalarda koordinatalar mavjud emas.")
        st.stop()

    mos_qatorlar["masofa_km"] = mos_qatorlar.apply(
        lambda row: haversine(user_lat, user_lon, row["Latitude"], row["Longitude"]),
        axis=1
    )

    eng_yaqin = mos_qatorlar.sort_values("masofa_km").iloc[0]
    narx = eng_yaqin["clean_narx"]

currency = tr("currency", lang)

price_label = tr("price", lang)


    # Masofa va narx bo‘yicha saralash
top_20 = mos_qatorlar.sort_values("masofa_km").head(20)


@st.cache_data
def load_data():
    df = pd.read_csv("APTEKA.csv", encoding="utf-8-sig")
    df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
    df.columns = df.columns.str.strip()

    # Narx tozalash
    def to_number(x):
        try:
            return int(str(x).replace(" ", "").split(".")[0])
        except:
            return float('inf')
    df["clean_narx"] = df["Narxi (taxminiy)"].apply(to_number)
    return df

df = load_data()
#st.title("📍 Dori mavjud aptekalar ro'yxati")

mos_aptekalar = pd.DataFrame()
if dori_nomi:
    mask = df["Dori nomi"].fillna("").str.lower().str.contains(dori_nomi.lower())
    mos_aptekalar = df[mask]


def clean_key(text):
    return re.sub(r'[^a-z0-9]', '', text.lower())

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

if "user_lat" in st.session_state and "user_lon" in st.session_state:
    user_lat = st.session_state["user_lat"]
    user_lon = st.session_state["user_lon"]

    def haversine(lat1, lon1, lat2, lon2):
        R = 6371
        dlat = radians(lat2 - lat1)
        dlon = radians(lon2 - lon1)
        a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
        return 2 * R * atan2(sqrt(a), sqrt(1 - a))

    filtered_df = df[df["Dori nomi"] == dori_nomi].copy()
    filtered_df = filtered_df.dropna(subset=["Latitude", "Longitude"])
    filtered_df["masofa_km"] = filtered_df.apply(
        lambda row: haversine(user_lat, user_lon, row["Latitude"], row["Longitude"]),
        axis=1
    )

    filtered_df = filtered_df.sort_values("masofa_km", ascending=True)
else:
    st.warning("❗ Masofa bo‘yicha saralash uchun lokatsiya kerak.")
    filtered_df = df[df["Dori nomi"] == dori_nomi].copy()

# ✅ Sahifalash (Pagination)
items_per_page = 7
total_pages = (len(filtered_df) - 1) // items_per_page + 1

# Joriy sahifa dorilarini ko‘rsatish (to'g'ri sahifalash)
start_idx = st.session_state["cheap_page"] * items_per_page
end_idx = start_idx + items_per_page
page_df = filtered_df.iloc[start_idx:end_idx]
    
for i, row in page_df.iterrows():
    
    dori_nomi = row.get("Dori nomi", "Nomaʼlum")
    narx = int(row.get("clean_narx", 0))
    narx_formatted = f"{narx:,.0f}".replace(",", " ")

    apteka = row.get("Apteka nomi", "Nomaʼlum")
    telefon_raw = row.get("Telefon", "")
    masofa = float(row.get("masofa_km", 0))
    vaqt = datetime.now().strftime("%H:%M:%S")

    try:
        telefon = str(int(float(str(telefon_raw).replace(" ", "").replace("-", ""))))
    except:
        telefon = "Nomaʼlum"

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
                <img src="data:image/png;base64,{drug_icon}" width="60" height="60" style="margin-right: 20px;">
                <div>  
                    <b>{dori_nomi}</b><br>
                    💰 Narxi: {narx_formatted} so'm<br>
                    🏥 Dorixona: {apteka}<br>
                    📞 Telefon: <a href="tel:{telefon}">{telefon}</a><br>
                    📍 Masofa: {masofa:.2f} km<br>
                    📅 Yaroqlik muddati: <i>{yaroqlik_muddati}</i><br>
                    📦 Omborda mavjudligi: <i>{omborda_mavjud}</i>
                </div>
            </div>
        """, unsafe_allow_html=True)

        key = f"buy_{clean_key(dori_nomi)}_{clean_key(apteka)}_{i}"
        col1, col2 = st.columns(2)

    with col1:
        if st.button(" Tolovga o`tish", key=f"buy_{key}"):
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

            st.session_state["cart"].append(item)
            #st.session_state["tanlangan_dori"] = row.to_dict()
            st.switch_page("pages/pay.py")

    with col2:
        if st.button(" Savatga qo‘shish", key=f"savat_{i}"):
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

            st.session_state["cart"].append(item)
            st.success("✅ Savatga qo‘shildi!")
          
col2, col3 = st.columns(2)



# import base64

# # Rasmni base64 formatga o‘girish
# def get_base64_image(path):
#     with open(path, "rb") as image_file:
#         encoded = base64.b64encode(image_file.read()).decode()
#     return f"data:image/png;base64,{encoded}"

# # Rasm yo‘li
# icon_base64 = get_base64_image("images/cart.png")

# with col2:
#     st.markdown(f"""
#         <div style='text-align:center;'>
#             <form action='/pages/savat.py'>
#                 <button style='background:none; border:none; cursor:pointer;'>
#                     <img src="{icon_base64}" width="50" />
#                 </button>
#             </form>
#         </div>
#     """, unsafe_allow_html=True)


# # with col3:
#     st.markdown(f"<div style='text-align:center;'>", unsafe_allow_html=True)
#     if st.button(tr("go_payment", lang), use_container_width=True):
#         st.switch_page("pages/pay.py")
#     st.markdown("</div>", unsafe_allow_html=True)

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

# # Bosh sahifa tugmasi
# st.markdown("---")
# col_a, col_b, col_c = st.columns([1, 2, 1])
# with col_b:
#     st.markdown(f"<div style='text-align:center;'>", unsafe_allow_html=True)
#     if st.button(tr("go_home", lang), use_container_width=True):
#         st.switch_page("pages/home.py")
#     st.markdown("</div>", unsafe_allow_html=True)
