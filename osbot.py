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
from PIL.ExifTags import TAGS

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

# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---
def is_ip(text):
    return bool(re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", text))

def is_email(text):
    return bool(re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", text))

async def get_ip_intel(ip):
    async with httpx.AsyncClient() as client:
        try:
            r = await client.get(f"http://ip-api.com/json/{ip}?fields=status,country,city,isp,query")
            return r.json() if r.status_code == 200 else None
        except: return None

def generate_elite_dossier(target):
    img = Image.new('RGB', (600, 350), color=(5, 5, 5))
    draw = ImageDraw.Draw(img)
    chars = "ABEKMHOPCTYX"
    car_id = f"{random.choice(chars)}{random.randint(100,999)}{random.choice(chars)}{random.choice(chars)} {random.choice(['77','99','777','197'])}"
    lat, lon = f"{random.uniform(55.5, 55.9):.6f}", f"{random.uniform(37.3, 37.8):.6f}"
    gold = (255, 215, 0)
    text = (f"TARGET ID: {target}\n---------------------------\n"
            f"REGION: RUS [77]\nVEHICLE: {car_id}\n"
            f"GPS LOCK: {lat}, {lon}\nSTATUS: TRACKING...")
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
    welcome = "👑 **INFEX OSINT v9.9**\n\nПришлите IP, Email или Фото. Для глубокого деанона по нику активируйте Premium."
    await message.answer(welcome, parse_mode="Markdown", reply_markup=builder.as_markup())

@dp.callback_query(F.data == "enter_code")
async def ask_code(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("⌨️ **Введите код активации:**")
    await state.set_state(AuthState.waiting_for_code)
    await callback.answer()

@dp.message(AuthState.waiting_for_code)
async def check_code(message: types.Message, state: FSMContext):
    if message.text.strip().lower() == SECRET_CODE.lower():
        premium_users.add(message.from_user.id)
        await message.answer("✅ **PREMIUM АКТИВИРОВАН!**")
        await state.clear()
    else:
        await message.answer("❌ Неверный код. Купить: @softpack1977")
        await state.clear()

@dp.message(F.document)
async def handle_photo(message: types.Message):
    if not message.document.mime_type.startswith('image'): return
    status = await message.answer("🟡 *Дешифровка метаданных фото...*", parse_mode="Markdown")
    file = await bot.get_file(message.document.file_id)
    path = f"t_{message.from_user.id}.jpg"
    await bot.download_file(file.file_path, path)
    
    try:
        img = Image.open(path)
        exif = {TAGS.get(k): v for k, v in img._getexif().items() if k in TAGS} if img._getexif() else {}
        if exif:
            res = f"📸 **ДАННЫЕ ФОТО:**\nМодель: `{exif.get('Model', 'N/A')}`\nДата: `{exif.get('DateTime', 'N/A')}`"
            await status.edit_text(res, parse_mode="Markdown")
        else:
            await status.edit_text("❌ Метаданные не найдены.")
    except:
        await status.edit_text("❌ Ошибка при чтении файла.")
    if os.path.exists(path): os.remove(path)

@dp.message()
async def main_handler(message: types.Message):
    target = message.text.strip()
    user_id = message.from_user.id

    if is_ip(target):
        data = await get_ip_intel(target)
        if data and data.get('status') == 'success':
            msg = (f"🌍 **IP REPORT:** `{target}`\nСтрана: `{data.get('country')}`\n"
                   f"Город: `{data.get('city')}`\nПровайдер: `{data.get('isp')}`")
            await message.answer(msg, parse_mode="Markdown")
        else: await message.answer("❌ IP не найден.")
    
    elif is_email(target):
        await message.answer(f"📧 **EMAIL SEARCH:** `{target}`\nРезультат: Найден в 3 базах утечек. Активируйте Premium для подробностей.")

    elif user_id in premium_users:
        status = await message.answer("📡 **СПУТНИКОВЫЙ ЗАХВАТ...**")
        await asyncio.sleep(1)
        path, lat, lon = generate_elite_dossier(target)
        kb = InlineKeyboardBuilder().row(types.InlineKeyboardButton(text="🗺 КАРТА", url=f"https://www.google.com/maps?q={lat},{lon}"))
        await message.answer_photo(types.FSInputFile(path), caption=f"🎯 Объект `{target}` локализован.", reply_markup=kb.as_markup())
        os.remove(path)
        await status.delete()
    else:
        kb = InlineKeyboardBuilder().row(types.InlineKeyboardButton(text="💎 АКТИВИРОВАТЬ", callback_data="enter_code"))
        await message.answer("🔒 **ДОСТУП ОГРАНИЧЕН**\nПоиск по нику доступен в Premium.", reply_markup=kb.as_markup())

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
