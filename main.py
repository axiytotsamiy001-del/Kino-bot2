import json
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = "8246735746:AAF7hHb4Xnmh4ufy5DPPAwAaZ-8zbRltrNc"
ADMIN_ID = 867449036
CHANNEL = "@talim_guruhii"

# 📂 load/save
def load_movies():
    try:
        with open("movies.json", "r") as f:
            return json.load(f)
    except:
        return {}

def save_movies(data):
    with open("movies.json", "w") as f:
        json.dump(data, f)

movies = load_movies()
user_state = {}

# 🔒 OBUNA TEKSHIRISH
async def check_sub(user_id, context):
    try:
        member = await context.bot.get_chat_member(CHANNEL, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# 🎬 START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_sub(update.effective_user.id, context):
        await update.message.reply_text(
            f"❌ Kanalga obuna bo‘ling:\n👉 {CHANNEL}"
        )
        return

    await update.message.reply_text(
        "🎬 Kino botga xush kelibsiz!\n\n📌 Kino kodini yuboring"
    )

# 👑 ADD
async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    user_state[update.effective_user.id] = "code"
    await update.message.reply_text("🔢 Kino kodini yozing")

# 💬 HANDLE
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    # 🔒 CHECK SUB
    if not await check_sub(user_id, context):
        await update.message.reply_text(
            f"❌ Kanalga obuna bo‘ling:\n👉 {CHANNEL}"
        )
        return

    # 👑 ADMIN
    if user_id == ADMIN_ID:
        if user_state.get(user_id) == "code":
            user_state[user_id] = {"code": text}
            await update.message.reply_text("🎥 Video yubor")
            return

        if isinstance(user_state.get(user_id), dict):
            if update.message.video:
                file_id = update.message.video.file_id
                code = user_state[user_id]["code"]

                movies[code] = file_id
                save_movies(movies)

                # 📢 KANALGA POST
                await context.bot.send_video(
                    chat_id=CHANNEL,
                    video=file_id,
                    caption=f"🎬 Kino kodi: {code}\n\n👉 Botdan olish uchun: {code}"
                )

                user_state[user_id] = None
                await update.message.reply_text(f"✅ Qo‘shildi! Kod: {code}")
            else:
                await update.message.reply_text("❗ Video yubor")

            return

    # 👤 USER
    if text in movies:
        await context.bot.send_video(
            chat_id=update.effective_chat.id,
            video=movies[text],
            caption=f"🎬 Kino kodi: {text}"
        )
    else:
        await update.message.reply_text("❌ Bunday kod yo‘q")

# 🤖 APP
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("add", add))
app.add_handler(MessageHandler(filters.TEXT | filters.VIDEO, handle))

print("🔥 FINAL PRO BOT ISHLAYAPTI")
app.run_polling()
