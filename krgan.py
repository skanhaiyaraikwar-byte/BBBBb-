import asyncio
import os
import re
import sys
import json
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

TOKEN = "8416186963:AAFAdF-Vsh9AW4xzyg4h1CIzmL_iHbcoot0"

# -------- Per-user storage --------
user_processes = {}   # {user_id: process}
user_proxy = {}        # {user_id: True/False}

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ACCOUNTS_FOLDER = os.path.join(CURRENT_DIR, "ACCOUNTS")  # स्क्रिप्ट वाली फाइल

# -------- START COMMAND --------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [['🚀 Start Script', '🛑 Stop Script'], ['📊 Status']]

    inline_buttons = [
        [InlineKeyboardButton("📝 Show Accounts", callback_data="show_account")],
        [InlineKeyboardButton("🌐 Add Proxy", callback_data="add_proxy")]
    ]

    await update.message.reply_text(
        "🤖 Controller Active",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

    await update.message.reply_text(
        "Feature buttons:",
        reply_markup=InlineKeyboardMarkup(inline_buttons)
    )


# -------- SCRIPT RUNNER --------
async def run_script(update: Update):
    user_id = update.effective_user.id
    script_file = "gan.py"

    if not os.path.exists(script_file):
        await update.message.reply_text("❌ Script file not found.")
        return

    process = await asyncio.create_subprocess_exec(
        sys.executable, script_file,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT
    )

    user_processes[user_id] = process
    await update.message.reply_text("✅ Script started.")

    # Create per-user bot file
    bot_file = os.path.join(CURRENT_DIR, f"BOT_ACCOUNTS_{user_id}.json")
    if not os.path.exists(bot_file):
        with open(bot_file, "w") as f:
            json.dump([], f)

    while True:
        line = await process.stdout.read(1024)
        if not line:
            break

        output = line.decode(errors="ignore").strip()
        clean_text = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', output)

        if clean_text:
            # Save account lines to per-user BOT file
            if "Name:" in clean_text or "Registration" in clean_text:
                try:
                    with open(bot_file, "r") as f:
                        accounts = json.load(f)

                    accounts.append({
                        "text": clean_text,
                        "time": datetime.now().strftime('%H:%M:%S')
                    })

                    with open(bot_file, "w") as f:
                        json.dump(accounts, f, indent=2)
                except:
                    pass

            await update.message.reply_text(clean_text)

    await process.wait()
    user_processes.pop(user_id, None)


# -------- HANDLE MESSAGES --------
async def handle_everything(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    process = user_processes.get(user_id)

    if text == '🚀 Start Script':
        if process and process.returncode is None:
            await update.message.reply_text("⚠️ Already running.")
        else:
            asyncio.create_task(run_script(update))

    elif text == '🛑 Stop Script':
        if process:
            process.terminate()
            user_processes.pop(user_id, None)
            await update.message.reply_text("🛑 Script stopped.")
        else:
            await update.message.reply_text("No script running.")

    elif text == '📊 Status':
        msg = "🟢 RUNNING" if process and process.returncode is None else "🔴 STOPPED"
        await update.message.reply_text(f"Status: {msg}")

    else:
        if process and process.returncode is None:
            process.stdin.write((text + "\n").encode())
            await process.stdin.drain()
        else:
            await update.message.reply_text("❌ Start script first.")


# -------- BUTTON HANDLER --------
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    # Per-user bot file
    bot_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"BOT_ACCOUNTS_{user_id}.json")

    if query.data == "show_account":
        if not os.path.exists(bot_file):
            await query.message.reply_text("No accounts stored yet.")
            return

        with open(bot_file, "r") as f:
            accounts = json.load(f)

        if not accounts:
            await query.message.reply_text("⚠️ You have no accounts yet.")
            return

        for i, acc in enumerate(accounts, 1):
            await query.message.reply_text(
                f"📝 Account #{i}\n{acc['text']}"
            )

        # clear file after sending
        with open(bot_file, "w") as f:
            json.dump([], f)

    elif query.data == "add_proxy":
        if not user_proxy.get(user_id):
            user_proxy[user_id] = True
            await query.message.reply_text("🌐 Proxy enabled.")
        else:
            await query.message.reply_text("Proxy already active.")


# -------- MAIN --------
if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_everything))
    app.add_handler(CallbackQueryHandler(button_handler))

    app.run_polling()