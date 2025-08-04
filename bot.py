import asyncio
import logging
import threading
import schedule
import time

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from utils import generate_final_inventory, send_inventory_file
from config import BOT_TOKEN, ADMIN_IDS

logging.basicConfig(level=logging.INFO)

# وقتی کاربر پیام داد
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if str(user_id) not in ADMIN_IDS:
        await update.message.reply_text("⛔ دسترسی شما محدود شده.")
        return
    await send_inventory_file(update, context)

# زمان‌بندی روزانه ۲ بار
def run_scheduler():
    schedule.every().day.at("10:00").do(generate_final_inventory)
    schedule.every().day.at("17:00").do(generate_final_inventory)
    print("🕘 زمان‌بندی اجرا می‌شود: 10:00 و 17:00 روزانه")

    while True:
        schedule.run_pending()
        time.sleep(60)

# اجرای اصلی
async def main():
    # ساخت فایل نهایی هنگام شروع
    print("🔧 ساخت اولیه فایل موجودی...")
    generate_final_inventory()

    # اجرای زمان‌بندی در ترد جداگانه
    threading.Thread(target=run_scheduler, daemon=True).start()

    # شروع ربات تلگرام
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))

    print("🤖 ربات فعال است")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
