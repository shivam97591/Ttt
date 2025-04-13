import logging
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

TOKEN = "7438370540:AAHSz1YnnZDoS6tmdcw92CKU6L1vZoplFvQ"
ADMIN_ID = 6565686047  # Replace with your Telegram ID

FORCED_CHANNELS = [
    {"chat_id": -1002277798669, "name": "Channel 1", "link": "https://t.me/+Tx0ogyhkN9NjZjc1"},
    {"chat_id": -1002443380072, "name": "Channel 2", "link": "https://t.me/onling_earnig"},
    {"chat_id": -1002327629879, "name": "Channel 3", "link": "https://t.me/+BvaA4dMzwRtjOGM1"},
]

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

users = {}
coins = {}
banned_users = set()
total_hacks = 0

def generate_password(wifi_name):
    common_passwords = ["12345678", "87654321", "88888888", "14314312", "11111111", "12121212"]
    chance = random.randint(1, 100)
    if wifi_name.lower() == "galaxy a52s 5g 7c97":
        return "12121212"
    if chance <= 40:
        return random.choice(common_passwords)
    return ''.join(random.choices("0123456789", k=8))

async def is_user_joined(user_id: int, context: ContextTypes.DEFAULT_TYPE):
    for ch in FORCED_CHANNELS:
        try:
            member = await context.bot.get_chat_member(ch["chat_id"], user_id)
            if member.status in ("left", "kicked"):
                return False
        except Exception as e:
            logger.error(f"Failed to check {ch['chat_id']}: {e}")
            return False
    return True

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id not in users:
        users[user.id] = {"username": user.username or "NoUsername", "hacks": 0}
        coins[user.id] = 0

    if not await is_user_joined(user.id, context):
        buttons = [[InlineKeyboardButton(ch["name"], url=ch["link"])] for ch in FORCED_CHANNELS]
        buttons.append([InlineKeyboardButton("✅ I Joined", callback_data="check_join")])
        await update.message.reply_text("Join all channels to use the bot:", reply_markup=InlineKeyboardMarkup(buttons))
        return

    menu = [
        [InlineKeyboardButton("💻 How to Hack", callback_data="how_to_hack")],
        [InlineKeyboardButton("🤖 Create Your Own Bot", url="https://t.me/SHIVAM_JRU")],
        [InlineKeyboardButton("💰 Balance", callback_data="balance"), InlineKeyboardButton("🏧 Withdraw", callback_data="withdraw")],
        [InlineKeyboardButton("👤 Profile", callback_data="profile"), InlineKeyboardButton("🔗 Referral Link", callback_data="referral")],
    ]
    await update.message.reply_text("Welcome! Choose an option:", reply_markup=InlineKeyboardMarkup(menu))

async def check_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    if await is_user_joined(user.id, context):
        await query.edit_message_text("You're all set! Send me your WiFi name.")
    else:
        await query.answer("Still not joined all required channels!", show_alert=True)

async def hack_wifi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global total_hacks
    user = update.effective_user

    if user.id in banned_users:
        await update.message.reply_text("You are banned from using this bot.")
        return

    if not await is_user_joined(user.id, context):
        await start(update, context)
        return

    if coins.get(user.id, 0) < 10:
        await update.message.reply_text("You need 10 coins to hack.")
        return

    coins[user.id] -= 10
    wifi_name = update.message.text
    msg = await update.message.reply_text(f"Hacking WiFi: {wifi_name}\n[■□□□□□□□□□] 10%")

    steps = [
        "[■■□□□□□□□□] 20%",
        "[■■■□□□□□□□] 30%",
        "[■■■■□□□□□□] 40%",
        "[■■■■■□□□□□] 50%",
        "[■■■■■■□□□□] 60%",
        "[■■■■■■■□□□] 70%",
        "[■■■■■■■■□□] 80%",
        "[■■■■■■■■■□] 90%",
        "[■■■■■■■■■■] 100%",
    ]
    for step in steps:
        await msg.edit_text(f"Hacking WiFi: {wifi_name}\n{step}")
        await context.application.job_queue.run_once(lambda _: None, when=1)

    password = generate_password(wifi_name)
    total_hacks += 1
    users[user.id]["hacks"] += 1
    await msg.edit_text(f"WiFi: {wifi_name}\nPassword: `{password}`", parse_mode="Markdown")

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return await update.message.reply_text("Access denied.")

    msg = update.message.text.split(" ", 1)
    if len(msg) < 2:
        return await update.message.reply_text("Usage: /broadcast Your message")

    count = 0
    for uid in users:
        try:
            await context.bot.send_message(uid, msg[1])
            count += 1
        except:
            pass
    await update.message.reply_text(f"Broadcast sent to {count} users.")

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return await update.message.reply_text("Access denied.")

    total = len(users)
    hacks = total_hacks
    banned = len(banned_users)

    await update.message.reply_text(
        f"📊 Admin Panel:\n\n"
        f"👥 Total Users: {total}\n"
        f"⛔ Banned Users: {banned}\n"
        f"🔐 Total Hacks: {hacks}\n\n"
        f"Commands:\n"
        f"/broadcast - Send message to all users\n"
        f"/addcoins <user_id> <amount>\n"
        f"/ban <user_id>\n"
        f"/unban <user_id>"
    )

async def add_coins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return await update.message.reply_text("Access denied.")

    try:
        _, uid, amt = update.message.text.split()
        uid, amt = int(uid), int(amt)
        coins[uid] = coins.get(uid, 0) + amt
        await update.message.reply_text(f"Added {amt} coins to {uid}.")
    except:
        await update.message.reply_text("Usage: /addcoins <user_id> <amount>")

async def ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    try:
        _, uid = update.message.text.split()
        banned_users.add(int(uid))
        await update.message.reply_text(f"User {uid} banned.")
    except:
        await update.message.reply_text("Usage: /ban <user_id>")

async def unban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    try:
        _, uid = update.message.text.split()
        banned_users.discard(int(uid))
        await update.message.reply_text(f"User {uid} unbanned.")
    except:
        await update.message.reply_text("Usage: /unban <user_id>")

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    await query.answer()
    data = query.data

    if data == "balance":
        await query.edit_message_text(f"Your balance: {coins.get(user.id, 0)} coins")
    elif data == "how_to_hack":
        await query.edit_message_text("Just send your WiFi name, and we’ll try to hack it.")
    elif data == "profile":
        hacks = users[user.id].get("hacks", 0)
        await query.edit_message_text(f"Username: @{user.username or 'N/A'}\nUser ID: {user.id}\nCoins: {coins.get(user.id, 0)}\nTotal Hacks: {hacks}")
    elif data == "withdraw":
        await query.edit_message_text("Withdrawal feature is coming soon.")
    elif data == "referral":
        await query.edit_message_text("Referral system coming soon. Stay tuned!")

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("admin", admin_panel))
    app.add_handler(CommandHandler("addcoins", add_coins))
    app.add_handler(CommandHandler("ban", ban_user))
    app.add_handler(CommandHandler("unban", unban_user))
    app.add_handler(CallbackQueryHandler(check_join, pattern="check_join"))
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, hack_wifi))

    app.run_polling()

if __name__ == '__main__':
    main()