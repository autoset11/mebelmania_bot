import json
import os
from datetime import datetime, timedelta
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
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📱 Перейти в Telegram-канал", url=LINK_TELEGRAM)]
        ]
    )
    return keyboard

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
    
    # ОТЛАДКА: пишем в консоль Render
    print(f"🔍 Получен переход: метка={payload}, пользователь={user_id}, время={timestamp}")
    
    if payload not in stats:
        stats[payload] = []
    
    stats[payload].append({
        "user_id": user_id,
        "username": username,
        "first_name": first_name,
        "timestamp": timestamp
    })
    save_stats(stats)
    
    # ОТЛАДКА: сколько всего записей
    total = sum(len(v) for v in stats.values())
    print(f"📊 Всего записей в статистике: {total}")
    
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

# ========== СТАТИСТИКА ==========

@dp.message(Command("stats"))
async def show_stats_all(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ Нет доступа.")
        return
    
    if not stats:
        await message.answer("📊 Статистики пока нет.")
        return
    
    result = "📊 ВСЯ СТАТИСТИКА:\n\n"
    total = 0
    for payload, users in sorted(stats.items(), key=lambda x: len(x[1]), reverse=True):
        count = len(users)
        total += count
        result += f"🔹 {payload}: {count} чел.\n"
    result += f"\n📈 ВСЕГО: {total}"
    await message.answer(result)

@dp.message(Command("stats_week"))
async def show_stats_week(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ Нет доступа.")
        return
    
    week_ago = datetime.now() - timedelta(days=7)
    
    result = "📊 СТАТИСТИКА ЗА НЕДЕЛЮ:\n\n"
    total = 0
    week_stats = {}
    
    for payload, users in stats.items():
        week_users = [u for u in users if datetime.strptime(u['timestamp'], "%Y-%m-%d %H:%M:%S") >= week_ago]
        if week_users:
            week_stats[payload] = week_users
            total += len(week_users)
    
    if not week_stats:
        await message.answer("📊 За неделю статистики пока нет.")
        return
    
    for payload, users in sorted(week_stats.items(), key=lambda x: len(x[1]), reverse=True):
        result += f"🔹 {payload}: {len(users)} чел.\n"
    result += f"\n📈 ВСЕГО за неделю: {total}"
    await message.answer(result)

@dp.message(Command("stats_month"))
async def show_stats_month(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ Нет доступа.")
        return
    
    month_ago = datetime.now() - timedelta(days=30)
    
    result = "📊 СТАТИСТИКА ЗА МЕСЯЦ:\n\n"
    total = 0
    month_stats = {}
    
    for payload, users in stats.items():
        month_users = [u for u in users if datetime.strptime(u['timestamp'], "%Y-%m-%d %H:%M:%S") >= month_ago]
        if month_users:
            month_stats[payload] = month_users
            total += len(month_users)
    
    if not month_stats:
        await message.answer("📊 За месяц статистики пока нет.")
        return
    
    for payload, users in sorted(month_stats.items(), key=lambda x: len(x[1]), reverse=True):
        result += f"🔹 {payload}: {len(users)} чел.\n"
    result += f"\n📈 ВСЕГО за месяц: {total}"
    await message.answer(result)

@dp.message(Command("stats_period"))
async def show_stats_period(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ Нет доступа.")
        return
    
    try:
        parts = message.text.split()
        if len(parts) != 3:
            await message.answer("❌ Использование: /stats_period ГГГГ-ММ-ДД ГГГГ-ММ-ДД\nПример: /stats_period 2026-05-01 2026-06-01")
            return
        
        start_date = datetime.strptime(parts[1], "%Y-%m-%d")
        end_date = datetime.strptime(parts[2], "%Y-%m-%d")
        
        if start_date > end_date:
            await message.answer("❌ Первая дата не может быть позже второй.")
            return
        
    except ValueError:
        await message.answer("❌ Неверный формат даты. Используйте ГГГГ-ММ-ДД\nПример: /stats_period 2026-05-01 2026-06-01")
        return
    
    result = f"📊 СТАТИСТИКА ЗА ПЕРИОД:\n{start_date.strftime('%d.%m.%Y')} — {end_date.strftime('%d.%m.%Y')}\n\n"
    total = 0
    period_stats = {}
    
    for payload, users in stats.items():
        period_users = []
        for u in users:
            user_date = datetime.strptime(u['timestamp'], "%Y-%m-%d %H:%M:%S")
            if start_date <= user_date <= end_date:
                period_users.append(u)
        
        if period_users:
            period_stats[payload] = period_users
            total += len(period_users)
    
    if not period_stats:
        await message.answer(f"📊 За период {start_date.strftime('%d.%m.%Y')} — {end_date.strftime('%d.%m.%Y')} статистики нет.")
        return
    
    for payload, users in sorted(period_stats.items(), key=lambda x: len(x[1]), reverse=True):
        result += f"🔹 {payload}: {len(users)} чел.\n"
    result += f"\n📈 ВСЕГО: {total}"
    
    await message.answer(result)

# ========== ВЕБХУК И ЗАПУСК ==========

async def webhook(request):
    update = await request.json()
    await dp.feed_update(bot, types.Update(**update))
    return web.Response()

async def on_startup():
    await bot.delete_webhook()
    webhook_url = "https://mebelmania-bot.onrender.com/webhook"
    await bot.set_webhook(webhook_url)
    print(f"✅ Webhook set to {webhook_url}")

app = web.Application()
app.router.add_post("/webhook", webhook)
app.router.add_get("/", lambda r: web.Response(text="Bot is running"))

async def main():
    await on_startup()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", int(os.environ.get("PORT", 10000)))
    await site.start()
    print(f"🚀 Server started on port {int(os.environ.get('PORT', 10000))}")
    await asyncio.Future()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
