# 👆 Kodning boshlanishi
import streamlit as st
import uuid
import requests
from streamlit_extras.switch_page_button import switch_page
from transfer import taqsimla, taqsimla_cart
from cart_utils import get_cart, clear_cart
from theme_manager import apply_theme 
apply_theme()
from translate import tr
from datetime import datetime
import pandas as pd
from pathlib import Path
from yandex_mock_pricing import foydalanuvchi_uchun_narx
from math import radians, sin, cos, sqrt, atan2


# ====== SESSION VA MA’LUMOTLAR ======
st.set_page_config(page_title="Buyurtma", layout="centered")
lang = st.session_state.get("lang", "uz")

# 🔁 Dorixona yoki foydalanuvchi koordinatalari o‘zgarganligini tekshirish
if "cart" in st.session_state:
    cart = st.session_state["cart"]
    dorixona_lat = cart[0].get("lat")
    dorixona_lon = cart[0].get("lon")

    user_lat = st.session_state.get("user_lat")
    user_lon = st.session_state.get("user_lon")

    if not (dorixona_lat and dorixona_lon and user_lat and user_lon):
        st.warning("Lokatsiya ma'lumotlari yetarli emas.")
        st.stop()
    
    # 🔁 Masofa qayta hisoblanadi
    old_distance = st.session_state.get("old_distance")
    from math import radians, sin, cos, sqrt, atan2

    def haversine(lat1, lon1, lat2, lon2):
        R = 6371
        dlat = radians(lat2 - lat1)
        dlon = radians(lon2 - lon1)
        a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        return R * c

    new_distance = haversine(user_lat, user_lon, dorixona_lat, dorixona_lon)
    rounded_distance = round(new_distance, 2)

    # ✅ Agar masofa o‘zgargan bo‘lsa — sahifani qayta yuklaymiz
    if old_distance is None or abs(rounded_distance - old_distance) > 0.01:
        st.session_state["old_distance"] = rounded_distance
        st.rerun()

# ====== STATIK QIYMATLAR ======
SERVICE_PCT, LOGISTICS_PCT, PAYME_PCT, VAT_PCT = 0.02, 0.02, 0.015, 0.04
tablet_card  = "8600 7777 6666 0000"   # servis
pharmacy_card = "8600 5555 4444 1111"   # kuryer (misol)

# ----- yordamchi funksiyalar -----
def taqsimla_yangi(total_price, drug_price, pharmacy_card, tablet_card):
    return {
        "to_apteka": {"receiver": pharmacy_card, "amount": drug_price},
        "to_tablet": {"receiver": tablet_card, "amount": total_price - drug_price},
    }

def send_order_to_apteka(chat_id, apteka_name, drug_list, order_id,
                         user_name, user_phone, location, amount, pharmacy_card):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    msg = (
        f"📦 *Yangi buyurtma!*\n\n"
        f"🏥 *{apteka_name}*\n🧾 ID `{order_id}`\n🕒 {now}\n\n"
        f"{drug_list}\n\n"
        f"💳 *To‘langan:* `{amount:,}` so‘m\n"
        f"💼 `{pharmacy_card}`"
    )
    BOT_TOKEN = "7962351903:AAGOKHW_4QLiMksqL6bQsUF6GDeu1yrbOlw"
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={"chat_id": chat_id, "text": msg, "parse_mode": "Markdown"},
    )

# ====== SESSION VA MA’LUMOTLAR ======
st.set_page_config(page_title="Buyurtma", layout="centered")
lang = st.session_state.get("lang", "uz")
st.title(tr("order_page", lang))

cart = st.session_state.get("cart", [])

if not cart:
    st.warning("Hech qanday dori tanlanmagan.")
    st.stop()

def get_valid_items():
    cart = st.session_state.get("cart", [])
    selected = st.session_state.get("tanlangan_dori")
    # 🆕 Tanlangan bitta dori bo‘lsa savatga kirmasdan ishlash
    if selected and "dori_nomi" in selected:
        return [selected]
    # 🧺 Aks holda savatdagi dorilarni tekshirish
    return [i for i in cart if "dori_nomi" in i]

valid_items = get_valid_items()

if not valid_items:
    st.warning("Hech qanday dori tanlanmagan.")
    st.stop()


    first_item = valid_items[0]
   

# KeyError chiqmasligi uchun xavfsiz ishlash
try:
    drug_names = ", ".join(i["dori_nomi"].capitalize() for i in valid_items)
except KeyError as e:
    st.error(f"❌ Ma'lumot topilmadi: {e}")
    st.stop()

drug_price = sum(
    int(str(i.get("narx", "0")).replace(" ", "")) for i in valid_items if i.get("narx")
)

# 🧭 Koordinatalarni aniqlash (birinchi elementdan emas, valid elementdan)
first_item = valid_items[0]
dorixona_lat = valid_items[0].get("lat")
dorixona_lon = valid_items[0].get("lon")

user_lat = st.session_state.get("user_lat")
user_lon = st.session_state.get("user_lon")

if not (dorixona_lat and dorixona_lon and user_lat and user_lon):
    st.warning("Lokatsiya ma'lumotlari yetarli emas.")
    st.stop()


# 📏 Masofa hisoblash
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Yer radiusi km
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return round(R * c, 1)

masofa_km = 3  # default
if user_lat and user_lon and dorixona_lat and dorixona_lon:
    try:
        masofa_km = haversine(user_lat, user_lon, dorixona_lat, dorixona_lon)
    except:
        pass

