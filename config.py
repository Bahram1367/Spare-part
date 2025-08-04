import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = os.getenv("ADMIN_IDS", "").split(",")

FINAL_FILE_NAME = "final_inventory.xlsx"

FILE_URLS = {
    "inventory": "https://raw.githubusercontent.com/bahram1367/repo/main/inventory.xlsx",
    "brands": [,FILE_URLS = {
    "inventory": "https://raw.githubusercontent.com/bahram1367/inventory-bot/main/data/inventory.xlsx",
    "brands": [
        "https://raw.githubusercontent.com/bahram1367/inventory-bot/main/data/brand_prices.xlsx",
    ]
}

        # می‌تونی برندهای بیشتر اضافه کنی
    ]
}
