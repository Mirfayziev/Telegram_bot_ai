import logging
import os
from dotenv import load_dotenv
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BACKEND_API_BASE = os.getenv("BACKEND_API_BASE", "http://127.0.0.1:8000/api/v1")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Simple in-memory token storage for demo (per chat)
user_tokens = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Salom! Men Aziz AI 10.0 Telegram yordamchiman.\n"
        "Avval backendda ro'yxatdan o'tib, login tokenni /settoken bilan yubor."
    )

async def settoken(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Foydalanish: /settoken YOUR_JWT_TOKEN")
        return
    token = context.args[0]
    chat_id = update.effective_chat.id
    user_tokens[chat_id] = token
    await update.message.reply_text("✅ Token saqlandi. Endi oddiy xabar yuborsang, Aziz AI javob beradi.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    token = user_tokens.get(chat_id)
    if not token:
        await update.message.reply_text("Avval /settoken bilan JWT token yubor.")
        return

    text = update.message.text or ""
    try:
        resp = requests.post(
            f"{BACKEND_API_BASE}/chat/send",
            json={"content": text},
            headers={"Authorization": f"Bearer {token}"},
            timeout=15,
        )
        if resp.status_code != 200:
            await update.message.reply_text(f"Backend xato: {resp.status_code} {resp.text}")
            return
        data = resp.json()
        reply = data.get("content", "Javob kelmadi.")
        await update.message.reply_text(reply)
    except Exception as e:
        logger.exception("Error talking to backend")
        await update.message.reply_text(f"Xatolik: {e}")

def main():
    if not TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN env o'rnatilmagan")
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("settoken", settoken))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()

if __name__ == "__main__":
    main()