# 💡 Yetkazib berish narxini avtomatik hisoblash
now = datetime.now()
kun_turi_auto = "dam olish" if now.weekday() == 6 else "ish kuni"  # faqat yakshanba dam olish deb olinmoqda
def format_narx(narx: int) -> str:
    return f"{narx:,}"

# har safar dorixona tanlansa yoki user joylashuvi o‘zgarsa:
if user_lat and user_lon and dorixona_lat and dorixona_lon:
    masofa_km = haversine(user_lat, user_lon, dorixona_lat, dorixona_lon)

result = foydalanuvchi_uchun_narx(
    masofa_km=masofa_km,
    soat=now.hour,
    kun_turi=kun_turi_auto,
    yomgir=False,
    ogirlik_kg=3,
    yuk_kategoriya="kichik"
)

delivery_fee_default = result["foydalanuvchiga_narx"]  # ✅ foydalanuvchiga ko‘rsatiladigan umumiy narx
st.info(f"📏 Dorixonagacha masofa: {masofa_km:.2f} km")

# ====== 1‑FORM: BUYURTMA ======
with st.form(key="buyurtma_form"):
    order_id  = str(uuid.uuid4())[:8]
   

    # def tr(key, lang):
    #     return {"phone": "📞 Telefon raqamingizni kiriting:"}.get(key, key)

    # Telefon raqami input
    default = "+998 "
    phone = st.text_input(tr("phone", lang), value=default, max_chars=14)

    # Validatsiya
    is_valid = (
        phone.startswith("+998 ") and
        len(phone) == 14 and
        phone[5:].isdigit()
        )

# Faqat to‘g‘ri raqam bo‘lsa natija ko‘rsatiladi
    if is_valid:
        st.success(f"✅ To‘g‘ri raqam: {phone}")

    name = st.text_input(tr("name", lang), max_chars=15)

    # ✅ Ism uzunligi validatsiyasi
    if name and len(name) > 15:
        st.error()


     # 🌍 Lokatsiya inputi: avtomatik aniqlangan yoki qo‘lda kiritiladigan
    location = st.text_area(
        tr("your_location", lang),
        value=st.session_state.get("user_location_name", "")
    )
    st.text_area(tr("drug_list", lang), value=drug_names, disabled=True)

    drug_price_in = st.number_input(
        tr("drug_price", lang), value=drug_price, disabled=True, step=1000
    )

    delivery_fee = st.number_input(
    label=tr("delivery_fee", lang),
    value=delivery_fee_default,
    step=1000,
    format="%d",
    disabled=True
    )

    # --- foizlar ---
    base_total    = drug_price_in + delivery_fee
    logistics_fee = int(base_total * LOGISTICS_PCT)
    smart_service = int(base_total * SERVICE_PCT)
    payme_fee     = int(base_total * PAYME_PCT)
    tax_fee       = int(base_total * VAT_PCT)
    total_price   = base_total + logistics_fee + smart_service + payme_fee + tax_fee
    cur = tr("currency", lang)

    # c1, c2 = st.columns(2)
    # c1.markdown(f" {tr('logistics_fee', lang)} (2%): {logistics_fee:,} {cur}")
    # c2.markdown(f"**🧠 {tr('smart_service', lang)} (2%)**: {smart_service:,} {cur}")
   
   

    st.markdown(
        f"""<div class='info-box'>
             {tr('total_pay', lang)}: {total_price:,} {cur}
        </div>""",
        unsafe_allow_html=True,
    )
      # Submit tugmasi
    submitted = st.form_submit_button(tr("confirm_order", lang), use_container_width=True)

    if submitted:
        st.session_state.update({
            "order_id": order_id,
            "name": name,
            "phone": phone,
            "location": location,
            "drug_name": drug_names,
            "drug_price": drug_price_in,
            "delivery_fee": delivery_fee,
            "logistics_fee": logistics_fee,
            "smart_service": smart_service,
            "total": total_price,
            "profit": logistics_fee + smart_service
        })


        # ======  BUYURTMA SUBMIT LOGIKA  ======

        # --- apteka ma’lumoti ---
        apteka_df   = pd.read_csv("APTEKA.csv")
        apteka_nomi = valid_items[0].get("dorixona", "Nomaʼlum")
        apteka_info = apteka_df.loc[apteka_df["Apteka nomi"] == apteka_nomi]
        if apteka_info.empty:
            st.error("❌ Apteka topilmadi!")
            st.stop()
        apteka_info = apteka_info.squeeze()
                # Telegram xabar yuborish
        send_order_to_apteka(
        chat_id       = apteka_info["telegram_ID"],
        apteka_name   = apteka_nomi,
        drug_list     = drug_names,
        order_id      = order_id,
        amount        = drug_price_in,
        pharmacy_card = apteka_info["Hisob_raqami"],
        user_name     = name,
        user_phone    = phone,
        location      = location
        )

        # 💳 Taqsimlash (shunchaki ishlatilgan bo‘lishi uchun)
        transfers = taqsimla_yangi(
        total_price=total_price,
        drug_price=drug_price_in,
        pharmacy_card=apteka_info["Hisob_raqami"],
        tablet_card=tablet_card
        )

        # Sahifani almashtirish (pages/order.py → sarlavhasi: Buyurtma)
        st.switch_page("pages/order.py")

