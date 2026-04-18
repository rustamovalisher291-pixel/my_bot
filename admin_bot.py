import asyncio
<<<<<<< HEAD
import json
from pathlib import Path
from typing import Optional

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

API_TOKEN = "..."  # BotFather token
ADMIN_USERNAME = "Obito_2343"  # @ belgisisiz, faqat username

DATA_PATH = Path("movies.json")
=======
from typing import Optional, cast
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command

import os
API_TOKEN = os.getenv("BOT_TOKEN", "")
>>>>>>> ec58fc070b0dc7319df16daa41221ef198c9dab8

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

<<<<<<< HEAD
admin_state: dict[int, dict] = {}


def load_movies() -> list[dict]:
    if not DATA_PATH.exists():
        return []
    try:
        data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return data
    except Exception:
        pass
    return []


def save_movies(movies: list[dict]) -> None:
    DATA_PATH.write_text(json.dumps(movies, indent=2, ensure_ascii=True), encoding="utf-8")


def normalize_name(name: str) -> str:
    return " ".join(name.strip().lower().split())


def normalize_genre(genre: str) -> str:
    return " ".join(genre.strip().lower().split())


def is_admin(message: Message) -> bool:
    return bool(message.from_user and message.from_user.username == ADMIN_USERNAME)


def make_start_kb() -> ReplyKeyboardMarkup:
    try:
        button = KeyboardButton(text="Boshlash", style="primary")
    except TypeError:
        button = KeyboardButton(text="Boshlash")
    return ReplyKeyboardMarkup(
        keyboard=[[button]],
        resize_keyboard=True,
    )


def make_admin_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Kino qo‘shish")],
            [KeyboardButton(text="🗑 Kino o‘chirish")],
            [KeyboardButton(text="📋 Kinolar ro‘yxati")],
        ],
        resize_keyboard=True,
    )


def make_back_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🔙 Orqaga")]],
        resize_keyboard=True,
    )


def make_movies_kb(movies: list[dict]) -> ReplyKeyboardMarkup:
    buttons = [[KeyboardButton(text=m["name"])] for m in movies]
    buttons.append([KeyboardButton(text="🔙 Orqaga")])
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


def format_movie(movie: dict) -> str:
    genre = movie.get("genre", "Noma'lum")
    return f"{movie['name']} ({genre})"


def find_similar_movies(selected_movie: dict, movies: list[dict]) -> list[dict]:
    selected_genre = normalize_genre(selected_movie.get("genre", ""))
    if not selected_genre:
        return []
    selected_name = normalize_name(selected_movie["name"])
    return [
        movie
        for movie in movies
        if normalize_name(movie["name"]) != selected_name
        and normalize_genre(movie.get("genre", "")) == selected_genre
    ]


@dp.message(Command("start"))
async def cmd_start(message: Message) -> None:
    await message.answer(
        "Kino botga xush kelibsiz. Boshlash tugmasini bosing 👇",
        reply_markup=make_start_kb(),
    )


@dp.message(Command("admin"))
async def cmd_admin(message: Message) -> None:
    if not is_admin(message):
        await message.answer("Siz admin emassiz ❌")
        return
    await message.answer("Admin panel 👑", reply_markup=make_admin_kb())


@dp.message(F.text == "Boshlash")
async def start_movies(message: Message) -> None:
    movies = load_movies()
    if not movies:
        await message.answer("Hozircha kino yo‘q ❌", reply_markup=make_start_kb())
        return
    await message.answer("Kino tanlang 👇", reply_markup=make_movies_kb(movies))


@dp.message(F.text == "🔙 Orqaga")
async def go_back(message: Message) -> None:
    if is_admin(message) and message.from_user and message.from_user.id in admin_state:
        admin_state.pop(message.from_user.id, None)
        await message.answer("Admin panel 👇", reply_markup=make_admin_kb())
        return
    await message.answer("Bosh sahifa 👇", reply_markup=make_start_kb())


@dp.message(F.text == "📋 Kinolar ro‘yxati")
async def list_movies(message: Message) -> None:
    if not is_admin(message):
        return
    movies = load_movies()
    if not movies:
        await message.answer("Hozircha kino yo‘q ❌")
        return
    text = "\n".join([f"{i + 1}. {format_movie(m)}" for i, m in enumerate(movies)])
    await message.answer(text)


@dp.message(F.text == "➕ Kino qo‘shish")
async def add_movie(message: Message) -> None:
    if not is_admin(message) or not message.from_user:
        return
    admin_state[message.from_user.id] = {"mode": "ADD_NAME"}
    await message.answer("Kino nomini yuboring:", reply_markup=make_back_kb())


