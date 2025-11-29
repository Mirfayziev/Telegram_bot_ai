import requests
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from config import BOT_TOKEN, BACKEND_URL, BOT_LOGIN_EMAIL, BOT_LOGIN_PASSWORD

access_token: str | None = None


def get_headers():
    global access_token
    headers = {"Content-Type": "application/json"}
    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"
    return headers


def backend_login() -> bool:
    global access_token

    url = f"{BACKEND_URL}/login"

    payload = {
        "email": BOT_LOGIN_EMAIL,
        "password": BOT_LOGIN_PASSWORD,
    }

    try:
        resp = requests.post(url, json=payload, timeout=20)

        if resp.status_code != 200:
            print("Backend login failed:", resp.status_code, resp.text)
            return False

        data = resp.json()
        token = data.get("access_token")
        if not token:
            print("Backend login response missing access_token:", data)
            return False

        access_token = token
        print("Backend login successful")
        return True

    except Exception as e:
        print("Backend login exception:", e)
        return False


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Assalomu alaykum! Aziz AI 10.0 Telegram yordamchisiga xush kelibsiz."
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global access_token

    user_id = update.message.from_user.id
    text = update.message.text

    if not access_token:
        if not backend_login():
            await update.message.reply_text("❌ Backend login bo'lmadi.")
            return

    payload = {"user_id": str(user_id), "message": text}

    try:
        url = f"{BACKEND_URL}/chat/send"

        resp = requests.post(url, json=payload, headers=get_headers(), timeout=30)

        if resp.status_code == 401:
            if backend_login():
                resp = requests.post(url, json=payload, headers=get_headers(), timeout=30)
            else:
                await update.message.reply_text("❌ Auth xatosi.")
                return

        if resp.status_code != 200:
            await update.message.reply_text(f"❌ Backend xato: {resp.status_code}")
            print(resp.text)
            return

        reply = resp.json().get("reply") or "⚠ Javob topilmadi."
        await update.message.reply_text(reply)

    except Exception as e:
        print("Bot exception:", e)
        await update.message.reply_text("❌ Serverga ulanishda xato.")


def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Bot running...")
    app.run_polling()


if __name__ == "__main__":
    main()
