import os
import logging
import requests
import sys
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    ContextTypes,
    filters,
)

# ================================
#  LOGGING
# ================================
logging.basicConfig(
    format="%(asctime)s - BOT - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ================================
#  CONFIG
# ================================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BACKEND_URL = os.getenv("BACKEND_URL", "https://aimaksimal-production.up.railway.app")

# Bot user login credentials (auto-register ishlatadi)
BOT_LOGIN_EMAIL = os.getenv("BOT_LOGIN_EMAIL", "bot@telegram.user")
BOT_LOGIN_PASSWORD = os.getenv("BOT_LOGIN_PASSWORD", "azizai")

# Global token
access_token = None


# ================================
#  BACKEND LOGIN
# ================================
def backend_login() -> bool:
    """Backendga login qilish."""
    global access_token

    url = f"{BACKEND_URL}/auth/login"
    payload = {
        "email": BOT_LOGIN_EMAIL,
        "password": BOT_LOGIN_PASSWORD
    }

    try:
        resp = requests.post(url, json=payload, timeout=20)

        if resp.status_code == 401:
            logger.warning("User not found. Auto-registering...")
            return backend_register()

        if resp.status_code != 200:
            logger.error(f"Login failed [{resp.status_code}]: {resp.text}")
            return False

        data = resp.json()
        access_token = data.get("access_token")

        if not access_token:
            logger.error(f"Login response missing token: {data}")
            return False

        logger.info("Backend login successful")
        return True

    except Exception as e:
        logger.error(f"Login exception: {e}")
        return False


# ================================
#  AUTO REGISTER
# ================================
def backend_register() -> bool:
    """Agar user bo‘lmasa — auto register."""
    url = f"{BACKEND_URL}/auth/register"
    payload = {
        "full_name": "AzizAI Telegram User",
        "email": BOT_LOGIN_EMAIL,
        "password": BOT_LOGIN_PASSWORD,
    }

    try:
        resp = requests.post(url, json=payload, timeout=20)

        if resp.status_code not in [200, 201]:
            logger.error(f"Auto-register failed [{resp.status_code}]: {resp.text}")
            return False

        logger.info("User auto-registered!")
        return backend_login()

    except Exception as e:
        logger.error(f"Register exception: {e}")
        return False


# ================================
#  SEND MESSAGE TO AI BACKEND
# ================================
def ask_backend_ai(message: str) -> str:
    """Backendga AI so‘rovi yuboradi."""
    global access_token

    if not access_token:
        if not backend_login():
            return "❌ Backend bilan ulanishda xatolik."

    url = f"{BACKEND_URL}/chat/send"

    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        payload = {"message": message}

        resp = requests.post(url, json=payload, headers=headers, timeout=25)

        # Token eskirgan bo‘lsa → qayta login
        if resp.status_code == 401:
            logger.warning("Token expired, relogin...")
            backend_login()
            return ask_backend_ai(message)

        if resp.status_code != 200:
            logger.error(f"Chat failed [{resp.status_code}]: {resp.text}")
            return "❌ AI server javob qaytarmadi."

        data = resp.json()
        return data.get("response", "❌ Javob topilmadi.")

    except Exception as e:
        logger.error(f"AI exception: {e}")
        return "❌ AI bilan ulanishda xatolik."


# ================================
#  HANDLERS
# ================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Assalomu alaykum! Aziz AI 10.0 yordamchisiga xush kelibsiz.\n"
        "Menga xohlagan savolingizni yuboring."
    )


async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text

    response = ask_backend_ai(user_message)

    await update.message.reply_text(response)


# ================================
#  MAIN
# ================================
def main():
    if not TELEGRAM_TOKEN:
        logger.error("❌ TELEGRAM_BOT_TOKEN topilmadi!")
        sys.exit()

    logger.info("Bot starting...")

    # Ishga tushayotganda backendga login
    backend_login()

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    logger.info("Bot polling started.")
    app.run_polling()


if __name__ == "__main__":
    main()