@dp.message(F.text == "🗑 Kino o‘chirish")
async def delete_movie(message: Message) -> None:
    if not is_admin(message) or not message.from_user:
        return
    movies = load_movies()
    if not movies:
        await message.answer("Hozircha kino yo‘q ❌")
        return
    admin_state[message.from_user.id] = {"mode": "DELETE_PICK"}
    text = "\n".join([f"{i + 1}. {m['name']}" for i, m in enumerate(movies)])
    await message.answer("O‘chirish uchun raqam yoki nom yuboring:\n" + text, reply_markup=make_back_kb())


@dp.message()
async def handle_messages(message: Message) -> None:
    user = message.from_user
    if user is None:
        return

    # Admin oqimi
    astate = admin_state.get(user.id)
    if astate and is_admin(message):
        mode = astate.get("mode")
        text = message.text

        if mode == "ADD_NAME":
            if not text:
                await message.answer("Iltimos, kino nomini matn ko‘rinishida yuboring.")
                return
            movies = load_movies()
            name_key = normalize_name(text)
            if any(normalize_name(m["name"]) == name_key for m in movies):
                await message.answer("Bu nom allaqachon bor ❌")
                return
            astate["name"] = text.strip()
            astate["mode"] = "ADD_GENRE"
            await message.answer("Endi kino janrini yuboring. Masalan: Komediya, Jangari, Drama")
            return

        if mode == "ADD_GENRE":
            if not text:
                await message.answer("Iltimos, janrni matn ko‘rinishida yuboring.")
                return
            astate["genre"] = text.strip()
            astate["mode"] = "ADD_FILE"
            await message.answer("Endi kino faylini yuboring (video yoki document):")
            return

        if mode == "ADD_FILE":
            movies = load_movies()
            file_id: Optional[str] = None
            file_type: Optional[str] = None

            if message.video:
                file_id = message.video.file_id
                file_type = "video"
            elif message.document:
                file_id = message.document.file_id
                file_type = "document"

            if not file_id or not file_type:
                await message.answer("Faqat video yoki document yuboring.")
                return

            movies.append({
                "name": astate["name"],
                "genre": astate.get("genre", "Noma'lum"),
                "file_id": file_id,
                "file_type": file_type,
            })
            save_movies(movies)
            admin_state.pop(user.id, None)
            await message.answer("Kino qo‘shildi ✅", reply_markup=make_admin_kb())
            return

        if mode == "DELETE_PICK":
            if not text:
                await message.answer("Raqam yoki nom yuboring.")
                return
            movies = load_movies()
            idx = None
            if text.isdigit():
                idx = int(text) - 1
                if idx < 0 or idx >= len(movies):
                    idx = None
            else:
                name_key = normalize_name(text)
                for i, m in enumerate(movies):
                    if normalize_name(m["name"]) == name_key:
                        idx = i
                        break

            if idx is None:
                await message.answer("Topilmadi. Qayta yuboring.")
                return

            removed = movies.pop(idx)
            save_movies(movies)
            admin_state.pop(user.id, None)
            await message.answer(f"O‘chirildi ✅: {removed['name']}", reply_markup=make_admin_kb())
            return

    # Oddiy foydalanuvchi: kino tanlash
    text = message.text
    if not text:
        return
    movies = load_movies()
    name_key = normalize_name(text)
    for m in movies:
        if normalize_name(m["name"]) == name_key:
            if m["file_type"] == "video":
                await message.answer_video(m["file_id"])
            else:
                await message.answer_document(m["file_id"])
            genre = m.get("genre", "Noma'lum")
            similar_movies = find_similar_movies(m, movies)
            if similar_movies:
                similar_text = "\n".join(
                    [f"{i + 1}. {format_movie(movie)}" for i, movie in enumerate(similar_movies)]
                )
                await message.answer(
                    f"Janri: {genre}\n\nShu janrdagi o‘xshash kinolar:\n{similar_text}"
                )
            else:
                await message.answer(f"Janri: {genre}\nShu janrda boshqa kino topilmadi.")
            return


async def main() -> None:
    print("Bot ishga tushdi ✅")
    await dp.start_polling(bot)


=======
# 🔹 Admin username (faqat @sizningusername emas)
ADMIN_USERNAME = "Obito_2343"  # @ belgisi yo'q, faqat text

# 🔹 Savollar va foydalanuvchi holati
questions = []
test_state = {}
admin_state = {}

# 🔹 Tugmalar yaratuvchi funksiya
def make_answers_kb(answers):
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=a)] for a in answers],
        resize_keyboard=True
    )

