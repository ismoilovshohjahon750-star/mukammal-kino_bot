import logging
import asyncio
import aiosqlite
import os
import uuid
import re
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.client.default import DefaultBotProperties
from openai import OpenAI

# ⚙️ KONFIGURATSIYA
TOKEN = 'Botni tokini'
ADMIN_ID = telegramdan olinadigan ID
GITHUB_TOKEN = "githubdan oligan AI API"

client = OpenAI(
    base_url="https://models.github.ai/inference/v1",
    api_key=GITHUB_TOKEN
)
MODEL_NAME = "openai/gpt-4o"

DB_NAME = "milliarder.db"
REKLAMA_INTERVALI = 3600

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
dp = Dispatcher()

class AdminStates(StatesGroup):
    kino_kodi = State()
    kino_nomi = State()
    kino_yili = State()
    kino_vidosi = State()
    reklama_yuborish = State()
    kanal_qoshish = State()

async def check_sub(user_id):
    if user_id == ADMIN_ID: return True
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT id FROM channels") as cur: channels = await cur.fetchall()
    if not channels: return True
    for (ch_id,) in channels:
        try:
            member = await bot.get_chat_member(chat_id=ch_id, user_id=user_id)
            if member.status not in ['member', 'administrator', 'creator']: return False
        except: continue
    return True

# 🧠 BAZADAGI KINOLARNI CHUQQUR TAHLIL QILIB TAVSIYA BERISH (Strictly from DB)
async def ask_ai_recommendation(user_query: str, available_movies: list):
    if not available_movies:
        return "😔 Afsuski, siz qidirgan kino topilmadi va hozircha bazamiz bo'sh. Tez orada yangi kinolar qo'shiladi!"
        
    # Bazadagi bor kinolarni matn ko'rinishiga keltiramiz
    movies_str = "\n".join([f"- Nomi: {m[0]} | Chiqqan yili: {m[1]} | Kodi: {m[2]}" for m in available_movies])
    
    prompt = f"""
    Foydalanuvchi botdan ushbu kinoni so'radi: "{user_query}".
    Afsuski, bizning bazamizda aynan ushbu nomdagi kino topilmadi.
    
    Bizning bazamizda MAVJUD BO'LGAN kinolar ro'yxati (Faqat shu ro'yxatdan foydalan, boshqa kino o'ylab topma!):
    {movies_str}
    
    Vazifang: Foydalanuvchiga u qidirgan kino yo'qligini muloyim tushuntir. Keyin, yuqoridagi ro'yxat ichidan unga mos kelishi mumkin bo'lgan 2-3 ta kinoni chiroyli qilib tavsiya et va ularni botdan qanday kod orqali olishi mumkinligini (Kodi: deb) ko'rsat. Javobingni faqat o'zbek tilida yoz.
    """
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=600
        )
        return response.choices[0].message.content
    except Exception as e:
        # AI ulanmay qolsa, quruq xato bermasdan bazadagi kinolarni shundoq ko'rsatamiz
        text = "😔 Afsuski, siz qidirgan kino topilmadi.\n\n🎬 **Bazamizdagi bor kinolar ro'yxati:**\n"
        for m in available_movies[:5]:
            text += f"🔹 {m[0]} ({m[1]}) — Kodi: <code>{m[2]}</code>\n"
        return text

# 🧠 ODDIY SALOM-ALIK UCHUN AI CHAT
async def ask_ai_chat(text: str):
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "Sen foydali kino yordamchisisan. Foydalanuvchiga salom ber va kino qidirish uchun kino nomi yoki kodini yuborishi mumkinligini eslat. Qisqa yoz."},
                {"role": "user", "content": text}
            ],
            temperature=0.7,
            max_tokens=300
        )
        return response.choices[0].message.content
    except:
        return "👋 Salom! Kino kodini yoki nomini yuboring, men bazadan qidirib beraman."

def admin_panel_kb():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🎬 Kino qo'shish"), KeyboardButton(text="📊 Statistika")],
        [KeyboardButton(text="📢 Kanallarni boshqarish")],
        [KeyboardButton(text="✉️ Reklama tarqatish"), KeyboardButton(text="🏠 Bosh menyu")]
    ], resize_keyboard=True)

