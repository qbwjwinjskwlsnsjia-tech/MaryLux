import telebot
from telebot import types
import random
import json
import os

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise RuntimeError("BOT_TOKEN is not configured")

bot = telebot.TeleBot(TOKEN)

DATA_FILE = "users.json"
users = {}
pending = {}

def load_users():
    global users
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            users = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        users = {}

def save_users():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

def get_user(message):
    uid = str(message.from_user.id)
    if uid not in users:
        users[uid] = {
            "name": message.from_user.first_name or "کاربر",
            "score": 0
        }
        save_users()
    return users[uid]

def main_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("🤖 هوش مصنوعی", "🎮 سرگرمی")
    kb.row("👤 پروفایل", "🏆 امتیازات")
    kb.row("ℹ️ راهنما")
    return kb

def game_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("🧩 معما", "🎯 حقیقت")
    kb.row("🔥 جرئت", "🔙 بازگشت")
    return kb

riddles = [
    ("آن چیست که دندان دارد ولی غذا نمی‌خورد؟", "شانه"),
    ("هرچه از آن برداری بزرگ‌تر می‌شود؟", "گودال"),
    ("پا ندارد ولی راه می‌رود؟", "ساعت"),
    ("همیشه جلو می‌رود و برنمی‌گردد؟", "زمان")
]

truths = [
    "بزرگ‌ترین آرزوت چیه؟",
    "بهترین خاطره‌ات چیه؟",
    "چه مهارتی دوست داری یاد بگیری؟",
    "بزرگ‌ترین هدفت چیه؟"
]

dares = [
    "یک جوک تعریف کن!",
    "اسم پنج میوه رو بگو!",
    "یک جمله خنده‌دار بساز!",
    "یک شعر کوتاه بخون!"
]

@bot.message_handler(commands=["start"])
def start(message):
    user = get_user(message)
    bot.send_message(
        message.chat.id,
        f"💗 سلام {user['name']}!\n"
        "به MaryLux خوش اومدی!\n"
        "از منوی زیر استفاده کن 🌸",
        reply_markup=main_menu()
    )

@bot.message_handler(commands=["cancel"])
def cancel(message):
    pending.pop(str(message.from_user.id), None)
    bot.send_message(
        message.chat.id,
        "بازی لغو شد 🌸",
        reply_markup=game_menu()
    )

@bot.message_handler(func=lambda m: m.text == "👤 پروفایل")
def profile(message):
    user = get_user(message)
    bot.reply_to(
        message,
        f"👤 نام: {user['name']}\n"
        f"⭐ امتیاز: {user['score']}"
    )

@bot.message_handler(func=lambda m: m.text == "🏆 امتیازات")
def scores(message):
    user = get_user(message)
    bot.reply_to(
        message,
        f"🏆 امتیاز شما: {user['score']}"
    )

@bot.message_handler(func=lambda m: m.text == "🎮 سرگرمی")
def games(message):
    bot.send_message(
        message.chat.id,
        "🎮 بازی مورد علاقه‌ات رو انتخاب کن:",
        reply_markup=game_menu()
    )

@bot.message_handler(func=lambda m: m.text == "🧩 معما")
def riddle(message):
    question, answer = random.choice(riddles)
    pending[str(message.from_user.id)] = answer
    bot.send_message(
        message.chat.id,
        "🧩 معمای MaryLux:\n" + question +
        "\n\nبرای لغو بازی /cancel رو بزن."
    )

@bot.message_handler(func=lambda m: m.text == "🎯 حقیقت")
def truth(message):
    bot.send_message(
        message.chat.id,
        "🎯 حقیقت:\n" + random.choice(truths)
    )

@bot.message_handler(func=lambda m: m.text == "🔥 جرئت")
def dare(message):
    bot.send_message(
        message.chat.id,
        "🔥 جرئت:\n" + random.choice(dares)
    )

@bot.message_handler(func=lambda m: m.text == "🔙 بازگشت")
def back(message):
    pending.pop(str(message.from_user.id), None)
    bot.send_message(
        message.chat.id,
        "به منوی اصلی برگشتی 💗",
        reply_markup=main_menu()
    )

@bot.message_handler(func=lambda m: m.text == "🤖 هوش مصنوعی")
def ai(message):
    bot.send_message(
        message.chat.id,
        "🤖 بخش هوش مصنوعی به‌زودی فعال می‌شود!"
    )

@bot.message_handler(func=lambda m: m.text == "ℹ️ راهنما")
def help_user(message):
    bot.send_message(
        message.chat.id,
        "💗 راهنمای MaryLux\n"
        "🎮 بازی و سرگرمی\n"
        "👤 پروفایل\n"
        "🏆 امتیازات\n"
        "/cancel لغو بازی"
    )

@bot.message_handler(func=lambda m: True)
def answer(message):
    uid = str(message.from_user.id)

    if uid in pending:
        correct = pending.pop(uid)
        user = get_user(message)

        if message.text.strip() == correct:
            user["score"] += 10
            save_users()
            bot.reply_to(
                message,
                "آفرین! 🌟 ۱۰ امتیاز گرفتی!"
            )
        else:
            bot.reply_to(
                message,
                f"جواب درست: {correct}\n"
                "دوباره امتحان کن! 💗"
            )
    else:
        bot.reply_to(
            message,
            "از منوی اصلی یک گزینه انتخاب کن 🌸",
            reply_markup=main_menu()
        )

load_users()

print("MaryLux is starting...")