def get_user(message: types.Message) -> Optional[types.User]:
    if message.from_user is None:
        return None
    return cast(types.User, message.from_user)

start_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Boshlash")]],
    resize_keyboard=True
)

admin_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="➕ Savol qo‘shish")],
        [KeyboardButton(text="🧩 Savol-javob tuzish")],
        [KeyboardButton(text="✏️ Tahrirlash")],
        [KeyboardButton(text="🗑 O‘chirish")],
        [KeyboardButton(text="📋 Savollarni ko‘rish")]
    ],
    resize_keyboard=True
)

back_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="🔙 Orqaga")]],
    resize_keyboard=True
)

# /start
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Testni boshlash uchun Boshlash tugmasini bosing 👇", reply_markup=start_kb)

# /admin
@dp.message(Command("admin"))
async def admin_panel(message: types.Message):
    from_user = get_user(message)
    if from_user is None:
        return
    username = from_user.username
    if username == ADMIN_USERNAME:
        await message.answer("Admin panelga xush kelibsiz 👑", reply_markup=admin_kb)
    else:
        await message.answer("Siz admin emassiz ❌")

# ➕ Savol qo‘shish tugmasi
@dp.message(F.text == "➕ Savol qo‘shish")
async def add_question(message: types.Message):
    from_user = get_user(message)
    if from_user is None:
        return
    username = from_user.username
    if username != ADMIN_USERNAME:
        return
    admin_state[from_user.id] = {"mode": "ADD"}
    await message.answer("Format:\nSavol | A | B | C | D | To‘g‘ri javob", reply_markup=back_kb)

# 🧩 Savol-javob tuzish (bosqichma-bosqich)
@dp.message(F.text == "🧩 Savol-javob tuzish")
async def build_qa(message: types.Message):
    from_user = get_user(message)
    if from_user is None:
        return
    username = from_user.username
    if username != ADMIN_USERNAME:
        return
    admin_state[from_user.id] = {"mode": "BUILD_Q", "tmp": {}}
    await message.answer("Savol matnini yuboring:", reply_markup=back_kb)

# 📋 Savollarni ko‘rish tugmasi
@dp.message(F.text == "📋 Savollarni ko‘rish")
async def show_questions(message: types.Message):
    from_user = get_user(message)
    if from_user is None:
        return
    username = from_user.username
    if username != ADMIN_USERNAME:
        return
    if not questions:
        await message.answer("Savollar yo‘q ❌")
        return
    text = "\n".join([f"{i+1}. {q['question']} ({q['correct']})" for i, q in enumerate(questions)])
    await message.answer(text)

# ✏️ Tahrirlash
@dp.message(F.text == "✏️ Tahrirlash")
async def edit_question(message: types.Message):
    from_user = get_user(message)
    if from_user is None:
        return
    username = from_user.username
    if username != ADMIN_USERNAME:
        return
    if not questions:
        await message.answer("Savollar yo‘q ❌")
        return
    admin_state[from_user.id] = {"mode": "EDIT_PICK"}
    text = "\n".join([f"{i+1}. {q['question']}" for i, q in enumerate(questions)])
    await message.answer("Tahrirlash uchun raqam yuboring:\n" + text, reply_markup=back_kb)

# 🗑 O‘chirish
@dp.message(F.text == "🗑 O‘chirish")
async def delete_question(message: types.Message):
    from_user = get_user(message)
    if from_user is None:
        return
    username = from_user.username
    if username != ADMIN_USERNAME:
        return
    if not questions:
        await message.answer("Savollar yo‘q ❌")
        return
    admin_state[from_user.id] = {"mode": "DELETE_PICK"}
    text = "\n".join([f"{i+1}. {q['question']}" for i, q in enumerate(questions)])
    await message.answer("O‘chirish uchun raqam yuboring:\n" + text, reply_markup=back_kb)

# Savol qo‘shish logikasi
@dp.message(F.text.contains("|"))
async def save_question(message: types.Message):
    from_user = get_user(message)
    if from_user is None:
        return
    username = from_user.username
    if username != ADMIN_USERNAME:
        return
    text = message.text
    if text is None:
        return
    state = admin_state.get(from_user.id)
    if not state:
        return
    if state.get("mode") != "ADD":
        return
    try:
        parts = [p.strip() for p in text.split("|")]
        if len(parts) < 3:
            await message.answer("❌ Format xato!")
            return
        q = parts[0]
        answers = parts[1:-1]
        correct = parts[-1]
        questions.append({"question": q, "answers": answers, "correct": correct})
        await message.answer("✅ Savol qo‘shildi!", reply_markup=admin_kb)
        admin_state.pop(from_user.id, None)
    except Exception as e:
        await message.answer(f"Xato: {e}")

