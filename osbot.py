import logging
import asyncio
import httpx
import random
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from PIL import Image, ImageDraw
from PIL.ExifTags import TAGS, GPSTAGS

# --- КОНФИГУРАЦИЯ СИСТЕМЫ ---
API_TOKEN = '8686353635:AAHzwPvTVHvgaB3RdBMXgwYnw8FupK9bi30'
ADMIN_URL = "https://t.me/softpack1977" 
SECRET_CODE = "hackpack1977"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Список ID пользователей с премиумом (в памяти)
premium_users = set()

class AuthState(StatesGroup):
    waiting_for_code = State()

# --- ФУНКЦИИ ГЕНЕРАЦИИ И ПОИСКА ---

def generate_elite_dossier(target):
    img = Image.new('RGB', (600, 350), color=(5, 5, 5))
    draw = ImageDraw.Draw(img)
    regions = ["77", "99", "177", "777", "16", "78", "161"]
    car_id = f"{random.choice('ABEKMHOPCTYX')}{random.randint(100,999)}{random.choice('ABEKMHOPCTYX')}{random.choice('ABEKMHOPCTYX')} {random.choice(regions)}"
    lat, lon = f"{random.uniform(45.0, 60.0):.6f}", f"{random.uniform(30.0, 100.0):.6f}"
    gold = (255, 215, 0)
    text = (f"TARGET: {target}\n---------------------------\n"
            f"IDENTITY: VERIFIED\nTRANSPORT ID: {car_id}\n"
            f"LAST GPS: {lat}, {lon}\nSTATUS: LOCATED")
    draw.text((30, 30), text, fill=gold)
    draw.rectangle([5, 5, 595, 345], outline=gold, width=2)
    path = f"dossier_{target}.png"
    img.save(path)
    return path, lat, lon

async def get_ip_intel(ip):
    async with httpx.AsyncClient() as client:
        try:
            r = await client.get(f"http://ip-api.com/json/{ip}?fields=status,country,city,isp,query")
            return r.json() if r.status_code == 200 else None
        except: return None

def extract_exif(file_path):
    try:
        img = Image.open(file_path)
        exif = img._getexif()
        if not exif: return None
        data = {TAGS.get(tag, tag): value for tag, value in exif.items()}
        return data
    except: return None

# --- ОБРАБОТЧИКИ КОМАНД ---

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    welcome = (
        "👑 **INFEX OSINT: GOLD ELITE v9.5**\n"
        "───────────────────────\n"
        "Система готова к работе, мой господин.\n\n"
        "📡 **БЕСПЛАТНО:** Поиск по IP и анализ фото.\n"
        "💎 **PREMIUM:** Модуль Deep Hack (Досье + GPS + Авто).\n"
    )
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="💳 КУПИТЬ КОД", url=ADMIN_URL))
    builder.row(types.InlineKeyboardButton(text="🔑 ВВЕСТИ КОД АКТИВАЦИИ", callback_data="enter_code"))
    
    await message.answer(welcome, parse_mode="Markdown", reply_markup=builder.as_markup())

@dp.callback_query(F.data == "enter_code")
async def ask_code(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("⌨️ **Введите ваш секретный код доступа:**")
    await state.set_state(AuthState.waiting_for_code)
    await callback.answer()

@dp.message(AuthState.waiting_for_code)
async def check_code(message: types.Message, state: FSMContext):
    if message.text == SECRET_CODE:
        premium_users.add(message.from_user.id)
        await message.answer("✅ **ДОСТУП ELITE АКТИВИРОВАН!**\nТеперь любой ваш запрос проходит через спутник.")
        await state.clear()
    else:
        await message.answer("❌ **ОШИБКА АКТИВАЦИИ.** Проверьте код или обратитесь к @softpack1977")

# --- АНАЛИЗ ФОТО (ДОКУМЕНТЫ) ---
@dp.message(F.document)
async def handle_docs(message: types.Message):
    if not message.document.mime_type.startswith('image'): return
    status = await message.answer("🟡 *Дешифровка метаданных...*", parse_mode="Markdown")
    
    file = await bot.get_file(message.document.file_id)
    path = f"tmp_{message.from_user.id}.jpg"
    await bot.download_file(file.file_path, path)
    
    exif = extract_exif(path)
    if exif and "DateTime" in exif:
        await status.edit_text(f"📸 **ДАТА СЪЕМКИ:** `{exif.get('DateTime')}`\nУстройство: `{exif.get('Model')}`")
    else:
        await status.edit_text("❌ Метаданные не найдены.")
    
    if os.path.exists(path): os.remove(path)

# --- ГЛАВНЫЙ ОБРАБОТЧИК (IP И НИКИ) ---
@dp.message()
async def main_handler(message: types.Message):
    if not message.text: return
    target = message.text.strip()
    user_id = message.from_user.id

    if user_id in premium_users:
        # PREMIUM: ГЕНЕРАЦИЯ ДОСЬЕ
        status = await message.answer("🛸 **ПЕРЕХВАТ ДАННЫХ СПУТНИКОМ...**")
        await asyncio.sleep(1.2)
        photo_path, lat, lon = generate_elite_dossier(target)
        
        kb = InlineKeyboardBuilder()
        kb.row(types.InlineKeyboardButton(text="🗺 ОТКРЫТЬ GOOGLE MAPS", url=f"https://www.google.com/maps?q={lat},{lon}"))
        
        await message.answer_photo(
            photo=types.FSInputFile(photo_path),
            caption=f"✅ **ОБЪЕКТ {target} ЛОКАЛИЗОВАН**\nДоступ к данным подтвержден.",
            reply_markup=kb.as_markup()
        )
        if os.path.exists(photo_path): os.remove(photo_path)
        await status.delete()
    else:
        # FREE: REAL IP OSINT
        ip_data = await get_ip_intel(target)
        if ip_data and ip_data.get('status') == 'success':
            res = (f"🌍 **РЕЗУЛЬТАТ ПО IP:** `{target}`\n"
                   f"Страна: `{ip_data.get('country')}`\n"
                   f"Город: `{ip_data.get('city')}`\n"
                   f"Провайдер: `{ip_data.get('isp')}`\n\n"
                   f"💎 *Для поиска по нику введите Premium-код.*")
            await message.answer(res, parse_mode="Markdown")
        else:
            await message.answer("⚠️ Введите корректный IP или активируйте Premium для поиска по нику.")

async def main():
    print("--- INFEX OSINT SYSTEM v9.5 ONLINE ---")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
