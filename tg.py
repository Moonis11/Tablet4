from fastapi import FastAPI, Request, HTTPException
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Misol: https://sizningdomeningiz.com/webhook

app = FastAPI()
application = ApplicationBuilder().token(BOT_TOKEN).build()

# /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🇺🇿 Uzbek", callback_data="lang_uz")],
        [InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")],
        [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "👋 Tilni tanlang / Choose language / Выберите язык:",
        reply_markup=reply_markup
    )

# Callback query handler
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "lang_uz":
        text = "Assalomu alaykum! Til uzbekcha tanlandi."
    elif data == "lang_ru":
        text = "Здравствуйте! Выбран русский язык."
    elif data == "lang_en":
        text = "Hello! English language selected."
    else:
        text = "Noma'lum tanlov."

    await query.edit_message_text(text=text)

# Handlerlarni qo‘shamiz
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(button_handler))

@app.post("/webhook")
async def telegram_webhook(request: Request):
    try:
        data = await request.json()
    except Exception as e:
        print("JSON parsing error:", e)
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    try:
        update = Update.de_json(data, application.bot)
        await application.process_update(update)
        return {"ok": True}
    except Exception as e:
        print("Error processing Telegram update:", e)
        raise HTTPException(status_code=500, detail="Failed to process Telegram update")

@app.on_event("startup")
async def on_startup():
    if WEBHOOK_URL:
        await application.bot.set_webhook(WEBHOOK_URL)
        print(f"Webhook o‘rnatildi: {WEBHOOK_URL}")
    else:
        print("WEBHOOK_URL o‘rnatilmagan!")

# Bu kodni ishga tushirish uchun terminalda:
# uvicorn tg:app --host 0.0.0.0 --port 8000
# deb yozing (agar fayl nomi tg.py bo‘lsa)