# Boshlash tugmasi
@dp.message(F.text == "Boshlash")
async def start_test(message: types.Message):
    from_user = get_user(message)
    if from_user is None:
        return
    user_id = from_user.id
    if not questions:
        await message.answer("Savollar yo‘q ❌")
        return
    test_state[user_id] = {"i": 0, "score": 0}
    q = questions[0]
    await message.answer(q["question"], reply_markup=make_answers_kb(q["answers"]))

# Javob tekshirish
@dp.message()
async def check_answer(message: types.Message):
    from_user = get_user(message)
    if from_user is None:
        return
    text = message.text
    if text is None:
        return
    user_id = from_user.id
    # Admin orqaga qaytish
    if text == "🔙 Orqaga":
        if from_user.username == ADMIN_USERNAME and admin_state.get(user_id):
            admin_state.pop(user_id, None)
            await message.answer("Admin menyu 👇", reply_markup=admin_kb)
        return

    # Admin oqimi
    astate = admin_state.get(user_id)
    if astate:
        mode = astate.get("mode")
        if mode == "BUILD_Q":
            astate["tmp"]["question"] = text
            astate["mode"] = "BUILD_A"
            await message.answer("Variantlarni yuboring (masalan: A,B,C,D):")
            return
        if mode == "BUILD_A":
            answers = [p.strip() for p in text.split(",") if p.strip()]
            if len(answers) < 2:
                await message.answer("Kamida 2 ta variant yuboring.")
                return
            astate["tmp"]["answers"] = answers
            astate["mode"] = "BUILD_C"
            await message.answer("To‘g‘ri javobni yuboring (variantlardan biri bo‘lsin):")
            return
        if mode == "BUILD_C":
            correct = text.strip()
            answers = astate["tmp"].get("answers", [])
            if correct not in answers:
                await message.answer("To‘g‘ri javob variantlardan biri bo‘lishi kerak.")
                return
            questions.append(
                {"question": astate["tmp"]["question"], "answers": answers, "correct": correct}
            )
            admin_state.pop(user_id, None)
            await message.answer("✅ Savol-javob qo‘shildi!", reply_markup=admin_kb)
            return
        if mode == "EDIT_PICK":
            if not text.isdigit():
                await message.answer("Raqam yuboring.")
                return
            idx = int(text) - 1
            if idx < 0 or idx >= len(questions):
                await message.answer("Noto‘g‘ri raqam.")
                return
            astate["mode"] = "EDIT_SAVE"
            astate["idx"] = idx
            await message.answer("Yangi formatni yuboring:\nSavol | A | B | C | D | To‘g‘ri javob")
            return
        if mode == "EDIT_SAVE":
            try:
                parts = [p.strip() for p in text.split("|")]
                if len(parts) < 3:
                    await message.answer("❌ Format xato!")
                    return
                q = parts[0]
                answers = parts[1:-1]
                correct = parts[-1]
                questions[astate["idx"]] = {"question": q, "answers": answers, "correct": correct}
                admin_state.pop(user_id, None)
                await message.answer("✅ Tahrirlandi!", reply_markup=admin_kb)
            except Exception as e:
                await message.answer(f"Xato: {e}")
            return
        if mode == "DELETE_PICK":
            if not text.isdigit():
                await message.answer("Raqam yuboring.")
                return
            idx = int(text) - 1
            if idx < 0 or idx >= len(questions):
                await message.answer("Noto‘g‘ri raqam.")
                return
            deleted = questions.pop(idx)
            admin_state.pop(user_id, None)
            await message.answer(f"✅ O‘chirildi: {deleted['question']}", reply_markup=admin_kb)
            return

    # Test oqimi
    if user_id not in test_state:
        return
    state = test_state[user_id]
    if state["i"] >= len(questions):
        return
    q = questions[state["i"]]
    if text == q["correct"]:
        state["score"] += 1
        await message.answer("To‘g‘ri ✅")
    else:
        state["score"] -= 1
        await message.answer("Xato ❌")
    state["i"] += 1
    if state["i"] < len(questions):
        q = questions[state["i"]]
        await message.answer(q["question"], reply_markup=make_answers_kb(q["answers"]))
    else:
        await message.answer(f"Tugadi! Ballingiz: {state['score']} 🎯")

# BOTNI ISHGA TUSHIRISH
async def main():
    print("Bot ishga tushdi ✅")
    await dp.start_polling(bot)

>>>>>>> ec58fc070b0dc7319df16daa41221ef198c9dab8
if __name__ == "__main__":
    asyncio.run(main())
