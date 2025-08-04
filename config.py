import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = os.getenv("ADMIN_IDS", "").split(",")

FINAL_FILE_NAME = "final_inventory.xlsx"

FILE_URLS = {
    "inventory": "https://raw.githubusercontent.com/username/repo/main/inventory.xlsx",
    "brands": [
        "https://raw.githubusercontent.com/username/repo/main/brand1.xlsx",
        "https://raw.githubusercontent.com/username/repo/main/brand2.xlsx",
        # می‌تونی برندهای بیشتر اضافه کنی
    ]
}
