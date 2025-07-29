import streamlit as st
from PIL import Image
import pandas as pd
import re
import traceback
import base64
from voiceapp import AudioProcessor
from imageapp import (
    resize_image, fix_orientation, image_to_base64, clean_drug_name,
    transliterate_ru_to_lat, is_cyrillic, get_drug_info_from_csv
)
from oracle import extract_drug_info_by_cropping
from theme_manager import get_theme_css
from streamlit_webrtc import webrtc_streamer
import uuid
from streamlit_extras.switch_page_button import switch_page



# Sahifa sozlamasi
st.set_page_config(
    page_title="TabletAI - Dori tanib olish",
    layout="centered",  # mobilga eng yaxshi variant
    initial_sidebar_state="collapsed"
)


df = pd.read_csv("alternativa1.csv")

# 🚦 Rejimni tekshirish va default qiymat berish
if "mode" not in st.session_state or st.session_state["mode"] is None:
    st.session_state["mode"] = "image"  # yoki "manual", "voice" — bu yerda o'zingiz tanlaysiz

mode = st.session_state["mode"]


# 🌗 Theme toggle (Light ↔ Dark)
# ✅ Session_state ni initialize qilish
if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "dark"

if "theme_toggle_state" not in st.session_state:
    st.session_state.theme_toggle_state = (st.session_state.theme_mode == "light")

# 🎛️ Toggle UI
toggle_label = "🌞 Light Mode" if st.session_state.theme_mode == "dark" else "🌙 Dark Mode"
new_toggle_value = st.sidebar.toggle(toggle_label, value=st.session_state.theme_toggle_state)

# 🔁 Toggle o‘zgarsa — theme_mode yangilanadi va sahifa yangilanadi
if new_toggle_value != st.session_state.theme_toggle_state:
    st.session_state.theme_toggle_state = new_toggle_value
    st.session_state.theme_mode = "light" if new_toggle_value else "dark"
    st.rerun()

# 🎨 CSS yuklash
st.markdown(get_theme_css(st.session_state.theme_mode), unsafe_allow_html=True)



from translate import tr, languages

# Tilni session_state ga o‘rnatamiz
if "lang" not in st.session_state:
    st.session_state["lang"] = "uz"

previous_lang = st.session_state["lang"]
lang_choice = st.sidebar.radio(
    "🌐 Til / Language / Язык",
    list(languages.keys()),
    index=list(languages.values()).index(previous_lang)
)
new_lang = languages[lang_choice]

if new_lang != previous_lang:
    st.session_state["lang"] = new_lang
    st.rerun()

lang = st.session_state["lang"]
st.set_page_config(page_title=tr("title", lang))


