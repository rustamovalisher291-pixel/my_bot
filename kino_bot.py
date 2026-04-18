import asyncio
import json
from pathlib import Path
from typing import Optional

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

API_TOKEN = "..."  # BotFather token
ADMIN_USERNAME = "Obito_2343"  # @ belgisisiz, faqat username

DATA_PATH = Path("movies.json")

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

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


if __name__ == "__main__":
    asyncio.run(main())
