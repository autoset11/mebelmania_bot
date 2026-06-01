import json
import os
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiohttp import web

TOKEN = os.environ.get("BOT_TOKEN", "8713840490:AAGO7oPvw71p64nCoajRaztCizvDq9IYm40")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "405947113"))
LINK_TELEGRAM = "https://t.me/mebelmania56"

stats_file = "stats.json"

def load_stats():
    if os.path.exists(stats_file):
        with open(stats_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_stats(stats):
    with open(stats_file, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

stats = load_stats()
bot = Bot(token=TOKEN)
dp = Dispatcher()

def get_telegram_button():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📱 Перейти в Telegram-канал", url=LINK_TELEGRAM)]
        ]
    )

@dp.message(CommandStart(deep_link=True))
async def start_with_payload(message: types.Message):
    text = message.text
    payload = text.replace("/start", "").strip()
    if payload.startswith(" "):
        payload = payload[1:]
    if not payload:
        payload = "direct"
    
    user_id = str(message.from_user.id)
    username = message.from_user.username or "без_username"
    first_name = message.from_user.first_name
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if payload not in stats:
        stats[payload] = []
    
    stats[payload].append({
        "user_id": user_id,
        "username": username,
        "first_name": first_name,
        "timestamp": timestamp
    })
    save_stats(stats)
    
    await message.answer(
        f"👋 Спасибо, {first_name}!\n\n"
        f"Спасибо за переход по QR коду! Тут вы сможете узнавать обо всех акциях первыми!\n\n"
        f"👇 Нажмите на кнопку, чтобы перейти:",
        reply_markup=get_telegram_button()
    )
    
    try:
        await bot.send_message(ADMIN_ID, f"🆕 Новый переход!\n👤 {first_name} (@{username})\n🏷️ Метка: {payload}")
    except:
        pass

@dp.message(CommandStart())
async def start_regular(message: types.Message):
    await message.answer(
        f"👋 Спасибо, {message.from_user.first_name}!\n\n"
        f"Спасибо за переход по QR коду! Тут вы сможете узнавать обо всех акциях первыми!\n\n"
        f"👇 Нажмите на кнопку, чтобы перейти:",
        reply_markup=get_telegram_button()
    )

@dp.message(Command("stats"))
async def show_stats(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ Нет доступа.")
        return
    
    if not stats:
        await message.answer("📊 Статистики пока нет.")
        return
    
    result = "📊 СТАТИСТИКА ПЕРЕХОДОВ:\n\n"
    total = 0
    for payload, users in sorted(stats.items(), key=lambda x: len(x[1]), reverse=True):
        count = len(users)
        total += count
        result += f"🔹 {payload}: {count} чел.\n"
    result += f"\n📈 ВСЕГО: {total}"
    await message.answer(result)

# Webhook обработчик
async def webhook(request):
    update = await request.json()
    await dp.feed_update(bot, types.Update(**update))
    return web.Response()

async def on_startup():
    webhook_url = f"https://mebelmania-bot.onrender.com/webhook"
    await bot.set_webhook(webhook_url)
    print(f"✅ Webhook установлен: {webhook_url}")

async def on_shutdown():
    await bot.delete_webhook()

# Запуск
app = web.Application()
app.router.add_post("/webhook", webhook)
app.router.add_get("/", lambda r: web.Response(text="OK"))

if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