@dp.message(Command("start"))
async def start_handler(message: Message, state: FSMContext = None):
    if state: await state.clear()
    user_id = message.from_user.id
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("INSERT OR IGNORE INTO users (id) VALUES (?)", (user_id,))
        await db.commit()

    if not await check_sub(user_id):
        async with aiosqlite.connect(DB_NAME) as db:
            async with db.execute("SELECT id FROM channels") as cur: channels = await cur.fetchall()
        inline_kb = [[InlineKeyboardButton(text=f"Obuna bo'lish: {ch_id}", url=f"https://t.me/{ch_id.replace('@', '')}")] for (ch_id,) in channels]
        inline_kb.append([InlineKeyboardButton(text="✅ Tekshirish", callback_data="check_sub")])
        return await message.answer("<b>Botdan foydalanish uchun kanallarimizga obuna bo'ling!</b>", reply_markup=InlineKeyboardMarkup(inline_keyboard=inline_kb))
    await message.answer("👋 Salom! Kino kodini kiriting yoki kino nomini yozib qidiring (Masalan: Merlin 1-qismi).")

@dp.callback_query(F.data == "check_sub")
async def check_cb(call: CallbackQuery):
    if await check_sub(call.from_user.id):
        try: await call.message.delete()
        except: pass
        await call.message.answer("✅ Rahmat! Obuna tasdiqlandi. Kino qidirishingiz mumkin.")
    else: await call.answer("❌ Hali hamma kanallarga obuna bo'lmagansiz!", show_alert=True)

@dp.message(Command("admin"))
async def admin_cmd(message: Message):
    if message.from_user.id == ADMIN_ID: await message.answer("🛠 <b>Admin panelga xush kelibsiz!</b>", reply_markup=admin_panel_kb())

@dp.message(F.text == "🏠 Bosh menyu")
async def home(message: Message): await message.answer("Siz bosh menyudasiz.", reply_markup=ReplyKeyboardRemove())

@dp.message(F.text == "📊 Statistika", F.from_user.id == ADMIN_ID)
async def stats(message: Message):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT COUNT(*) FROM users") as u: u_cnt = (await u.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM movies") as m: m_cnt = (await m.fetchone())[0]
    await message.answer(f"📈 <b>Statistika:</b>\n\n👤 Foydalanuvchilar: {u_cnt}\n🎬 Jami kinolar: {m_cnt}")

# 🎬 KINO QO'SHISH BOSQICHLARI
@dp.message(F.text == "🎬 Kino qo'shish", F.from_user.id == ADMIN_ID)
async def start_add_movie(message: Message, state: FSMContext):
    await state.set_state(AdminStates.kino_kodi)
    await message.answer("Kino uchun raqamli kod kiriting (masalan: 1):")

@dp.message(AdminStates.kino_kodi)
async def process_movie_code(message: Message, state: FSMContext):
    await state.update_data(code=str(message.text).strip())
    await state.set_state(AdminStates.kino_nomi)
    await message.answer("Kino nomini to'liq kiriting (masalan: Merlin 1-qism):")

@dp.message(AdminStates.kino_nomi)
async def process_movie_title(message: Message, state: FSMContext):
    await state.update_data(title=str(message.text).strip())
    await state.set_state(AdminStates.kino_yili)
    await message.answer("Kino chiqqan yilini kiriting (masalan: 2008):")

@dp.message(AdminStates.kino_yili)
async def process_movie_year(message: Message, state: FSMContext):
    await state.update_data(year=str(message.text).strip())
    await state.set_state(AdminStates.kino_vidosi)
    await message.answer("Endi kinoning video faylini yuboring:")

@dp.message(AdminStates.kino_vidosi, F.video)
async def process_movie_video(message: Message, state: FSMContext):
    data = await state.get_data()
    unique_id = f"MV-{uuid.uuid4().hex[:8].upper()}"
    
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "INSERT OR REPLACE INTO movies (id, title, year, code, file_id) VALUES (?, ?, ?, ?, ?)", 
            (unique_id, data['title'], data['year'], data['code'], message.video.file_id)
        )
        await db.commit()
    await state.clear()
    await message.answer(
        f"✅ <b>Kino muvaffaqiyatli saqlandi!</b>\n\n🆔 ID: <code>{unique_id}</code>\n🎬 Nomi: {data['title']}\n📅 Yili: {data['year']}\n🔢 Kodi: {data['code']}", 
        reply_markup=admin_panel_kb()
    )

