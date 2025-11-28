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

# Global token (bot uchun backend JWT)
access_token: str | None = None


def get_headers() -> dict:
    """Backendga so'rov yuborish uchun header."""
    global access_token
    headers = {"Content-Type": "application/json"}
    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"
    return headers


def backend_login() -> bool:
    """
    Bot uchun backendga login bo'ladi.
    Muvaffaqiyatli bo'lsa access_token global o'zgaruvchiga yoziladi.
    """
    global access_token

    url = f"{BACKEND_URL}/auth/login"
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
        # Ko'p JWT authlarda 'access_token' maydoni bo'ladi
        token = data.get("access_token")
        if not token:
            print("Backend login response missing 'access_token':", data)
            return False

        access_token = token
        print("Backend login successful")
        return True

    except Exception as e:
        print("Backend login exception:", e)
        return False


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Assalomu alaykum! Aziz AI 10.0 Telegram yordamchisiga xush kelibsiz.\n"
        "Menga xabar yuboring."
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global access_token

    user_id = update.message.from_user.id
    text = update.message.text

    # Agar token hali olinmagan bo'lsa – login qilib ko'ramiz
    if not access_token:
        ok = backend_login()
        if not ok:
            await update.message.reply_text("❌ Backendga login bo'lmadi.")
            return

    payload = {
        "user_id": str(user_id),
        "message": text,
    }

    try:
        url = f"{BACKEND_URL}/chat/send"
        resp = requests.post(url, json=payload, headers=get_headers(), timeout=30)

        # Agar token eskirib qolgan bo'lsa yoki noto'g'ri bo'lsa – qayta login
        if resp.status_code == 401:
            # Yangi login
            if backend_login():
                resp = requests.post(
                    url, json=payload, headers=get_headers(), timeout=30
                )
            else:
                await update.message.reply_text("❌ Auth xatosi (401).")
                return

        if resp.status_code != 200:
            await update.message.reply_text(
                f"❌ Backend xato qaytardi: {resp.status_code}"
            )
            print("Backend error:", resp.status_code, resp.text)
            return

        data = resp.json()
        reply = data.get("reply") or data.get("response") or "⚠ Javob topilmadi."

        await update.message.reply_text(reply)

    except Exception as e:
        print("Exception while calling backend:", e)
        await update.message.reply_text("❌ Server bilan ulanishda xato.")


def main():
    if not BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN topilmadi!")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Telegram bot is running (Aziz AI 10.0)...")
    app.run_polling()


if __name__ == "__main__":
    main()
