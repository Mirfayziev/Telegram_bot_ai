import os
import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# ==============================================
# LOGGING
# ==============================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - BOT - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# ==============================================
# CONFIG
# ==============================================
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BACKEND_URL = os.getenv("BACKEND_URL")

if not BOT_TOKEN:
    logger.error("❌ TELEGRAM_BOT_TOKEN topilmadi!")
    raise SystemExit

if not BACKEND_URL:
    logger.error("❌ BACKEND_URL topilmadi!")
    raise SystemExit

API_LOGIN = f"{BACKEND_URL}/api/v1/auth/login"
API_REGISTER = f"{BACKEND_URL}/api/v1/auth/register"
API_CHAT = f"{BACKEND_URL}/api/v1/chat/send"

BOT_EMAIL = "bot@azizai.com"
BOT_PASSWORD = "supersecretpassword123"

# ==============================================
# BACKEND FUNCTIONS
# ==============================================
def backend_register():
    try:
        r = requests.post(API_REGISTER, json={
            "email": BOT_EMAIL,
            "full_name": "Telegram Bot",
            "password": BOT_PASSWORD
        })

        if r.status_code == 200:
            logger.info("🟢 Bot backendda ro'yxatdan o'tdi.")
            return True

        if r.status_code == 400:
            logger.info("ℹ️ Bot foydalanuvchi allaqachon mavjud.")
            return True

        logger.error(f"❌ Register error: {r.status_code} {r.text}")
        return False

    except Exception as e:
        logger.error(f"❌ Register exception: {e}")
        return False


def backend_login():
    try:
        r = requests.post(API_LOGIN, json={
            "email": BOT_EMAIL,
            "password": BOT_PASSWORD
        })

        if r.status_code == 200:
            logger.info("🟢 Backend login OK.")
            return r.json().get("access_token")

        logger.error(f"❌ Login error: {r.status_code} {r.text}")
        return None

    except Exception as e:
        logger.error(f"❌ Login exception: {e}")
        return None


# ==============================================
# HANDLERS
# ==============================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Assalomu alaykum! Aziz AI 10.0 Telegram yordamchisiga xush kelibsiz."
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    token = backend_login()
    if not token:
        await update.message.reply_text("❌ Backend bilan aloqa bo‘lmadi.")
        return

    headers = {"Authorization": f"Bearer {token}"}

    try:
        r = requests.post(API_CHAT, json={"message": user_text}, headers=headers)

        if r.status_code == 200:
            reply = r.json().get("reply", "❌ Javob topilmadi.")
            await update.message.reply_text(reply)
        else:
            await update.message.reply_text("❌ Backend xatosi.")
    except Exception as e:
        logger.error(e)
        await update.message.reply_text("❌ Xatolik yuz berdi.")


# ==============================================
# MAIN (SYNC, TO‘G‘RI VARIANT)
# ==============================================
def main():
    logger.info("🚀 Bot starting...")

    backend_register()

    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("🟢 Bot polling started.")
    application.run_polling()


if __name__ == "__main__":
    main()