# 📢 KANALLAR VA REKLAMA
@dp.message(F.text == "📢 Kanallarni boshqarish", F.from_user.id == ADMIN_ID)
async def manage_channels(message: Message):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT id FROM channels") as cur: channels = await cur.fetchall()
    kb = [[InlineKeyboardButton(text=f"❌ O'chirish {ch_id}", callback_data=f"del_ch:{ch_id}")] for (ch_id,) in channels]
    kb.append([InlineKeyboardButton(text="➕ Kanal qo'shish", callback_data="add_ch")])
    await message.answer("<b>Majburiy obuna kanallari:</b>", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))

@dp.callback_query(F.data == "add_ch")
async def add_ch_call(call: CallbackQuery, state: FSMContext):
    await state.set_state(AdminStates.kanal_qoshish)
    await call.message.answer("Kanalning @username sini yuboring:")
    await call.answer()

@dp.message(AdminStates.kanal_qoshish)
async def save_channel(message: Message, state: FSMContext):
    if message.text.startswith("@"):
        async with aiosqlite.connect(DB_NAME) as db:
            await db.execute("INSERT OR IGNORE INTO channels (id) VALUES (?)", (message.text,))
            await db.commit()
        await state.clear()
        await message.answer(f"✅ {message.text} qo'shildi!", reply_markup=admin_panel_kb())
    else: await message.answer("❌ Xato! @ bilan boshlanishi kerak.")

@dp.callback_query(F.data.startswith("del_ch:"))
async def delete_channel(call: CallbackQuery):
    ch_id = call.data.split(":")[1]
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("DELETE FROM channels WHERE id = ?", (ch_id,))
        await db.commit()
    await call.answer("Kanal o'chirildi", show_alert=True)
    await manage_channels(call.message)

@dp.message(F.text == "✉️ Reklama tarqatish", F.from_user.id == ADMIN_ID)
async def start_ads(message: Message, state: FSMContext):
    await state.set_state(AdminStates.reklama_yuborish)
    await message.answer("📢 <b>Reklama postini yuboring.</b>")

@dp.message(AdminStates.reklama_yuborish)
async def save_ads(message: Message, state: FSMContext):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("DELETE FROM ads")
        await db.execute("INSERT INTO ads (from_chat_id, message_id) VALUES (?, ?)", (message.chat.id, message.message_id))
        await db.commit()
    await state.clear()
    await message.answer("✅ Reklama saqlandi!", reply_markup=admin_panel_kb())

# 🎬 1. FAQAT TO'G'RIDAN-TO'G'RI RAQAMLI KOD BILAN QIDIRISH
@dp.message(F.text.regexp(r'^\d+$'))
async def search_movie_by_code(message: Message, state: FSMContext):
    if not await check_sub(message.from_user.id): return await start_handler(message, state)
    search_code = str(message.text).strip()
    
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT file_id, title, year, id FROM movies WHERE code = ?", (search_code,)) as cur: 
            movie = await cur.fetchone()
            
    if movie:
        file_id, title, year, unique_id = movie
        async with aiosqlite.connect(DB_NAME) as db:
            async with db.execute("SELECT from_chat_id, message_id FROM ads LIMIT 1") as ad_cur: ad = await ad_cur.fetchone()
        if ad:
            try: await bot.copy_message(chat_id=message.chat.id, from_chat_id=ad[0], message_id=ad[1])
            except: pass
            
        caption_text = f"🎬 <b>{title}</b>\n\n📅 <b>Yili:</b> {year}\n🔢 <b>Kino kodi:</b> {search_code}\n🆔 <b>ID:</b> <code>{unique_id}</code>"
        await message.answer_video(file_id, caption=caption_text)
    else:
        # Agar kod xato bo'lsa, bazadagi barcha kinolarni AIga berib tavsiya qildiramiz
        async with aiosqlite.connect(DB_NAME) as db:
            async with db.execute("SELECT title, year, code FROM movies") as c: available_movies = await c.fetchall()
        rec_msg = await ask_ai_recommendation(f"Kod: {search_code}", available_movies)
        await message.answer(rec_msg)

