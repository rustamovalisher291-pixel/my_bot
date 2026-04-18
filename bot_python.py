import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command

API_TOKEN = "8784943275:AAF8gs2vpHZ5HB5fT4hJVEnB9w2feEWudKI"  # BotFather dan olgan token

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Boshlash tugmasi
start_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Boshlash")]],
    resize_keyboard=True
)

def build_answers_kb(answers):
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=a) for a in answers]],
        resize_keyboard=True
    )

# Savollar va javoblar
questions = [
    {
        "question": "5 + 3 nechiga teng?",
        "answers": ["6", "8", "10", "12"],
        "correct": "8"
    },
    {
        "question": "O‘zbekiston poytaxti qaysi?",
        "answers": ["Samarqand", "Toshkent", "Buxoro", "Namangan"],
        "correct": "Toshkent"
    },
    {
        "question": "2 * 2 nechiga teng?",
        "answers": ["2", "3", "4", "5"],
        "correct": "4"
    },
    {
        "question": "Eng katta okean qaysi?",
        "answers": ["Atlantika", "Tinch", "Hind", "Shimoliy muz okeani"],
        "correct": "Tinch"
    }
]

# Foydalanuvchi holati
user_state = {}  # user_id: {"score": int, "current": index, "answered": bool}

# /start
@dp.message(Command(commands=["start"]))
async def cmd_start(message: types.Message):
    await message.answer(
        "Salom! Testni boshlash uchun tugmani bosing 👇",
        reply_markup=start_kb
    )

# Boshlash va javoblar
@dp.message()
async def handle_message(message: types.Message):
    user = message.from_user
    if not user:
        return
    user_id = user.id

    # Yangi foydalanuvchi
    if user_id not in user_state:
        user_state[user_id] = {"score": 0, "current": 0, "answered": False}

    state = user_state[user_id]

    # Boshlash tugmasi
    if message.text == "Boshlash":
        state["current"] = 0
        state["answered"] = False
        current_q = questions[state["current"]]
        await message.answer(current_q["question"], reply_markup=build_answers_kb(current_q["answers"]))
        return

    # Javob allaqachon berilgan bo‘lsa
    if state["answered"]:
        await message.answer("Siz allaqachon javob berdingiz! Keyingi savolni kuting 😅")
        return

    # Javobni tekshirish
    current_q = questions[state["current"]]
    if message.text == current_q["correct"]:
        state["score"] += 1
        await message.answer(f"To‘g‘ri! 🎉 Ballingiz: {state['score']}")
    else:
        state["score"] -= 1
        await message.answer(f"Xato 😅 Ballingiz: {state['score']}")

    state["answered"] = True
    state["current"] += 1

    # Keyingi savol
    if state["current"] < len(questions):
        state["answered"] = False
        next_q = questions[state["current"]]
        await message.answer(next_q["question"], reply_markup=build_answers_kb(next_q["answers"]))
    else:
        await message.answer(f"Test tugadi! Yakuniy ballingiz: {state['score']} ✅")

# Botni ishga tushirish
async def main():
    print("Bot ishga tushdi ✅")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
