import logging
import asyncio
import httpx
import random
import os
import re
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from PIL import Image, ImageDraw

# --- КОНФИГУРАЦИЯ ---
API_TOKEN = '8686353635:AAHzwPvTVHvgaB3RdBMXgwYnw8FupK9bi30'
ADMIN_URL = "https://t.me/softpack1977" 
SECRET_CODE = "hackpack1977"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

premium_users = set()

class AuthState(StatesGroup):
    waiting_for_code = State()

# --- ВАЛИДАТОРЫ ---
def is_ip(text):
    return bool(re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", text))

def is_email(text):
    return bool(re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", text))

# --- ГЕНЕРАТОР ДОСЬЕ (PREMIUM) ---
def generate_elite_dossier(target):
    img = Image.new('RGB', (600, 350), color=(5, 5, 5))
    draw = ImageDraw.Draw(img)
    chars = "ABEKMHOPCTYX"
    car_id = f"{random.choice(chars)}{random.randint(100,999)}{random.choice(chars)}{random.choice(chars)} {random.choice(['77','99','777','197'])}"
    lat, lon = f"{random.uniform(55.5, 55.9):.6f}", f"{random.uniform(37.3, 37.8):.6f}"
    
    gold = (255, 215, 0)
    text = (f"TARGET ID: {target}\n"
            f"---------------------------\n"
            f"REGION: RUS [77]\n"
            f"VEHICLE: {car_id}\n"
            f"GPS LOCK: {lat}, {lon}\n"
            f"STATUS: TRACKING...")
    draw.text((30, 30), text, fill=gold)
    draw.rectangle([5, 5, 595, 345], outline=gold, width=2)
    path = f"d_{target}.png"
    img.save(path)
    return path, lat, lon

# --- ОБРАБОТЧИКИ ---

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="💳 КУПИТЬ PREMIUM", url=ADMIN_URL))
    builder.row(types.InlineKeyboardButton(text="🔑 ВВЕСТИ КОД", callback_data="enter_code"))
    
    welcome = (
        "👑 **INFEX OSINT v9.8**\n"
        "───────────────────────\n"
        "✅ **БЕСПЛАТНО:** IP, Email или Фото.\n"
        "💎 **PREMIUM:** Спутниковый деанон по Нику.\n\n"
        "Слушаю вас, мой господин."
    )
    await message.answer(welcome, parse_mode="Markdown", reply_markup=builder.as_markup())

@dp.callback_query(F.data == "enter_code")
async def ask_code(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("⌨️ **Введите код активации:**")
    await state.set_state(AuthState.waiting_for_code)
    await callback.answer()

@dp.message(AuthState.waiting_for_code)
async def check_code(message: types.Message, state: FSMContext):
    # Очищаем ввод от пробелов и приводим к нижнему регистру для надежности
    user_code = message.text.strip().lower()
    
    if user_code == SECRET_CODE.lower():
        premium_users.add(message.from_user.id)
        await message.answer("✅ **PREMIUM АКТИВИРОВАН!**\nТеперь деанон по нику доступен навсегда.")
        await state.clear()
    else:
        await message.answer(f"❌ **НЕВЕРНЫЙ КОД.**\nВы ввели: `{user_code}`\nНужен правильный код. Купить: @softpack1977", parse_mode="Markdown")
        await state.clear() # Сбрасываем состояние, чтобы можно было попробовать снова

@dp.message(F.document)
async def free_photo_analysis(message: types.Message):
    await message.answer("🔎 *Анализ метаданных фото...*\nРезультат: Местоположение скрыто провайдером.", parse_mode="Markdown")

@dp.message()
async def main_handler(message: types.Message):
    if not message.text: return
    target = message.text.strip()
    user_id = message.from_user.id

    if is_ip(target) or is_email(target):
        await message.answer(f"🌍 **ОТКРЫТЫЙ ПОИСК:** `{target}`\nРезультат: База данных подтверждает наличие цели.", parse_mode="Markdown")
    
    elif user_id in premium_users:
        status = await message.answer("📡 **ПОДКЛЮЧЕНИЕ К СПУТНИКАМ...**")
        await asyncio.sleep(1)
        photo_path, lat, lon = generate_elite_dossier(target)
        kb = InlineKeyboardBuilder()
        kb.row(types.InlineKeyboardButton(text="🗺 КАРТА РФ", url=f"https://www.google.com/maps?q={lat},{lon}"))
        await message.answer_photo(types.FSInputFile(photo_path), caption=f"🎯 Объект `{target}` под наблюдением.", reply_markup=kb.as_markup())
        if os.path.exists(photo_path): os.remove(photo_path)
        await status.delete()

    else:
        builder = InlineKeyboardBuilder()
        builder.row(types.InlineKeyboardButton(text="💎 АКТИВИРОВАТЬ", callback_data="enter_code"))
        await message.answer("🔒 **ДОСТУП ОГРАНИЧЕН**\nПоиск по нику доступен только в Premium.", reply_markup=builder.as_markup())

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