translations = {
    "title": {
        "uz": "🧪 TabletAI",
        "ru": "🧪 ТаблетAI",
        "en": "🧪 TabletAI",
        "kiril": "🧪 ТаблетAI"
    },
    "upload_label": {
        "uz": "Rasm yuklang",
        "ru": "Загрузите изображение",
        "en": "Upload an image",
        "kiril": "Расм юкланг"
    },
    "detecting": {
        "uz": "🔍 Dori nomi aniqlanmoqda...",
        "ru": "🔍 Название лекарства определяется...",
        "en": "🔍 Detecting drug name...",
        "kiril": "🔍 Дори номи аниқланмоқда..."
    },
    "not_found": {
        "uz": "💬 Dori topilmadi.",
        "ru": "💬 Лекарство не найдено.",
        "en": "💬 Drug not found.",
        "kiril": "💬 Дори топилмади."
    },
    "alt_drugs": {
        "uz": "Alternativ dorilar",
        "ru": "Альтернативные лекарства",
        "en": "Alternative Drugs",
        "kiril": "Альтернатив дорилар"
    },
    "illness": {
        "uz": "Kasalliklar",
        "ru": "Заболевания",
        "en": "Illnesses",
        "kiril": "Касалликлар"
    },
    "usage": {
        "uz": "Instruksiya",
        "ru": "Инструкция",
        "en": "Instruction",
        "kiril": "Инструкция"
    },
    "disclaimer": {
        "uz": " Diqqat: bu dastur tibbiy maslahat emas.",
        "ru": " Внимание: это не медицинская консультация.",
        "en": " Note: This is not medical advice.",
        "kiril": " Диққат: бу дастур тиббий маслаҳат емас."
    },
    "price_label": {
        "uz": "Narxi",
        "ru": "Цена",
        "en": "Price",
        "kiril": "Нархи"
    },
    "drug_name": {
        "uz": "Dori nomi",
        "ru": "Название",
        "en": "Drug name",
        "kiril": "Дори номи"
    },
    "history_title": {
        "uz": "Tekshiruv tarixi",
        "ru": "История проверок",
        "en": "Search History",
        "kiril": "Текширув тарихи"
    },
    "image_upload_title": {
        "uz": "Rasm yuklang",
        "ru": "Загрузите изображение",
        "en": "Upload Image",
        "kiril": "Расм юкланг"
    },
    "voice_recording_title": {
        "uz": "Ovoz yozilmoqda...",
        "ru": "Голос записывается...",
        "en": "Recording voice...",
        "kiril": "Овоз ёзилмоқда..."
    },
    "cheap": {
        "uz": "Arzon",
        "ru": " Дешевле",
        "en": " Cheap",
        "kiril": "Арзон"
    },
    "near": {
        "uz": " Yaqin",
        "ru": " Ближе",
        "en": "Close",
        "kiril": " Яқин"
    },
    "history": {
        "uz": "Tarix",
        "ru": "История",
        "en": "History",
        "kiril": "Тарих"
    },
     "update": {
        "uz": "♻️ Yangilash",
        "ru": "♻️ Обновить",
        "en": "♻️ Update",
        "kiril": "♻️ Янгилаш"
    },
    "delete": {
        "uz": "🗑️ O‘chirish",
        "ru": "🗑️ Удалить",
        "en": "🗑️ Delete",
        "kiril": "🗑️ Ўчириш"
    }
}




def transliterate_to_cyrillic(text):
    mapping = {
        'a': 'а', 'b': 'б', 'd': 'д', 'e': 'е', 'f': 'ф', 'g': 'г', 'h': 'ҳ',
        'i': 'и', 'j': 'ж', 'k': 'к', 'l': 'л', 'm': 'м', 'n': 'н', 'o': 'о',
        'p': 'п', 'q': 'қ', 'r': 'р', 's': 'с', 't': 'т', 'u': 'у', 'v': 'в',
        'x': 'х', 'y': 'й', 'z': 'з', 'ʼ': 'ъ', "'": 'ъ', 'sh': 'ш', 'ch': 'ч',
        'ng': 'нг', 'ya': 'я', 'yo': 'ё', 'yu': 'ю', 'ts': 'ц', 'é': 'э'
    }

    for latin, cyrillic in sorted(mapping.items(), key=lambda x: -len(x[0])):
        text = re.sub(rf'\b{latin}\b', cyrillic, text, flags=re.IGNORECASE)
        text = re.sub(latin, cyrillic, text, flags=re.IGNORECASE)
    return text

