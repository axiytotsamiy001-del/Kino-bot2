import json
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = "8703304211:AAFU-OPeISDFzWoFvnjOxlcFl1udjH7aSxI"
ADMIN_ID = 867449036   # o‘zingni id

CHANNEL = "@talim_guruhii"  # majburiy obuna kanali

# 📦 DATABASE
try:
    with open("db.json", "r") as f:
        movies = json.load(f)
except:
    movies = {}

def save():
    with open("db.json", "w") as f:
        json.dump(movies, f)

# 🔒 OBUNA TEKSHIRISH
async def check_sub(update, context):
    user_id = update.effective_user.id
    try:
        member = await context.bot.get_chat_member(CHANNEL, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# 🎬 START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if not await check_sub(update, context):
        await update.message.reply_text(f"❗ Avval kanalga qo‘shiling:\n{CHANNEL}")
        return

    if user_id == ADMIN_ID:
        keyboard = [
            ["🎬 Film yuklash"],
            ["📊 Statistika", "📩 Xabarnoma"],
            ["⚙️ Sozlamalar"]
        ]
    else:
        keyboard = [
            ["🎬 Kinolar menyusi"],
            ["🔎 Kino qidirish"],
            ["⭐ Top kinolar"]
        ]

    await update.message.reply_text(
        "👋 Xush kelibsiz!",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

# 🧠 STATE
state = {}

# 📩 HANDLE
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id

    if not await check_sub(update, context):
        await update.message.reply_text(f"❗ Kanalga qo‘shiling:\n{CHANNEL}")
        return

    # 🔎 QIDIRISH
    if text == "🔎 Kino qidirish":
        state[user_id] = "search"
        await update.message.reply_text("Kino nomini yozing")
        return

    # 🎬 ADMIN ADD
    if text == "🎬 Film yuklash" and user_id == ADMIN_ID:
        state[user_id] = "add_name"
        await update.message.reply_text("Kino nomi:")
        return

    # ➕ NOM
    if state.get(user_id) == "add_name":
        state[user_id] = {"name": text}
        await update.message.reply_text("Link yubor:")
        return

    # ➕ LINK
    if isinstance(state.get(user_id), dict):
        name = state[user_id]["name"]
        movies[name.lower()] = text
        save()

        state[user_id] = None
        await update.message.reply_text("✅ Saqlandi")
        return

    # 🔎 SEARCH
    if state.get(user_id) == "search":
        result = movies.get(text.lower())

        if result:
            await update.message.reply_text(f"🎬 {text}\n🔗 {result}")
        else:
            await update.message.reply_text("❌ Topilmadi")

        return

    # 🎬 MENU
    if text == "🎬 Kinolar menyusi":
        if movies:
            msg = "\n".join([f"🎬 {k}" for k in movies.keys()])
            await update.message.reply_text(msg)
        else:
            await update.message.reply_text("Hali kino yo‘q")
        return

    # ⭐ TOP
    if text == "⭐ Top kinolar":
        if movies:
            first = list(movies.items())[:5]
            msg = "\n".join([f"🔥 {k}" for k,v in first])
            await update.message.reply_text(msg)
        return

# 🤖 RUN
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

print("🔥 FULL PRO BOT ISHLAYAPTI")
app.run_polling()
