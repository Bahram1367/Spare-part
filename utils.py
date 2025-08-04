import pandas as pd
import requests
from io import BytesIO
from config import FILE_URLS, FINAL_FILE_NAME

def download_excel(url):
    response = requests.get(url)
    return pd.read_excel(BytesIO(response.content))

def generate_final_inventory():
    print("📥 دریافت و پردازش فایل‌ها...")
    
    inventory_df = download_excel(FILE_URLS['inventory'])

    brand_dfs = []
    for url in FILE_URLS['brands']:
        df = download_excel(url)
        brand_dfs.append(df)

    combined_brands = pd.concat(brand_dfs, ignore_index=True)

    # حذف آیتم‌های تکراری براساس کد و نام کالا
    combined_brands.drop_duplicates(subset=["کدکالا", "نام کالا"], keep="last", inplace=True)

    # ترکیب موجودی با برندها
    merged_df = pd.merge(inventory_df, combined_brands, on=["کدکالا", "نام کالا"], how="inner")

    # مرتب‌سازی براساس نام کالا
    merged_df.sort_values(by="نام کالا", inplace=True)

    # ذخیره فایل نهایی
    merged_df.to_excel(FINAL_FILE_NAME, index=False)
    print("✅ فایل نهایی ساخته شد:", FINAL_FILE_NAME)

async def send_inventory_file(update, context):
    chat_id = update.effective_chat.id
    await context.bot.send_document(chat_id=chat_id, document=open(FINAL_FILE_NAME, "rb"), filename="موجودی_با_قیمت.xlsx")
