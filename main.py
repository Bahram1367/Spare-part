import os
import math
import pandas as pd
import requests
from io import BytesIO
from dotenv import load_dotenv

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext

# --- بارگذاری متغیرهای محیطی ---
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

# --- آدرس فایل‌های قیمت در گیت‌هاب ---
price_files = {
    "dinapart": "https://raw.githubusercontent.com/yourusername/yourrepo/main/prices/dinapart.xlsx",
    "amata": "https://raw.githubusercontent.com/yourusername/yourrepo/main/prices/amata.xlsx",
    "tinako": "https://raw.githubusercontent.com/yourusername/yourrepo/main/prices/tinako.xlsx",
    "hafner": "https://raw.githubusercontent.com/yourusername/yourrepo/main/prices/hafner.xlsx",
    "click": "https://raw.githubusercontent.com/yourusername/yourrepo/main/prices/click.xlsx",
    "mashita": "https://raw.githubusercontent.com/yourusername/yourrepo/main/prices/mashita.xlsx",
    "appetibel": "https://raw.githubusercontent.com/yourusername/yourrepo/main/prices/appetibel.xlsx",
    "shaygan": "https://raw.githubusercontent.com/yourusername/yourrepo/main/prices/shaygan.xlsx",
}

# --- درصد افزایش قیمت هر برند ---
price_increase = {
    "dinapart": 0.13,
    "amata": 0.13,
    "tinako": 0.13,
    "shaygan": 0.13,
    "hafner": 0.0,
    "click": 0.0,
    "mashita": 0.0,
    "appetibel": 0.0,
}

FINAL_FILE = "final_inventory_with_price.xlsx"
INVENTORY_URL = "https://raw.githubusercontent.com/yourusername/yourrepo/main/inventory/inventory.xlsx"

def round_up_price(price):
    if pd.isna(price):
        return price
    return int(math.ceil(price / 1000.0) * 1000)

def read_excel_from_url(url):
    response = requests.get(url)
    response.raise_for_status()
    return pd.read_excel(BytesIO(response.content))

def process_price_files():
    price_dfs = []
    for brand, url in price_files.items():
        df = read_excel_from_url(url)
        df["برند"] = brand

        # اعمال درصد افزایش قیمت (اگر داشته باشد)
        increase = price_increase.get(brand, 0)
        df["قیمت"] = df["قیمت"] * (1 + increase)

        # رند کردن قیمت‌ها به بالا (همه برندها)
        df["قیمت"] = df["قیمت"].apply(round_up_price)

        price_dfs.append(df)

    combined_prices = pd.concat(price_dfs, ignore_index=True)
    combined_prices = combined_prices.sort_values(by=["کدکالا", "نام کالا"])
    return combined_prices

def read_inventory_file():
    return read_excel_from_url(INVENTORY_URL)

def merge_inventory_price(inventory_df, price_df):
    def clean_text(text):
        return str(text).strip().lower().replace(" ", "")

    inventory_df["نام کالا_clean"] = inventory_df["نام کالا"].apply(clean_text)
    price_df["نام کالا_clean"] = price_df["نام کالا"].apply(clean_text)

    merged_df = pd.merge(
        inventory_df,
        price_df,
        how="inner",
        left_on=["کدکالا", "نام کالا_clean"],
        right_on=["کدکالا", "نام کالا_clean"],
        suffixes=("_inventory", "_price"),
    )

    final_df = merged_df[["ردیف_inventory", "کدکالا", "نام کالا_inventory", "برند_price", "قیمت"]].copy()
    final_df.rename(columns={
        "ردیف_inventory": "ردیف",
        "نام کالا_inventory": "نام کالا",
        "برند_price": "برند"
    }, inplace=True)

    final_df = final_df.sort_values(by=["کدکالا", "نام کالا"])
    return final_df

def build_final_file():
    try:
        print("در حال ساخت فایل نهایی موجودی با قیمت...")
        combined_prices = process_price_files()
        inventory_df = read_inventory_file()
        final_df = merge_inventory_price(inventory_df, combined_prices)
        final_df.to_excel(FINAL_FILE, index=False)
        print("✅ فایل نهایی با موفقیت ساخته شد.")
    except Exception as e:
        print(f"❌ خطا در ساخت فایل نهایی: {e}")

# ---------------- ربات تلگرام ------------------

def start(update: Update, context: CallbackContext):
    keyboard = [[InlineKeyboardButton("📦 دریافت موجودی", callback_data='get_inventory')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("سلام! برای دریافت لیست موجودی با قیمت روی دکمه زیر کلیک کن:", reply_markup=reply_markup)

def button(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id

    query.answer()

    if query.data == 'get_inventory':
        if user_id != ADMIN_ID:
            query.message.reply_text("⛔️ فقط ادمین به این ربات دسترسی دارد.")
            return

        build_final_file()  # فایل رو تازه بساز

        if not os.path.exists(FINAL_FILE):
            query.message.reply_text("⚠️ فایل موجود نیست. لطفاً بعداً تلاش کنید.")
            return

        with open(FINAL_FILE, "rb") as f:
            query.message.reply_document(f, filename="موجودی_انبار_با_قیمت.xlsx")

def main():
    if not TOKEN:
        print("❌ BOT_TOKEN در فایل .env پیدا نشد.")
        return

    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(button))

    print("✅ ربات در حال اجراست...")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
