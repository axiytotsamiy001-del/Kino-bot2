from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

TOKEN = "8703304211:AAFU-OPeISDFzWoFvnjOxlcFl1udjH7aSxI"
ADMIN_ID = 867449036

movies = {}
user_state = {}

# 🎬 START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎬 Kinolar", callback_data="movies")],
        [InlineKeyboardButton("🔎 Qidirish", callback_data="search")]
    ]

    await update.message.reply_text(
        "🎥 Menyuni tanlang:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# 🔘 BUTTONS
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if query.data == "movies":
        if not movies:
            await query.edit_message_text("❌ Kino yo‘q")
            return

        keyboard = []
        for name in movies:
            keyboard.append([InlineKeyboardButton(name, callback_data=f"movie_{name}")])

        await query.edit_message_text(
            "🎬 Kinolar:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data.startswith("movie_"):
        name = query.data.split("_", 1)[1]
        file_id = movies.get(name)

        if file_id:
            await context.bot.send_video(
                chat_id=query.message.chat_id,
                video=file_id,
                caption=f"🎬 {name}"
            )

    elif query.data == "search":
        user_state[user_id] = "search"
        await query.edit_message_text("🔎 Kino nomini yozing")

# 💬 USER MESSAGE
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id

    # 🔎 SEARCH
    if user_state.get(user_id) == "search":
        res = movies.get(text.lower())

        if res:
            await context.bot.send_video(
                chat_id=update.effective_chat.id,
                video=res,
                caption=f"🎬 {text}"
            )
        else:
            await update.message.reply_text("❌ Topilmadi")

        user_state[user_id] = None
        return

# 👑 ADMIN COMMAND
async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    user_state[update.effective_user.id] = "add_name"
    await update.message.reply_text("🎬 Kino nomini yozing")

# 👑 ADMIN HANDLE
async def admin_handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id != ADMIN_ID:
        return

    # kino nomi
    if user_state.get(user_id) == "add_name":
        user_state[user_id] = {"name": update.message.text}
        await update.message.reply_text("🎥 Endi kino VIDEONI yubor")
        return

    # video qabul qilish
    if isinstance(user_state.get(user_id), dict):
        if update.message.video:
            file_id = update.message.video.file_id
            name = user_state[user_id]["name"]

            movies[name.lower()] = file_id
            user_state[user_id] = None

            await update.message.reply_text("✅ Kino saqlandi")
        else:
            await update.message.reply_text("❗ Video yubor")

        return

# 🤖 APP
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("add", add))
app.add_handler(CallbackQueryHandler(buttons))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
app.add_handler(MessageHandler(filters.ALL, admin_handle))

print("🔥 FULL VIDEO BOT ISHLAYAPTI")
app.run_polling()
