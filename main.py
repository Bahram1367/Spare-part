import pandas as pd
import math
import requests
from io import BytesIO

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext

# آدرس فایل‌های اکسل قیمت در گیت‌هاب (URL مستقیم)
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

# درصد افزایش قیمت برای هر برند
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

# مسیر ذخیره فایل نهایی
FINAL_FILE = "final_inventory_with_price.xlsx"

# تابع برای رند کردن قیمت به سمت بالا (سه رقم آخر صفر)
def round_up_price(price):
    return int(math.ceil(price / 1000.0) * 1000)

# دانلود و خواندن فایل اکسل از URL
def read_excel_from_url(url):
    response = requests.get(url)
    response.raise_for_status()
    return pd.read_excel(BytesIO(response.content))

# خواندن و پردازش همه فایل‌های قیمت
def process_price_files():
    price_dfs = []
    for brand, url in price_files.items():
        df = read_excel_from_url(url)
        df["برند"] = brand  # اطمینان از داشتن ستون برند
        increase = price_increase.get(brand, 0)
        # افزایش قیمت
        df["قیمت"] = df["قیمت"] * (1 + increase)
        # رند کردن قیمت به بالا
        df["قیمت"] = df["قیمت"].apply(round_up_price)
        price_dfs.append(df)
    # ادغام همه دیتافریم‌ها
    combined_prices = pd.concat(price_dfs, ignore_index=True)
    # مرتب‌سازی (مثلاً بر اساس کد کالا و نام کالا)
    combined_prices = combined_prices.sort_values(by=["کدکالا", "نام کالا"])
    return combined_prices

# خواندن فایل موجودی انبار (URL را جایگزین کن)
def read_inventory_file():
    inventory_url = "https://raw.githubusercontent.com/yourusername/yourrepo/main/inventory/inventory.xlsx"
    return read_excel_from_url(inventory_url)

# ترکیب قیمت‌ها با موجودی انبار
def merge_inventory_price(inventory_df, price_df):
    # استانداردسازی نام کالاها برای مقایسه (حروف کوچک و حذف فاصله)
    def clean_text(text):
        if isinstance(text, str):
            return text.strip().lower().replace(" ", "")
        return text

    inventory_df["نام کالا_clean"] = inventory_df["نام کالا"].apply(clean_text)
    price_df["نام کالا_clean"] = price_df["نام کالا"].apply(clean_text)

    # ادغام با شرط بر روی کدکالا و نام کالا
    merged_df = pd.merge(
        inventory_df,
        price_df,
        how="inner",
        left_on=["کدکالا", "نام کالا_clean"],
        right_on=["کدکالا", "نام کالا_clean"],
        suffixes=("_inventory", "_price"),
    )

    # ستون‌های نهایی
    final_cols = ["ردیف_inventory", "کدکالا", "نام کالا_inventory", "برند_price", "قیمت"]
    final_df = merged_df[final_cols].copy()
    final_df.rename(
        columns={
            "ردیف_inventory": "ردیف",
            "نام کالا_inventory": "نام کالا",
            "برند_price": "برند",
        },
        inplace=True,
    )
    return final_df

# ساخت فایل نهایی
def build_final_file():
    print("خواندن و پردازش فایل‌های قیمت...")
    combined_prices = process_price_files()
    print("خواندن فایل موجودی انبار...")
    inventory_df = read_inventory_file()
    print("ترکیب قیمت‌ها با موجودی انبار...")
    final_df = merge_inventory_price(inventory_df, combined_prices)
    # ذخیره خروجی
    final_df.to_excel(FINAL_FILE, index=False)
    print(f"فایل نهایی ذخیره شد: {FINAL_FILE}")

# --- بخش ربات تلگرام ---

from telegram import Bot

def start(update: Update, context: CallbackContext):
    keyboard = [[InlineKeyboardButton("دریافت موجودی", callback_data='get_inventory')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('سلام! برای دریافت موجودی روی دکمه زیر کلیک کنید:', reply_markup=reply_markup)

def button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    if query.data == 'get_inventory':
        try:
            with open(FINAL_FILE, 'rb') as f:
                query.message.reply_document(f, filename="موجودی_انبار_با_قیمت.xlsx")
        except Exception as e:
            query.message.reply_text(f"خطا در ارسال فایل: {e}")

def main():
    TOKEN = "توکن_ربات_تو_اینجا_بذار"
    # اول فایل نهایی رو بساز
    build_final_file()

    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(button))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
