import os
from dotenv import load_dotenv

load_dotenv()  # بارگذاری فایل .env

TOKEN = os.getenv("BOT_TOKEN")

ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "").split(",")))

GITHUB_FILES = {
    'inventory': 'https://raw.githubusercontent.com/username/repo/main/inventory.xlsx',
    'brand_files': [
        'https://raw.githubusercontent.com/username/repo/main/brand1.xlsx',
        'https://raw.githubusercontent.com/username/repo/main/brand2.xlsx',
        # فایل‌های بیشتر برند اینجا...
    ]
}

FINAL_FILENAME = 'final_inventory.xlsx'
