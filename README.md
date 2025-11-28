# Aziz AI 10.0 - Telegram bot

Bu bot `backend` servisdagi Aziz AI 10.0 bilan Telegram orqali gaplashish uchun.

## O'rnatish

```bash
cd telegram_bot
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
cp .env.example .env
```

`.env` ichida:

- `TELEGRAM_BOT_TOKEN` ni o'zingizning bot tokeniga almashtirasiz
- `BACKEND_BASE_URL` agar Railway yoki boshqa URL bo'lsa, o'shani qo'yasiz

## Ishga tushirish

```bash
python bot.py
```

Telegram'da:

1. `/start`
2. `/login email parol`
3. Keyin odatdagi xabar yuborasiz – backend'dagi Aziz AI 10.0 javob qaytaradi.
