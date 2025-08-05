import os
from dotenv import load_dotenv

# بارگذاری متغیرهای محیطی از .env
load_dotenv()

# توکن ربات تلگرام
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN در فایل .env تعریف نشده است.")

# لیست آی‌دی‌های ادمین به صورت لیست رشته
ADMIN_IDS = os.getenv("ADMIN_IDS", "")
ADMIN_IDS = [admin.strip() for admin in ADMIN_IDS.split(",") if admin.strip()]

# نام فایل خروجی نهایی
FINAL_FILE_NAME = "final_inventory.xlsx"

# لینک فایل‌ها
FILE_URLS = {
    "inventory": "https://raw.githubusercontent.com/bahram1367/inventory-bot/main/data/inventory.xlsx",
    "brands": [
        "https://raw.githubusercontent.com/bahram1367/inventory-bot/main/data/brand_prices.xlsx",
        # فایل‌های بیشتر اینجا اضافه بشن
    ]
}
