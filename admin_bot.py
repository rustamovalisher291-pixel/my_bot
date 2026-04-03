import asyncio
from typing import Optional, cast
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command

API_TOKEN = "..."  # BotFather dan olgan token

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

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

if __name__ == "__main__":
    asyncio.run(main())