# 🧠 2. INTELLEKTUAL GAP ICHIDAN MATNLI QIDIRISH VA BAZADAGI KINOLARNI TAVSIYA QILISH
@dp.message(F.text)
async def smart_text_search_handler(message: Message, state: FSMContext):
    if message.text.startswith("/"): return
    if await state.get_state(): return 

    if not await check_sub(message.from_user.id): return await start_handler(message, state)

    user_query = message.text.strip()
    
    # Oddiy so'rashishlarni ajratish
    if user_query.lower() in ['salom', 'hello', 'qale', 'qalaysiz', 'assalomu alaykum']:
        ai_chat_resp = await ask_ai_chat(user_query)
        return await message.answer(ai_chat_resp)

    wait_msg = await message.answer("🔍 Kinoteatr bazasidan qidirilmoqda...")

    # Stop-so'zlarni olib tashlab, asosiy kalit so'zni topish
    words = [w for w in re.split(r'\s+', user_query) if len(w) > 2 and w.lower() not in ['menga', 'topib', 'ber', 'skachat', 'kino', 'film', 'bormi', 'bosa']]
    
    found_movies = []
    async with aiosqlite.connect(DB_NAME) as db:
        if words:
            for word in words:
                async with db.execute(
                    "SELECT file_id, title, year, code, id FROM movies WHERE title LIKE ? OR code = ? OR year = ?", 
                    (f"%{word}%", word, word)
                ) as cur:
                    rows = await cur.fetchall()
                    for r in rows:
                        if r not in found_movies: found_movies.append(r)
        else:
            async with db.execute("SELECT file_id, title, year, code, id FROM movies WHERE title LIKE ?", (f"%{user_query}%",)) as cur:
                found_movies = await cur.fetchall()

    # ✅ KINO BAZADA TOPILSA FOYDALANUVCHIGA YUBORISH
    if found_movies:
        try: await bot.delete_message(chat_id=message.chat.id, message_id=wait_msg.message_id)
        except: pass
        
        async with aiosqlite.connect(DB_NAME) as db:
            async with db.execute("SELECT from_chat_id, message_id FROM ads LIMIT 1") as ad_cur: ad = await ad_cur.fetchone()
        if ad:
            try: await bot.copy_message(chat_id=message.chat.id, from_chat_id=ad[0], message_id=ad[1])
            except: pass

        for movie in found_movies[:3]:
            file_id, title, year, code, unique_id = movie
            caption_text = f"🎬 <b>{title}</b>\n\n📅 <b>Yili:</b> {year}\n🔢 <b>Kino kodi:</b> {code}\n🆔 <b>ID:</b> <code>{unique_id}</code>"
            await message.answer_video(file_id, caption=caption_text)
        return

    # ❌ KINO TOPILMASA: BAZADAGI BARCHA KINOLAR RO'YXATINI AIGA TAVSIYA UCHUN YUBORISH
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT title, year, code FROM movies") as c: available_movies = await c.fetchall()
    
    recommendation_text = await ask_ai_recommendation(user_query, available_movies)
    
    try: await bot.delete_message(chat_id=message.chat.id, message_id=wait_msg.message_id)
    except: pass
    await message.answer(recommendation_text)

# 🕒 AVTO REKLAMA VAZIFASI
async def auto_reklama_task():
    while True:
        await asyncio.sleep(REKLAMA_INTERVALI)
        async with aiosqlite.connect(DB_NAME) as db:
            async with db.execute("SELECT from_chat_id, message_id FROM ads LIMIT 1") as cur: ad = await cur.fetchone()
            if ad:
                async with db.execute("SELECT id FROM users") as u_cur: users = await u_cur.fetchall()
                for (uid,) in users:
                    try:
                        if uid == ADMIN_ID: continue
                        await bot.copy_message(chat_id=uid, from_chat_id=ad[0], message_id=ad[1])
                        await asyncio.sleep(0.05)
                    except: continue

async def main():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY)")
        await db.execute("CREATE TABLE IF NOT EXISTS channels (id TEXT PRIMARY KEY)")
        await db.execute("CREATE TABLE IF NOT EXISTS ads (from_chat_id INTEGER, message_id INTEGER)")
        await db.execute("""
            CREATE TABLE IF NOT EXISTS movies (
                id TEXT PRIMARY KEY,
                title TEXT,
                year TEXT,
                code TEXT,
                file_id TEXT
            )
        """)
        await db.commit()
        
    await bot.delete_webhook(drop_pending_updates=True)
    asyncio.create_task(auto_reklama_task())
    print("Bot yangi real-tavsiya algoritmi bilan ishga tushdi!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
