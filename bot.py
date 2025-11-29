import os
import logging
import asyncio
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

# To‘liq backend URL misol:
# https://aimaksimal-production.up.railway.app
API_LOGIN = f"{BACKEND_URL}/api/v1/auth/login"
API_REGISTER = f"{BACKEND_URL}/api/v1/auth/register"
API_CHAT = f"{BACKEND_URL}/api/v1/chat/send"

# ==============================================
# Auto Register + Auto Login
# ==============================================
BOT_EMAIL = "bot@azizai.com"
BOT_PASSWORD = "supersecretpassword123"


async def backend_register():
    try:
        response = requests.post(API_REGISTER, json={
            "email": BOT_EMAIL,
            "full_name": "Telegram Bot",
            "password": BOT_PASSWORD
        })

        if response.status_code == 200:
            logger.info("🟢 Backendda yangi bot foydalanuvchi yaratildi.")
            return True
        elif response.status_code == 400:
            logger.info("ℹ️ Bot foydalanuvchisi allaqachon mavjud.")
            return True
        else:
            logger.error(f"❌ Register error: {response.status_code} {response.text}")
            return False

    except Exception as e:
        logger.error(f"❌ Register exception: {e}")
        return False


async def backend_login():
    try:
        response = requests.post(API_LOGIN, json={
            "email": BOT_EMAIL,
            "password": BOT_PASSWORD
        })

        if response.status_code == 200:
            token = response.json().get("access_token")
            logger.info("🟢 Backend login muvaffaqiyatli.")
            return token

        logger.error(f"❌ Login error: {response.status_code} {response.text}")
        return None

    except Exception as e:
        logger.error(f"❌ Login exception: {e}")
        return None


# ==============================================
# Handlers
# ==============================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Assalomu alaykum! Aziz AI 10.0 Telegram yordamchisiga xush kelibsiz.\n"
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    # Backend tokenni olish
    token = await backend_login()
    if not token:
        await update.message.reply_text("❌ Backend bilan aloqa o‘rnatilmadi.")
        return

    headers = {"Authorization": f"Bearer {token}"}

    # Backendga so‘rov jo‘natish
    try:
        response = requests.post(API_CHAT, json={"message": user_text}, headers=headers)

        if response.status_code == 200:
            bot_reply = response.json().get("reply", "❌ Javob topilmadi.")
            await update.message.reply_text(bot_reply)
        else:
            await update.message.reply_text("❌ Backend javob bermadi.")

    except Exception as e:
        await update.message.reply_text("❌ Xatolik yuz berdi.")
        logger.error(f"Chat error: {e}")


# ==============================================
# MAIN
# ==============================================
async def main():
    logger.info("🚀 Bot starting...")

    # Avval register → keyin login
    await backend_register()

    # Telegram botni ishga tushirish
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("🟢 Bot polling started.")
    await app.run_polling()


if __name__ == "__main__":
    asyncio.run(main())
