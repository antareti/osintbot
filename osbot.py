import logging
import asyncio
import httpx
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import os

# --- КОНФИГУРАЦИЯ СИСТЕМЫ ---
API_TOKEN = '8686353635:AAHzwPvTVHvgaB3RdBMXgwYnw8FupK9bi30'

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# --- АНИМАЦИОННЫЙ ЛОГОТИП HACKPACK ---
async def send_gold_animation(message: types.Message):
    logo_frames = [
        "<code>  H A C K P A C K  </code>",
        "<code>👑 H A C K P A C K 👑</code>",
        "<code>✨ H A C K P A C K ✨</code>",
        "<code>🏆 H A C K P A C K 🏆</code>"
    ]
    
    # Эффект "золотого мерцания"
    msg = await message.answer(logo_frames[0], parse_mode="HTML")
    for frame in logo_frames[1:]:
        await asyncio.sleep(0.4)
        await msg.edit_text(frame, parse_mode="HTML")
    return msg

# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---

def extract_exif(file_path):
    try:
        img = Image.open(file_path)
        exif_raw = img._getexif()
        if not exif_raw: return None
        
        data = {}
        for tag, value in exif_raw.items():
            decoded = TAGS.get(tag, tag)
            if decoded == "GPSInfo":
                gps_decoded = {}
                for t in value:
                    sub_decoded = GPSTAGS.get(t, t)
                    gps_decoded[sub_decoded] = value[t]
                data[decoded] = gps_decoded
            else:
                data[decoded] = value
        return data
    except Exception as e:
        logging.error(f"Exif error: {e}")
        return None

def convert_to_degrees(value):
    d = float(value[0])
    m = float(value[1]) / 60.0
    s = float(value[2]) / 3600.0
    return d + m + s

async def get_ip_intel(ip):
    async with httpx.AsyncClient() as client:
        try:
            r = await client.get(f"http://ip-api.com/json/{ip}?fields=status,message,country,city,isp,org,as,query")
            return r.json() if r.status_code == 200 else None
        except:
            return None

# --- ОБРАБОТЧИКИ КОМАНД ---

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    # Запуск золотой анимации
    await send_gold_animation(message)
    
    welcome_text = (
        "👑 **INFEX OSINT GOLD ELITE v7.0**\n"
        "───────────────────────\n"
        "Система активна. Слушаю вас, мой господин.\n\n"
        "🛰 **ДОСТУПНЫЕ МОДУЛИ:**\n"
        "• Отправьте **IP/Email/Ник** для анализа.\n"
        "• Отправьте **Фото (как файл)** для GPRS-захвата.\n"
        "• Текстовый поиск в теневых базах.\n\n"
        "✨ *HACKPACK PREMIUM EDITION*"
    )
    await message.answer(welcome_text, parse_mode="Markdown")

@dp.message(F.document)
async def handle_binary_data(message: types.Message):
    if not message.document or not message.document.mime_type.startswith('image'):
        return

    status_msg = await message.answer("🟡 *Инициирую дешифровку метаданных...*", parse_mode="Markdown")
    
    file_id = message.document.file_id
    file = await bot.get_file(file_id)
    file_name = f"cache_{file_id}.jpg"
    await bot.download_file(file.file_path, file_name)

    exif = extract_exif(file_name)
    
    if not exif:
        await status_msg.edit_text("❌ **МЕТАДАННЫЕ ОЧИЩЕНЫ ИЛИ ОТСУТСТВУЮТ.**")
        if os.path.exists(file_name): os.remove(file_name)
        return

    report = [
        "📸 **BINARY FORENSIC REPORT**",
        "───────────────────────",
        f"▪️ Устройство: `{exif.get('Make', 'N/A')} {exif.get('Model', 'N/A')}`",
        f"▪️ Время: `{exif.get('DateTime', 'N/A')}`",
    ]

    if 'GPSInfo' in exif:
        try:
            gps = exif['GPSInfo']
            lat = convert_to_degrees(gps['GPSLatitude'])
            lon = convert_to_degrees(gps['GPSLongitude'])
            if gps.get('GPSLatitudeRef') == 'S': lat = -lat
            if gps.get('GPSLongitudeRef') == 'W': lon = -lon
            
            report.append("\n📍 **GPRS SIGNAL LOCKED**")
            report.append(f"Координаты: `{lat:.6f}, {lon:.6f}`")
            
            kb = InlineKeyboardBuilder()
            kb.row(types.InlineKeyboardButton(text="🗺 ОТКРЫТЬ GOOGLE MAPS", url=f"https://www.google.com/maps?q={lat},{lon}"))
            await status_msg.edit_text("\n".join(report), parse_mode="Markdown", reply_markup=kb.as_markup())
            if os.path.exists(file_name): os.remove(file_name)
            return
        except:
            report.append("\n⚠️ Ошибка парсинга GPRS.")

    await status_msg.edit_text("\n".join(report), parse_mode="Markdown")
    if os.path.exists(file_name): os.remove(file_name)

@dp.message()
async def analyze_target(message: types.Message):
    if not message.text:
        return

    target = message.text.strip()
    status_msg = await message.answer(f"🔎 *Поиск в базе HACKPACK:* `{target}`...", parse_mode="Markdown")
    
    await asyncio.sleep(0.6)
    ip_data = await get_ip_intel(target)
    
    report = [
        f"🏆 **REPORT: {target}**",
        "───────────────────────"
    ]

    if ip_data and ip_data.get('status') == 'success':
        report.extend([
            f"🌍 Страна: `{ip_data.get('country')}`",
            f"🏙 Город: `{ip_data.get('city')}`",
            f"🏢 Провайдер: `{ip_data.get('isp')}`",
            ""
        ])

    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="📧 Epieos", url=f"https://epieos.com/?q={target}"))
    builder.row(types.InlineKeyboardButton(text="👤 WhatsMyName", url=f"https://whatsmyname.app/?q={target}"))
    builder.row(types.InlineKeyboardButton(text="🔍 Google Leaks", url=f"https://www.google.com/search?q=%22{target}%22+leak"))

    await status_msg.edit_text("\n".join(report), parse_mode="Markdown", reply_markup=builder.as_markup())

async def main():
    print("--- HACKPACK GOLD SYSTEM ONLINE ---")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("--- SYSTEM OFFLINE ---")