import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from utils import generate_final_inventory
from config import BOT_TOKEN, ADMIN_IDS, FINAL_FILE_NAME

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("دسترسی ندارید.")
        return

    keyboard = [
        [InlineKeyboardButton("دریافت موجودی", callback_data="get_inventory")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("سلام! دکمه رو بزن تا موجودی برات آماده و ارسال بشه.", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = str(query.from_user.id)

    if user_id not in ADMIN_IDS:
        await query.answer("دسترسی ندارید.", show_alert=True)
        return

    if query.data == "get_inventory":
        await query.answer("در حال آماده‌سازی فایل موجودی...")
        generate_final_inventory()
        with open(FINAL_FILE_NAME, "rb") as f:
            await context.bot.send_document(chat_id=query.message.chat_id, document=f)
        await query.message.reply_text("فایل موجودی ارسال شد.")

async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("🚀 ربات شروع به کار کرد.")
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