bot.infinity_polling(skip_pending=True)
import telebot
from telebot import types
import random
import json
import os

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise RuntimeError("BOT_TOKEN is not configured")

bot = telebot.TeleBot(TOKEN)

DATA_FILE = "users.json"
users = {}
pending = {}

def load_users():
    global users
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            users = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        users = {}

def save_users():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

def get_user(message):
    uid = str(message.from_user.id)
    if uid not in users:
        users[uid] = {
            "name": message.from_user.first_name or "کاربر",
            "score": 0
        }
        save_users()
    return users[uid]

def main_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("🤖 هوش مصنوعی", "🎮 سرگرمی")
    kb.row("👤 پروفایل", "🏆 امتیازات")
    kb.row("ℹ️ راهنما")
    return kb

def game_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("🧩 معما", "🎯 حقیقت")
    kb.row("🔥 جرئت", "🔙 بازگشت")
    return kb

riddles = [
    ("آن چیست که دندان دارد ولی غذا نمی‌خورد؟", "شانه"),
    ("هرچه از آن برداری بزرگ‌تر می‌شود؟", "گودال"),
    ("پا ندارد ولی راه می‌رود؟", "ساعت"),
    ("همیشه جلو می‌رود و برنمی‌گردد؟", "زمان")
]

truths = [
    "بزرگ‌ترین آرزوت چیه؟",
    "بهترین خاطره‌ات چیه؟",
    "چه مهارتی دوست داری یاد بگیری؟",
    "بزرگ‌ترین هدفت چیه؟"
]

dares = [
    "یک جوک تعریف کن!",
    "اسم پنج میوه رو بگو!",
    "یک جمله خنده‌دار بساز!",
    "یک شعر کوتاه بخون!"
]

@bot.message_handler(commands=["start"])
def start(message):
    user = get_user(message)
    bot.send_message(
        message.chat.id,
        f"💗 سلام {user['name']}!\n"
        "به MaryLux خوش اومدی!\n"
        "از منوی زیر استفاده کن 🌸",
        reply_markup=main_menu()
    )

@bot.message_handler(commands=["cancel"])
def cancel(message):
    pending.pop(str(message.from_user.id), None)
    bot.send_message(
        message.chat.id,
        "بازی لغو شد 🌸",
        reply_markup=game_menu()
    )

@bot.message_handler(func=lambda m: m.text == "👤 پروفایل")
def profile(message):
    user = get_user(message)
    bot.reply_to(
        message,
        f"👤 نام: {user['name']}\n"
        f"⭐ امتیاز: {user['score']}"
    )

@bot.message_handler(func=lambda m: m.text == "🏆 امتیازات")
def scores(message):
    user = get_user(message)
    bot.reply_to(
        message,
        f"🏆 امتیاز شما: {user['score']}"
    )

@bot.message_handler(func=lambda m: m.text == "🎮 سرگرمی")
def games(message):
    bot.send_message(
        message.chat.id,
        "🎮 بازی مورد علاقه‌ات رو انتخاب کن:",
        reply_markup=game_menu()
    )

@bot.message_handler(func=lambda m: m.text == "🧩 معما")
def riddle(message):
    question, answer = random.choice(riddles)
    pending[str(message.from_user.id)] = answer
    bot.send_message(
        message.chat.id,
        "🧩 معمای MaryLux:\n" + question +
        "\n\nبرای لغو بازی /cancel رو بزن."
    )

@bot.message_handler(func=lambda m: m.text == "🎯 حقیقت")
def truth(message):
    bot.send_message(
        message.chat.id,
        "🎯 حقیقت:\n" + random.choice(truths)
    )

@bot.message_handler(func=lambda m: m.text == "🔥 جرئت")
def dare(message):
    bot.send_message(
        message.chat.id,
        "🔥 جرئت:\n" + random.choice(dares)
    )

@bot.message_handler(func=lambda m: m.text == "🔙 بازگشت")
def back(message):
    pending.pop(str(message.from_user.id), None)
    bot.send_message(
        message.chat.id,
        "به منوی اصلی برگشتی 💗",
        reply_markup=main_menu()
    )

@bot.message_handler(func=lambda m: m.text == "🤖 هوش مصنوعی")
def ai(message):
    bot.send_message(
        message.chat.id,
        "🤖 بخش هوش مصنوعی به‌زودی فعال می‌شود!"
    )

@bot.message_handler(func=lambda m: m.text == "ℹ️ راهنما")
def help_user(message):
    bot.send_message(
        message.chat.id,
        "💗 راهنمای MaryLux\n"
        "🎮 بازی و سرگرمی\n"
        "👤 پروفایل\n"
        "🏆 امتیازات\n"
        "/cancel لغو بازی"
    )

@bot.message_handler(func=lambda m: True)
def answer(message):
    uid = str(message.from_user.id)

    if uid in pending:
        correct = pending.pop(uid)
        user = get_user(message)

        if message.text.strip() == correct:
            user["score"] += 10
            save_users()
            bot.reply_to(
                message,
                "آفرین! 🌟 ۱۰ امتیاز گرفتی!"
            )
        else:
            bot.reply_to(
                message,
                f"جواب درست: {correct}\n"
                "دوباره امتحان کن! 💗"
            )
    else:
        bot.reply_to(
            message,
            "از منوی اصلی یک گزینه انتخاب کن 🌸",
            reply_markup=main_menu()
        )

load_users()

print("MaryLux is starting...")

bot.infinity_polling(skip_pending=True)
