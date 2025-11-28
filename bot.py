from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests
from config import BOT_TOKEN, BACKEND_URL

# /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Assalomu alaykum! Aziz AI 10.0 Telegram yordamchisiga xush kelibsiz.\n"
        "Menga xabar yuboring."
    )

# Matnli xabarlarni qayta ishlash
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text

    payload = {
        "user_id": str(user_id),
        "message": text
    }

    try:
        r = requests.post(f"{BACKEND_URL}/chat/send", json=payload, timeout=20)
        data = r.json()

        reply = data.get("reply", "⚠ Backenddan javob olinmadi.")
        await update.message.reply_text(reply)

    except Exception as e:
        await update.message.reply_text("❌ Server bilan ulanishda xatolik yuz berdi.")

# Botni ishga tushirish
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot ishga tushdi...")
    app.run_polling()

if __name__ == "__main__":
    main()
