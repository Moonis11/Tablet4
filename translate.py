import streamlit as st

# Til nomlari va kodlari
languages = {
    "Uzbek": "uz",
    "Русский": "ru",
    "English": "en",
    "Кирил": "kiril"
}

def init_language():
    """Tilni bir marta boshlanishida aniqlash"""
    if "lang" not in st.session_state:
        st.session_state["lang"] = "uz"

def language_selector_inline(key_suffix="inline"):
    """Til tanlash selectbox — zamonaviy dizayn bilan"""

    key = f"lang_selector_{key_suffix}"

    st.markdown("""
    <style>
    .language-float-box {
        position: fixed;
        top: 15px;
        right: 25px;
        z-index: 9999;
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(8px);
        border-radius: 12px;
        padding: 6px 12px;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.25);
        font-weight: 600;
    }

    .language-float-box label {
        color: white !important;
    }

    .stSelectbox > div > div {
        background-color: transparent !important;
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # # Til tanlash oynasi
    # with st.markdown('<div class="language-float-box">', unsafe_allow_html=True):
    #     selected = st.selectbox(
    #         "🌐",
    #         options=list(languages.keys()),
    #         index=list(languages.values()).index(st.session_state["lang"]),
    #         label_visibility="collapsed",
    #         key=key
    #     )
    # st.markdown('</div>', unsafe_allow_html=True)

    lang_box = st.columns([4, 1, 1])[2]
    with lang_box:
        selected = st.selectbox(
            "🌐",
            options=list(languages.keys()),
            index=list(languages.values()).index(st.session_state["lang"]),
            label_visibility="collapsed"            
        )
    # Faqat til o‘zgargan bo‘lsa, session_state yangilanadi va sahifa yangilanadi
    selected_lang_code = languages[selected]
    if selected_lang_code != st.session_state["lang"]:
        st.session_state["lang"] = selected_lang_code
        st.rerun()

def tr(key: str, lang: str = "uz") -> str:
    """Berilgan kalit va til bo‘yicha tarjimani qaytaradi"""
    return translations.get(key, {}).get(lang, key)


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
        "ru": "Дешевле",
        "en": " Cheap",
        "kiril": "Арзон"
    },
    "near": {
        "uz": "Yaqin",
        "ru": "Ближе",
        "en": "Close",
        "kiril": "Яқин"
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
    },
    "close_pharmacy": {
        "uz": "📍 Eng yaqin dorixona",
        "ru": "📍 Ближайшая аптека",
        "en": "📍 Nearest Pharmacy",
        "kiril": "📍 Энг яқин дорихона"
    },
    "get_location": {
        "uz": "📡 Joylashuvni olish",
        "ru": "📡 Получить локацию",
        "en": "📡 Get Location",
        "kiril": "📡 Жойлашувни олиш"
    },
    "not_detected": {
        "uz": "❗ Dori aniqlanmadi. Iltimos, asosiy sahifada rasm yuklang.",
        "ru": "❗ Лекарство не распознано. Пожалуйста, загрузите изображение на главной странице.",
        "en": "❗ Drug not detected. Please upload an image on the main page.",
        "kiril": "❗ Дори аниқланмади. Илтимос, асосий саҳифада расм юкланг."
    },
    "to_cart": {
    "uz": "🛒 Savatchaga o'tish",
    "ru": "🛒 Перейти в корзину",
    "en": "🛒 Go to Cart",
    "kiril": "🛒 Саватга ўтиш"
    },
    "go_payment": {
        "uz": "✅ To‘lovga o‘tish",
        "ru": "✅ Перейти к оплате",
        "en": "✅ Proceed to Payment",
        "kiril": "✅ Тўловга ўтиш"
    },
    "go_home": {
        "uz": "🏠 Bosh sahifa",
        "ru": "🏠 Главная",
        "en": "🏠 Home",
        "kiril": "🏠 Бош саҳифа"
    },
    "price": {"uz": "Narxi", "ru": "Цена", "en": "Price", "kiril": "Нархи"},
    "pharmacy": {"uz": "Dorixona", "ru": "Аптека", "en": "Pharmacy", "kiril": "Дорихона"},
    "address": {"uz": "Manzil", "ru": "Адрес", "en": "Address", "kiril": "Манзил"},
    "phone": {"uz": "Telefon", "ru": "Телефон", "en": "Phone", "kiril": "Телефон"},
    "distance": {"uz": "Masofa", "ru": "Расстояние", "en": "Distance", "kiril": "Масофа"},
    "time_found": {"uz": "Topilgan vaqt", "ru": "Время нахождения", "en": "Found time", "kiril": "Топилган вақт"},
    "add_to_cart": {"uz": "➕ Savatchaga qo‘shish", "ru": "➕ Добавить в корзину", "en": "➕ Add to cart", "kiril": "➕ Саватга қўшиш"},
    "added_success": {"uz": "✅ Dori savatchaga qo‘shildi!", "ru": "✅ Лекарство добавлено!", "en": "✅ Drug added!", "kiril": "✅ Дори қўшилди!"},
    "no_coords": {"uz": "❗ Dorixonalarda koordinatalar mavjud emas.", "ru": "❗ Нет координат аптек.", "en": "❗ No coordinates for pharmacies.", "kiril": "❗ Дорихоналарда координаталар йўқ."
},
    "price": {
    "uz": "💰 <b>Narxi:</b>",
    "ru": "💰 <b>Цена:</b>",
    "en": "💰 <b>Price:</b>",
    "kiril": "💰 <b>Нархи:</b>"
},
"pharmacy": {
    "uz": "🏥 <b>Dorixona:</b>",
    "ru": "🏥 <b>Аптека:</b>",
    "en": "🏥 <b>Pharmacy:</b>",
    "kiril": "🏥 <b>Дорихона:</b>"
},
"phone": {
    "uz": "📞 <b>Telefon:</b>",
    "ru": "📞 <b>Телефон:</b>",
    "en": "📞 <b>Phone:</b>",
    "kiril": "📞 <b>Телефон:</b>"
},
"distance": {
    "uz": "📍 <b>Masofa:</b>",
    "ru": "📍 <b>Расстояние:</b>",
    "en": "📍 <b>Distance:</b>",
    "kiril": "📍 <b>Масофа:</b>"
},
"found_time": {
    "uz": "🕒 <b>Topilgan:</b>",
    "ru": "🕒 <b>Найдено в:</b>",
    "en": "🕒 <b>Found:</b>",
    "kiril": "🕒 <b>Топилган:</b>"
},
"add_to_cart": {
    "uz": "➕ Savatchaga qo‘shish",
    "ru": "➕ Добавить в корзину",
    "en": "➕ Add to cart",
    "kiril": "➕ Саватга қўшиш"
},
"go_to_cart": {
    "uz": "🛒 Savatchaga o'tish",
    "ru": "🛒 Перейти в корзину",
    "en": "🛒 Go to cart",
    "kiril": "🛒 Саватга ўтиш"
},
"go_to_payment": {
    "uz": "✅ To‘lovga o‘tish",
    "ru": "✅ Перейти к оплате",
    "en": "✅ Go to payment",
    "kiril": "✅ Тўловга ўтиш"
},
"go_home": {
    "uz": "🏠 Bosh sahifa",
    "ru": "🏠 Главная",
    "en": "🏠 Home",
    "kiril": "🏠 Бош саҳифа"
},
"added_success": {
    "uz": "✅ Dori savatchaga qo‘shildi!",
    "ru": "✅ Лекарство добавлено в корзину!",
    "en": "✅ Drug added to cart!",
    "kiril": "✅ Дори саватга қўшилди!"
}, 
"drug_not_detected": {
    "uz": "Dori aniqlanmadi. Iltimos, asosiy sahifada rasm yuklang.",
    "ru": "Лекарство не распознано. Пожалуйста, загрузите изображение на главной странице.",
    "en": "Drug not detected. Please upload an image on the main page.",
    "kiril": "Дори аниқланмади. Илтимос, асосий саҳифада расм юкланг."
},
"not_found_exact": {
    "uz": "'{dori}' dorisi topilmadi.",
    "ru": "Лекарство '{dori}' не найдено.",
    "en": "'{dori}' not found.",
    "kiril": "'{dori}' дориси топилмади."
},
"new_search": {
    "uz": "🔁 Yangi buyurtma",
    "ru": "🔁 Новый поиск",
    "en": "🔁 New search",
    "kiril": "🔁 Янги буюртма"
},
"get_location": {
    "uz": "📡 Joylashuvni olish",
    "ru": "📡 Получить геолокацию",
    "en": "📡 Get location",
    "kiril": "📡 Жойлашувни олиш"
},
"gps_failed_ip_fallback": {
    "uz": "📵 GPS aniqlanmadi, IP orqali urinilmoqda...",
    "ru": "📵 GPS не определен, пробуем через IP...",
    "en": "📵 GPS not available, trying via IP...",
    "kiril": "📵 GPS аниқланмади, IP орқали уринилмоқда..."
},
"cheap_pharmacy": {
    "uz": "📍 Eng arzon dorixona",
    "ru": "📍 Самая дешевая аптека",
    "en": "📍 Cheapest Pharmacy",
    "kiril": "📍 Энг арзон дорихона"
},
"order_page"      : {
    "uz": "📋 Buyurtma ma'lumotlari",
    "ru": "📋 Информация о заказе",
    "en": "📋 Order details",
    "kiril": "📋 Буюртма маълумотлари"
},

# ‑‑‑ Form vidjetlari
"phone"           : {"uz": "📞 Telefon raqami",
                        "ru": "📞 Номер телефона",
                        "en": "📞 Phone number",
                        "kiril": "📞 Телефон рақами"},
"name"            : {"uz": "👤 Ism",
                        "ru": "👤 Имя",
                        "en": "👤 Name",
                        "kiril": "👤 Исм"},
"address"         : {"uz": "📍 To‘liq manzil",
                        "ru": "📍 Полный адрес",
                        "en": "📍 Full address",
                        "kiril": "📍 Тўлиқ манзил"},
"drug_list"       : {"uz": "📦 Dori nomlari",
                        "ru": "📦 Список лекарств",
                        "en": "📦 Drug list",
                        "kiril": "📦 Дори номлари"},
"drug_price"      : {"uz": "💰 Dorilar narxi",
                        "ru": "💰 Стоимость лекарств",
                        "en": "💰 Drug price",
                        "kiril": "💰 Дорилар нархи"},
"delivery_fee"    : {"uz": "🚚 Yetkazib berish xizmati",
                        "ru": "🚚 Доставка",
                        "en": "🚚 Delivery",
                        "kiril": "🚚 Еткaзиб бериш"},
"logistics_fee"   : {"uz": "📦 Logistika xizmati",
                        "ru": "📦 Логистика",
                        "en": "📦 Logistics",
                        "kiril": "📦 Логистика хизмати"},
"smart_service"   : {"uz": "🤖 AI xizmatlar",
                        "ru": "🤖 AI‑сервис",
                        "en": "🤖 AI services",
                        "kiril": "🤖 AI хизматлар"},
"total_pay"       : {"uz": "💰 Umumiy to‘lov",
                        "ru": "💰 Общая сумма",
                        "en": "💰 Total",
                        "kiril": "💰 Умумий тўлов"},
"confirm_order"   : {"uz": "✅ Buyurtmani tasdiqlash",
                        "ru": "✅ Подтвердить заказ",
                        "en": "✅ Confirm order",
                        "kiril": "✅ Буюртмани тасдиқлаш"},
"empty_cart"      : {"uz": "❗ Savatcha bo‘sh. Iltimos, dorilar qo‘shing.",
                        "ru": "❗ Корзина пуста. Добавьте лекарства.",
                        "en": "❗ Cart is empty. Add drugs.",
                        "kiril": "❗ Саватча бўш. Дорилар қўшинг."},
"split_done"      : {"uz": "💸 Pul taqsimoti amalga oshirildi:",
                        "ru": "💸 Распределение средств выполнено:",
                        "en": "💸 Money split completed:",
                        "kiril": "💸 Пул тақсимоти амалга оширилди:"},
"payments_ready"  : {"uz": "✅ Barcha to‘lovlar tayyor!",
                        "ru": "✅ Все платежи готовы!",
                        "en": "✅ All payments ready!",
                        "kiril": "✅ Барча тўловлар тайёр!"},
"price": {
    "uz": "Narxi",
    "ru": "Цена",
    "en": "Price",
    "kiril": "Нархи"
},
"pharmacy": {
    "uz": "Dorixona",
    "ru": "Аптека",
    "en": "Pharmacy",
    "kiril": "Дорихона"
},
"address": {
    "uz": "Lokatsiya",
    "ru": "Локация",
    "en": "Location",
    "kiril": "Локация"
},
"time_found": {
    "uz": "Qo‘shilgan vaqt",
    "ru": "Время добавления",
    "en": "Added time",
    "kiril": "Қўшилган вақт"
},"your_cart": {
    "uz": "🧺 Savatchangiz",
    "ru": "🧺 Ваша корзина",
    "en": "🧺 Your Cart",
    "kiril": "🧺 Саватчангиз"
},
"remove": {
    "uz": "❌ O‘chirish",
    "ru": "❌ Удалить",
    "en": "❌ Remove",
    "kiril": "❌ Ўчириш"
},
"back": {
    "uz": "⬅️ Orqaga qaytish",
    "ru": "⬅️ Назад",
    "en": "⬅️ Back",
    "kiril": "⬅️ Орқага қайтиш"
},
"checkout": {
    "uz": "✅ To‘lovga o‘tish",
    "ru": "✅ Перейти к оплате",
    "en": "✅ Proceed to Payment",
    "kiril": "✅ Тўловга ўтиш"
},
"cart_page": {
    "uz": "🧺 Savatcha",
    "ru": "🧺 Корзина",
    "en": "🧺 Cart",
    "kiril": "🧺 Саватча"
},
"unknown": {
    "uz": "Nomaʼlum",
    "ru": "Неизвестно",
    "en": "Unknown",
    "kiril": "Номаълум"
},
"go_home": {
    "uz": "Orqaga qaytish",
    "ru": "Назад",
    "en": "Back",
    "kiril": "Ортга қайтиш"
},
"go_payment": {
    "uz": "To‘lovga o‘tish",
    "ru": "Перейти к оплате",
    "en": "Go to payment",
    "kiril": "Тўловга ўтиш"
},
"new_order": {
    "uz": "🛒 Yangi buyurtma",
    "ru": "🛒 Новый заказ",
    "en": "🛒 New order",
    "kiril": "🛒 Янги буюртма"
},
     "history_title": {
        "uz": "Oxirgi dori izlanmalari",
        "ru": "Последние поиски",
        "kiril": "Охирги дори изланмалари",
        "en": "Recent drug searches"
    },
    "no_history": {
        "uz": "❗ Hozircha hech qanday dori izlanmadi.",
        "ru": "❗ Пока что нет поисков.",
        "kiril": "❗ Ҳозирча ҳеч қандай дори изланмади.",
        "en": "❗ No drug searches yet."
    },
    "home": {
        "uz": "Bosh sahifa",
        "ru": "Главная",
        "kiril": "Бош саҳифа",
        "en": "Home"
    },
    "csv_load_error": {
        "uz": "Apteka CSV faylini yuklashda xatolik yuz berdi.",
        "ru": "Ошибка при загрузке CSV файла аптеки.",
        "kiril": "Аптека CSV файлини юклашда хатолик юз берди.",
        "en": "Error loading the pharmacy CSV file."
    },
    "unknown": {
        "uz": "Nomaʼlum",
        "ru": "Неизвестно",
        "kiril": "Номаълум",
        "en": "Unknown"
    },
    "currency": {
        "uz": "so'm",
        "ru": "сум",
        "kiril": "сўм",
        "en": "UZS"
    },
       "total": {
        "uz": "Umumiy",
        "ru": "Итого",
        "kiril": "Умумий",
        "en": "Total"
    },
    "order_completed_title": {
    "uz": "✅ To‘lov yakunlandi",
    "ru": "✅ Оплата завершена",
    "en": "✅ Payment completed",
    "kiril": "✅ Тўлов якунланди"
},
"not_enough_data": {
    "uz": "❗️ Ma’lumotlar yetarli emas. Bosh sahifaga qayting.",
    "ru": "❗️ Недостаточно данных. Вернитесь на главную.",
    "en": "❗️ Not enough data. Go back to the home page.",
    "kiril": "❗️ Маълумотлар етарли эмас. Бош саҳифага қайтинг."
},
"order_saved": {
    "uz": "✅ Buyurtma saqlandi va to‘lov qabul qilindi.",
    "ru": "✅ Заказ сохранён и оплата принята.",
    "en": "✅ Order saved and payment received.",
    "kiril": "✅ Буюртма сақланди ва тўлов қабул қилинди."
},
"qr_caption": {
    "uz": "To‘lov uchun QR kod",
    "ru": "QR‑код для оплаты",
    "en": "QR code for payment",
    "kiril": "Тўлов учун QR коди"
},
"order_id":  {"uz": "Buyurtma ID", "ru": "ID заказа", "en": "Order ID", "kiril": "Буюртма ID"},
"user":      {"uz": "Foydalanuvchi", "ru": "Пользователь", "en": "User", "kiril": "Фойдаланувчи"},
"drug":      {"uz": "Dori", "ru": "Лекарство", "en": "Drug", "kiril": "Дори"},
"tg_message": {
    "uz": "📦 <b>Yangi buyurtma</b>\nℹ️ Buyurtma ID: <code>{id}</code>\n👤 {name}\n {phone}\n📍 {loc}\n💊 {drug}\n {total}",
    "ru": "📦 <b>Новый заказ</b>\nℹ️ ID: <code>{id}</code>\n👤 {name}\ {phone}\n📍 {loc}\n💊 {drug}\n {total}",
    "en": "📦 <b>New order</b>\nℹ️ ID: <code>{id}</code>\n👤 {name}\n{phone}\n📍 {loc}\n💊 {drug}\n {total}",
    "kiril": "📦 <b>Янги буюртма</b>\nℹ️ ID: <code>{id}</code>\n👤 {name}\n {phone}\n📍 {loc}\n💊 {drug}\n {total}"
},
"tg_fail": {
    "uz": "Telegramga yuborib bo‘lmadi.",
    "ru": "Не удалось отправить в Telegram.",
    "en": "Failed to send to Telegram.",
    "kiril": "Telegram'га юбориб бўлмади."
},
 "title": {
            "uz": "🧪 Tablet AI", "ru": "🧪 Таблет AI", "en": "🧪 Tablet AI", "kiril": "🧪 Таблет AI"
        },
        "desc": {
            "uz": "📷 Rasm, 🎤 ovoz yoki ✍️ yozuv –\no‘zingizga qulayini tanlang.",
            "kiril": "📷 Расм, 🎤 овоз ёки ✍️ ёзув –\nўзингизга қулайини танланг.",
            "ru": "📷 Фото, 🎤 голос или ✍️ текст –\nвыберите, как вам удобно.",
            "en": "📷 Image, 🎤 voice, or ✍️ text –\nchoose what’s easiest for you."
            },
        "upload_image": {
            "uz": "📷 rasmni yuklash", "ru": "📷",
            "en": "📷", "kiril": "📷"
        },
        "voice_input": {
            "uz": "🎙️ ovoz yozish", "ru": "🎙️",
            "en": "🎙️", "kiril": "🎙️"
        },
        "manual_input": {
            "uz": "✍️ qo`l orqali", "ru": "✍️",
            "en": "✍️", "kiril": "✍️"
        },
                
        "your_location": {
            "uz": "📍 Manzil",
            "ru": "📍 Адрес",
            "en": "📍 Location",
            "kiril": "📍 Манзил"
        },
        "top_cheap_list": {
    "uz": "⬇️ Eng arzon 20 ta dorixona",
    "ru": "⬇️ Топ-20 дешевых аптек",
    "en": "⬇️ Top 20 Cheapest Pharmacies",
    "uzb-kiril": "⬇️ Энг арзон 20 та дорихона"
},
    "expiry_date": {
        "uz": "Yaroqlilik muddati",
        "ru": "Срок годности",
        "en": "Expiry date",
        "kr": "Яроқлик муддати"
    },
    "in_stock": {
        "uz": "Omborda mavjudligi",
        "ru": "Наличие на складе",
        "en": "In stock",
        "kr": "Омборда мавжудлиги"
    },
     "shu_faol_modda_dorilar": {
        "uz": "Shu faol modda bilan dorilar",
        "ru": "Лекарства с тем же действующим веществом",
        "en": "Drugs with the same active ingredient"
    }


}







