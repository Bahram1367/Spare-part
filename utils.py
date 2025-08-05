import pandas as pd
import requests
from io import BytesIO
from config import FILE_URLS, FINAL_FILE_NAME

def download_excel(url):
    try:
        print(f"📡 در حال دانلود فایل: {url}")
        response = requests.get(url)
        response.raise_for_status()
        return pd.read_excel(BytesIO(response.content), engine='openpyxl')
    except Exception as e:
        print(f"❌ خطا در دانلود یا خواندن فایل {url}: {e}")
        return pd.DataFrame()

def generate_final_inventory():
    print("📥 شروع دانلود و پردازش فایل‌ها...")

    # دانلود فایل موجودی اصلی
    inventory_df = download_excel(FILE_URLS['inventory'])

    if inventory_df.empty:
        print("⚠️ فایل موجودی بارگذاری نشد. عملیات متوقف شد.")
        return

    # دانلود و ترکیب فایل‌های برند
    brand_dfs = []
    for url in FILE_URLS['brands']:
        df = download_excel(url)
        if not df.empty:
            brand_dfs.append(df)

    if not brand_dfs:
        print("⚠️ هیچ فایل برند معتبری یافت نشد. عملیات متوقف شد.")
        return

    combined_brands = pd.concat(brand_dfs, ignore_index=True)
    print(f"🧮 تعداد کل ردیف‌های برند: {len(combined_brands)}")

    # حذف داده‌های تکراری بر اساس کدکالا و نام کالا
    combined_brands.drop_duplicates(subset=["کدکالا", "نام کالا"], keep="last", inplace=True)

    # ادغام موجودی با برندها
    merged_df = pd.merge(inventory_df, combined_brands, on=["کدکالا", "نام کالا"], how="inner")
    print(f"✅ تعداد ردیف‌های نهایی پس از ادغام: {len(merged_df)}")

    # مرتب‌سازی نهایی و ذخیره فایل
    merged_df.sort_values(by="نام کالا", inplace=True)
    merged_df.to_excel(FINAL_FILE_NAME, index=False, engine='openpyxl')
    print(f"✅ فایل نهایی '{FINAL_FILE_NAME}' ساخته شد.")