# 🔹 ALT DRUG ICON + Sarlavha
def get_base64_image(image_path):
        with open(image_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    
# ✅ SHU YERGA QO‘YING!
def clear_image():
    st.session_state.uploaded_image = None
    st.session_state.voice_mode = False
    st.session_state.current_expanded = None



# st.title(translations["title"][lang])

# Avval mavjud rasm yo'qligini tekshirish
image_path = st.session_state.get("uploaded_image_path")

from datetime import datetime  # Eslatma: bu yuqorida bo‘lishi kerak

# 🔁 Tarix mavjud bo‘lmasa, yaratamiz
if "history" not in st.session_state:
    st.session_state["history"] = []

# 🖼️ Rasm manzili
image_path = st.session_state.get("uploaded_image_path")

# 🔍 Rasm allaqachon tarixga yozilganmi?
already_logged = False
for item in st.session_state["history"]:
    if item.get("type") == "image" and item.get("data") == image_path:
        already_logged = True
        break


for key, default in {
    "uploaded_image": None,
    "voice_mode": False,
    "history": [],
    "current_expanded": None,
    "history_expanded": set(),
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


def add_to_history(item_type, data, result):
    # Takroran kiritmaslik uchun tekshiruv
    for item in st.session_state["history"]:
        if item.get("type") == item_type and item.get("data") == data:
            return  # allaqachon mavjud

    if result:
        if len(st.session_state.history) >= 10:
            st.session_state.history.pop(0)
        st.session_state.history.append({
            "type": item_type,
            "data": data,
            "result": result,
            "vaqt": datetime.now()
        })

def render_drug_info(result, expanded=True):
    import re
    import base64

    nomi, kasallik, instruktsiya, alternativalar, narx = result

    # NaN va None holatlarni tozalash
    kasallik = str(kasallik) if pd.notna(kasallik) else ""
    instruktsiya = str(instruktsiya) if pd.notna(instruktsiya) else ""

    if isinstance(alternativalar, pd.DataFrame) is False:
        alternativalar = pd.DataFrame()

    # Tilga qarab transliteratsiya
    if lang == "ru":
        nomi = transliterate_to_cyrillic(nomi).capitalize()

    if lang == "kiril":
        nomi = transliterate_to_cyrillic(nomi).capitalize()
        kasallik = transliterate_to_cyrillic(kasallik)
        instruktsiya = transliterate_to_cyrillic(instruktsiya)
        if not alternativalar.empty:
            alternativalar.columns = [transliterate_to_cyrillic(col) for col in alternativalar.columns]
            alternativalar = alternativalar.applymap(lambda x: transliterate_to_cyrillic(str(x)))


    kasallik_text = kasallik if kasallik.strip() else "⚠️ Ma’lumot mavjud emas"
    instruktsiya_text = instruktsiya if instruktsiya.strip() else "⚠️ Ma’lumot mavjud emas"


    def get_base64_image(image_path):
        try:
            with open(image_path, "rb") as f:
                return base64.b64encode(f.read()).decode()
        except:
            return ""

    drug_icon = get_base64_image("images/drug_icon.png")
    # #price_icon = get_base64_image("images/price_icon.png")

    # Dori nomi
    st.markdown(f"""
    <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px; border-bottom: 1px solid #ccc; padding-bottom: 10px;'>
        <div style='display: flex; align-items: center; gap: 10px;'>
            <img src='data:image/png;base64,{drug_icon}' width='30'>
            <span style='font-size: 30px; font-weight: bold;'>{nomi}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    
    # Alternativa dorilar
    alt_icon = get_base64_image("images/alt_drugs_icon.png")
    st.markdown(f"""
    <div style='display:flex; align-items:center; gap:10px; margin-bottom:10px;'>
        <img src='data:image/png;base64,{alt_icon}' width='30'>
        <span style='font-size:30px; font-weight:bold;'>{translations['alt_drugs'][lang]}</span>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("", expanded=False):
        st.dataframe(alternativalar, use_container_width=True)

    # Kasalliklar
    kasallik_text = kasallik if kasallik.strip() else "⚠️ Ma’lumot mavjud emas"
    illness_icon = get_base64_image("images/illness_icon.png")

    with st.container():
        st.markdown(f"""
            <div style='display:flex; align-items:center; gap:10px; margin-bottom:10px;'>
                <img src='data:image/png;base64,{illness_icon}' width='30'>
                <span style='font-size:30px; font-weight:bold;'>{translations['illness'][lang]}</span>
            </div>
        """, unsafe_allow_html=True)

        with st.expander("", expanded=False):
            st.markdown(f"""
                <div style='max-height: 300px; overflow-y: auto; font-size: 20px; padding: 10px;'>                 '>
                    {kasallik_text.replace('\n', '<br>')}
                </div>
            """, unsafe_allow_html=True)
        


    # Instruksiya
    instruktsiya_text = instruktsiya if instruktsiya.strip() else "⚠️ Ma’lumot mavjud emas"
    instruction_icon = get_base64_image("images/instruction_icon.png")

    st.markdown(f"""
    <div style='display:flex; align-items:center; gap:10px; margin-bottom:10px;'>
        <img src='data:image/png;base64,{instruction_icon}' width='30'>
        <span style='font-size:30px; font-weight:bold;'>{translations['usage'][lang]}</span>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("", expanded=False):
        formatted_instruksiya = "<br>".join([
            re.sub(r"^(\u2022|\d+[\.\)]|\-)?\s*", "", line).rstrip('.') + "."
            for line in instruktsiya_text.split("\n") if line.strip()
        ])
        st.markdown(f"""
        <div style='max-height: 300px; overflow-y: auto; font-size: 20px; padding: 10px;'>
            {formatted_instruksiya}
        </div>
        """, unsafe_allow_html=True)


# # Eslatma
# disclaimer_icon = get_base64_image("images/disclaimer_icon.png")
# st.markdown(f"""
# <div style='display: flex; align-items: center; background-color:#194522;
#             padding: 15px; border-radius: 10px; border: 1px solid #ccc;
#             font-size: 20px; color: white; gap: 12px;'>
#     <img src='data:image/png;base64,{disclaimer_icon}' width='40'>
#     <div>
#         <span style='font-weight: bold;'> {translations['disclaimer'][lang]}</span>
#     </div>
# </div>
# """, unsafe_allow_html=True)


       
    

def render_history():
    st.markdown("---")
    # history_icon = get_base64_image("images/history_icon.png")
    # st.markdown(f"""
    # <div style='display: flex; align-items: center; gap: 10px; margin-top: 20px; margin-bottom: 10px;'>
    #     <img src='data:image/png;base64,{history_icon}' width='28'>
    #     <span style='font-size: 26px; font-weight: bold;'>{translations['history_title'][lang]}</span>
    # </div>
    # """, unsafe_allow_html=True)

    max_visible = 3
    full_history = st.session_state.history[-10:][::-1]
    short_history = full_history[:max_visible]
    hidden_history = full_history[max_visible:]


with st.container():
    if st.session_state.get("mode") == "image":
     def render_image_mode():
        

        # 🔑 Fayl yuklash uchun key
        if "uploader_key" not in st.session_state:
            st.session_state["uploader_key"] = "image_uploader"

        # ✅ Fayl yuklanmagan bo‘lsa — file_uploader ko‘rinadi
        if "uploaded_image" not in st.session_state or st.session_state["uploaded_image"] is None:
            st.markdown("""
            <style>
            /* --- "Drag and drop file here" yozuvini yashirish --- */
            div[data-testid="stFileUploadDropzoneInstructions"] > div,
            div[data-testid="stFileDropzoneInstructions"] > div {
                visibility: hidden;
                position: relative;
            }

            /* Fayl limiti va format yozuvlarini yashirish */
            div[data-testid="stFileUploadFileSizeLimit"],
            div[data-testid="stFileUploaderFileSizeLimit"],
            small {
                display: none !important;
            }
            </style>
        """, unsafe_allow_html=True)
            uploaded = st.file_uploader(
                label=" ",
                type=["png", "jpg", "jpeg"],
                key=st.session_state["uploader_key"],
                label_visibility="visible"
            )

            if uploaded:
                try:
                    image = Image.open(uploaded)
                    image = resize_image(image, max_size=(200, 200))
                    image = fix_orientation(image)
                    image = image.convert("RGB")

                    st.session_state["uploaded_image"] = uploaded
                    st.session_state["image_data"] = image

                    with st.spinner("🔍 Dori aniqlanmoqda..."):
                        dori_nomi = extract_drug_info_by_cropping(image)

                    st.session_state["info"] = {
                        "name": dori_nomi,
                        "image": uploaded
                    }

                    # ✅ Sahifani darhol switch qilish emas, avval rerun qilish
                    st.session_state["go_home"] = True
                    st.rerun()

                except Exception as e:
                    st.error("❌ Xatolik yuz berdi:")
                    st.text(traceback.format_exc())


                    # ✅ Rasm yuklangan bo‘lsa — rasm va tugmalar chiqadi
        else:
            col1, col2 = st.columns([1.5, 2])
            with col1:
                    if "image_data" in st.session_state:
                            st.image(st.session_state.image_data, caption="📷 Yuklangan rasm", width=200)
                            
                    # ➕ Tugmalar yonma-yon
                    btn1, btn2, btn3 = st.columns([1, 2, 1])
                    with btn2:
                        
                        if st.button(translations["update"][lang], key="clear_image_button"):   # o'chirish kodlari
                            st.session_state.pop("uploaded_image", None)
                            st.session_state.pop("image_data", None)
                            st.session_state.pop("info", None)
                            st.rerun()
                        
                    
            with col2:
                try:
                    image = Image.open(st.session_state["uploaded_image"])
                    image = resize_image(image)
                    image = fix_orientation(image)
                    with st.spinner(translations["detecting"][lang]):
                        text, confidence = extract_drug_info_by_cropping(image)
                        cleaned = clean_drug_name(text)
                        drug_name = transliterate_ru_to_lat(cleaned) if is_cyrillic(cleaned) else cleaned
                        result = get_drug_info_from_csv(drug_name, df, lang)

                    if result:
                        st.session_state["last_result"] = result
                        add_to_history("image", st.session_state["uploaded_image"], result)
                        render_drug_info(result)
                    else:
                        st.warning(translations["not_found"][lang])

                except Exception as e:
                    st.error("❌ Xatolik yuz berdi:")
                    st.text(traceback.format_exc())

            


    def render_voice_mode():
        

        col1, col2 = st.columns([1, 1])

        with col1:
            st.markdown("### 🔴 Ovoz yozish")

            ctx = webrtc_streamer(
                key="speech-mode",
                audio_processor_factory=AudioProcessor,
                media_stream_constraints={"video": False, "audio": True},
                async_processing=True
            )

            # 👉 Faqat 5 sekund jimlikdan so‘ng transkripsiya qilish
            if ctx.state == ctx.State.ACTIVE and ctx.audio_processor:
                if ctx.audio_processor.is_done():
                    result = ctx.audio_processor.transcribe()
                    if result:
                        st.session_state["last_transcript"] = result
                        st.session_state["last_result"] = get_drug_info_from_csv(result)
                        st.rerun()  # Sahifani yangilab, natijani ko‘rsatamiz

            st.markdown("#### 📋 Matn:")
            if "last_transcript" in st.session_state:
                st.success(st.session_state["last_transcript"])

            if st.button("❌ Tozalash"):
                st.session_state.pop("last_transcript", None)
                st.session_state.pop("last_result", None)
                st.rerun()

        with col2:
            if "last_result" in st.session_state and st.session_state["last_result"] is not None:
                st.markdown("### 💊 Dori ma’lumoti:")
                st.dataframe(st.session_state["last_result"], use_container_width=True)




    def render_manual_mode():
        st.header("✍️ " + translations["drug_name"][lang])

        col1, col2 = st.columns([0.5, 0.5])

        with col1:
                # 🧾 Dori nomini qo‘lda kiritish
            drug_name = st.text_input("🔍 Dori nomini kiriting:", key="manual_input")

            # ▶️ Bosh sahifa va O‘chirish tugmalari
            col_x, col_y = st.columns([1, 1])
            with col_x:
                if st.button("🏠 Bosh sahifa", key="home_manual_btn"):
                    st.session_state["mode"] = None
                    st.switch_page("pages/home.py")
            with col_y:
                if st.button("❌ O'chirish", key="clear_manual_btn"):
                    st.session_state.pop("last_result", None)
                    st.session_state.pop("manual_input", None)
                    st.rerun()

            # 🔍 Qidirish va natijani olish
            if drug_name:
                result = get_drug_info_from_csv(drug_name.strip(), df, lang)
                if result:
                    st.session_state["last_result"] = result
                    add_to_history("manual", drug_name.strip(), result)
                else:
                    st.session_state["last_result"] = None
                    st.warning(translations["not_found"][lang])

        with col2:
            # 📄 Natijani ko‘rsatish
            if "last_result" in st.session_state and st.session_state["last_result"]:
                render_drug_info(st.session_state["last_result"])


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

# =====================
# 🚀 Rejimni ishga tushurish
# =====================
mode = st.session_state.get("mode")

if mode == "image":
    render_image_mode()
elif mode == "voice":
    render_voice_mode()
elif mode == "manual":
    render_manual_mode()
else:
    st.warning("❗ Rejim tanlanmagan. Avval bosh sahifadan tanlang.")
   

if st.session_state.history:
 render_history()


# Boshlang‘ich sahifaga qaytish uchun funksiya
def go_home():
    st.switch_page("pages/home")
    st.rerun()


# def render_result(result):
#     st.markdown("### 🔍 Topilgan dori haqida ma'lumot:")
#     st.write(result)

# Faqat 'last_result' mavjud bo‘lsa va u bo‘sh bo‘lmasa
if "last_result" in st.session_state and st.session_state["last_result"]:
    result = st.session_state["last_result"]
    drug_name_detected = result[0] if result[0] else "Nomaʼlum"
    st.session_state["drug_name"] = drug_name_detected
    st.session_state["info"] = {"name": drug_name_detected}

   
#--------------------------------------------------------------------------------------------------------------------------------
# Oxshash dorilar
#--------------------------------------------------------------------------------------------------------------------------------
# 🔄 Ma'lumotlarni kechikmasdan keshga olish
CSV_PATH = "APTEKA.csv"
import os
def get_file_mtime(path):
    return os.path.getmtime(path)  # oxirgi o‘zgartirish vaqti (timestamp)

@st.cache_data(show_spinner=False)
def load_data(file_updated_at):
    df = pd.read_csv(CSV_PATH, encoding="utf-8-sig")
    df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
    df.columns = df.columns.str.strip()
    return df

# 🕒 Har doim faylning o‘zgartirilgan vaqtini jo‘natamiz:
last_modified = get_file_mtime(CSV_PATH)
df = load_data(last_modified)



#st.title("📍 Dori mavjud aptekalar ro'yxati")
# 🔐 Har doim kerakli session_state kalitlarini boshlab qo‘yish
# Session state ni boshlash
for key in ["main_page", "tanlangan_dori", "last_result"]:
    if key not in st.session_state:
        st.session_state[key] = 0 if "page" in key else ""


result = st.session_state.get("last_result", "")
if isinstance(result, dict):
    dori_nomi = result.get("name", "").strip()
elif isinstance(result, tuple):
    dori_nomi = result[0].strip()
else:
    dori_nomi = str(result).strip()

# ⚠️ mos_aptekalar doimiy aniqlansin
mos_aptekalar = pd.DataFrame()
if dori_nomi:
    mask = df["Dori nomi"].fillna("").str.lower().str.contains(dori_nomi.lower())
    mos_aptekalar = df[mask]
# Tozalash funksiyasi
def normalize_name(name):
    return str(name).strip().lower()

# Guruhlashdan oldin normalizatsiya qilingan ustun qo‘shamiz
if mos_aptekalar is not None and not mos_aptekalar.empty and "Dori nomi" in mos_aptekalar.columns:
    mos_aptekalar["Dori nomi clean"] = mos_aptekalar["Dori nomi"].apply(normalize_name)

    # 🔁 Dori nomi va turi bo‘yicha guruhlash (faqat noyoblar)
if not mos_aptekalar.empty:
    # 🧮 Guruhlash: dori nomi bo‘yicha necha aptekada va minimal narx
    guruhlangan = (
        mos_aptekalar
        .groupby(["Dori nomi"])
        .agg({
            "Apteka nomi": "count",
            "Narxi (taxminiy)": "min"
        })
        .reset_index()
        .rename(columns={
            "Apteka nomi": "Nechta dorixonada",
            "Narxi (taxminiy)": "Minimal narxi"
        })
    )
    
    # 🔢 Sahifalash parametrlari
    items_per_page = 5
    if "main_page" not in st.session_state:
        st.session_state["main_page"] = 0
    if "tanlangan_dori" not in st.session_state:
       st.session_state["tanlangan_dori"] = ""

    total_items = len(guruhlangan)
    total_pages = (total_items + items_per_page - 1) // items_per_page

    start_idx = st.session_state["main_page"] * items_per_page
    end_idx = min(start_idx + items_per_page, total_items)
    current_page_data = guruhlangan.iloc[start_idx:end_idx]

    drug_icon = get_base64_image("images/drug_icon.png")
    query_raw = st.session_state.get("tanlangan_dori", "")
    if isinstance(query_raw, dict):
        query = query_raw.get("name", "")
    elif isinstance(query_raw, str):
        query = query_raw.strip()
    else:
        query = str(query_raw).strip()
    natija = df[df["Dori nomi"] == query]

    # 🔳 Dori kartochkalari chiqarish
    for i, row in current_page_data.iterrows():
        dori_nomi = row["Dori nomi"]
        narx = row.get("Minimal narxi", "Nomaʼlum")
        nechta = row.get("Nechta dorixonada", 0)
        
        with st.container(border=True):
            st.markdown(f"""
                <div style="display: flex; align-items: center;
                            border-radius: 10px; padding: 20px;
                            font-size: 18px; margin-bottom: 10px;">
                    <img src="data:image/png;base64,{drug_icon}" width="60" height="60" style="margin-right: 20px;">
                    <div>
                        <b>{dori_nomi}</b><br>
                        <b>Narxi:</b> {narx} so‘mdan<br>
                        <b>✅ {nechta} ta dorixonada mavjud</b><br>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # 📍 Tugma orqali sahifani almashtirish
            
                # st.session_state["tanlangan_dori"] = dori_nomi
                # switch_page('pages/arzon')
            if st.button("📍 Dorixona ro‘yxati", key=f"dorixona_{i}", use_container_width=True):
                st.session_state["tanlangan_dori"] = dori_nomi
                st.switch_page("pages/locatsiya.py")
if not mos_aptekalar.empty:
   # Sahifa tugmalari uchun ustunlar
    col1, col2, col3, col4, col5,col6 = st.columns([2.1,1, 2, 0.5, 1.7, 1])

    with col2:
        if st.button("⬅️", key="prev_btn") and st.session_state["main_page"] > 0:
            st.session_state["main_page"] -= 1
            st.rerun()

    with col3:
        st.markdown(
            f"<div style='text-align: center; font-size: 18px;'><b>{st.session_state['main_page'] + 1} / {total_pages}</b></div>",
            unsafe_allow_html=True
        )

    with col5:
        if st.button("➡️", key="next_btn") and st.session_state["main_page"] < total_pages - 1:
            st.session_state["main_page"] += 1
            st.rerun()
