# 🎬 Smart AI Cinema Telegram Bot

Ushbu loyiha **Aiogram 3.x** va **SQLite (aiosqlite)** yordamida yaratilgan, sun'iy intellekt (OpenAI GPT-4o) integratsiyasiga ega aqlli Telegram bot hisoblanadi. Bot foydalanuvchilarga kino kodlari yoki nomlari orqali kinolarni qidirish imkonini beradi, hamda baza ichidan semantik qidiruvni amalga oshiradi.

## ✨ Imkoniyatlari va Funksiyalari

* **🔢 Kod orqali qidiruv:** Foydalanuvchi quruq raqamli kod yuborganda, bot bazadan o'sha zahoti tegishli kinoni topib beradi.
* **🧠 Intellektual Matnli Qidiruv:** Foydalanuvchi gap orasida kino nomini yozsa ham (*masalan: "menga merlin kinosini topib ber"*), bot ortiqcha so'zlarni tozalab, sarlavha bo'yicha bazadan qidiradi.
* **🤖 AI Tavsiya Tizimi (Strict Recommendation):** Agar qidirilgan kino bazada mavjud bo'lmasa, OpenAI GPT-4o modeli ishga tushadi va foydalanuvchiga internetdagi emas, **aynan bazada mavjud bo'lgan** boshqa kinolarni kodlari bilan tavsiya qiladi.
* **🆔 Unikal ID Generatsiyasi:** Har bir qo'shilgan kinoga `uuid` orqali takrorlanmas, maxsus ID (`MV-XXXXXX`) biriktiriladi.
* **🛡 Majburiy Obuna Tizimi:** Foydalanuvchi botdan foydalanishi uchun admin tomonidan sozlangan kanallarga a'zo bo'lishi shart.
* **📢 Avto-Reklama va Hukmronlik:** Har soatda bazadagi barcha foydalanuvchilarga faol reklamani navbat bilan, Telegram cheklovlarini buzmagan holda avtomatik tarqatadi.
* **🛠 Kuchli Admin Panel:** Adminlar uchun alohida tugmalar orqali kontent qo'shish, kanallarni boshqarish va jonli statistikani ko'rish imkoniyati.

---

## 🛠 Arxitektura va Funksiyalar Tavsifi

### 1. Tizim va Himoya (System & Security)
* `main()` — Botning yuragi. SQLite ma'lumotlar bazasini (`users`, `movies`, `channels`, `ads` jadvallari bilan) noldan shakllantiradi va botni `polling` rejimida ishga tushiradi.
* `check_sub(user_id)` — Foydalanuvchining majburiy obuna kanallaridagi a'zolik statusini tekshiruvchi funksiya. Adminlarga cheklov qo'ymaydi.

### 2. Sun'iy Intellekt Mantiqi (AI Logic)
* `ask_ai_recommendation(user_query, available_movies)` — Kino topilmagan vaziyatda bazadagi barcha real kontent ro'yxatini olib, GPT-4o yordamida foydalanuvchiga mos muqobil variantlarni taklif qiladi.
* `ask_ai_chat(text)` — Kino qidirmay, shunchaki bot bilan salom-alik qilgan foydalanuvchilarga AI nomidan javob beruvchi muloqot funksiyasi.

### 3. Qidiruv va Kontent Yetkazish (Search Handlers)
* `search_movie_by_code(message)` — Faqat raqamlardan iborat xabarlarni tutib olib, kod bo'yicha videoni reklama posti bilan birga yetkazadi.
* `smart_text_search_handler(message)` — Gap ichidan kalit so'zlarni Regular Expressions (ReGex) yordamida ajratib, SQL `LIKE` operatori orqali matnli qidiruvni amalga oshiradi.

### 4. Fon Vazifalari (Background Tasks)
* `auto_reklama_task()` — Bot orqasida (`asyncio.create_task`) tinimsiz aylanib turadigan va har 3600 soniyada foydalanuvchilarga kontentni uzatuvchi asinxron sikl.

---

## 🚀 O'rnatish va Ishga Tushirish

1.  **Repository-ni clone qiling:**
    ```bash
    git clone [https://github.com/SizningUsername/LoyhaNomi.git](https://github.com/SizningUsername/LoyhaNomi.git)
    cd LoyhaNomi
    ```

2.  **Kerakli kutubxonalarni o'rnating:**
    ```bash
    pip install aiogram aiosqlite openai
    ```

3.  **Koddagi sozlamalarni o'zgartiring:**
    `main.py` fayli ichidagi `TOKEN`, `ADMIN_ID` va `GITHUB_TOKEN` qiymatlarini o'zingizniki bilan almashtiring.

4.  **Botni ishga tushiring:**
    ```bash
    python main.py
    ```

## 🧰 Texnologiyalar
* **Language:** Python 3.11+
* **Framework:** Aiogram 3.x (Asynchronous Telegram Bot API)
* **Database:** SQLite via `aiosqlite`
* **LLM Provider:** GitHub Models API (OpenAI GPT-4o)
* **OS Environment:** Linux (Kali Linux / Termux tested)
