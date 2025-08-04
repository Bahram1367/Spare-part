# utils.py

import pandas as pd
import requests
from io import BytesIO
from config import GITHUB_FILES, FINAL_FILENAME


def download_excel_from_url(url):
    """دانلود فایل اکسل از URL (مثلاً GitHub)"""
    response = requests.get(url)
    if response.status_code == 200:
        return pd.read_excel(BytesIO(response.content))
    else:
        raise Exception(f"خطا در دریافت فایل از: {url}")


def fetch_all_data():
    """خواندن موجودی و لیست برندها از GitHub"""
    inventory_df = download_excel_from_url(GITHUB_FILES['inventory'])
    
    brand_dfs = []
    for url in GITHUB_FILES['brand_files']:
        df = download_excel_from_url(url)
        brand_dfs.append(df)
    
    return inventory_df, brand_dfs


def clean_and_merge(inventory_df, brand_dfs):
    """ادغام برندها، حذف تکراری، join با موجودی"""
    
    # ادغام همه فایل‌های برند
    combined_brands = pd.concat(brand_dfs, ignore_index=True)
    
    # حذف کالاهای تکراری بر اساس کد و نام
    combined_brands.drop_duplicates(subset=["کد کالا", "نام کالا"], inplace=True)
    
    # Join با موجودی بر اساس کد و نام کالا
    merged = pd.merge(
        inventory_df,
        combined_brands,
        on=["کد کالا", "نام کالا"],
        how="inner"
    )

    # حذف ستون‌های اضافی (در صورت تکراری بودن)
    merged = merged.loc[:, ~merged.columns.duplicated()]

    # مرتب‌سازی بر اساس نام کالا (الفبایی)
    merged = merged.sort_values(by="نام کالا")
    
    return merged


def generate_final_inventory():
    """ساخت فایل نهایی اکسل"""
    try:
        inventory_df, brand_dfs = fetch_all_data()
        final_df = clean_and_merge(inventory_df, brand_dfs)
        final_df.to_excel(FINAL_FILENAME, index=False)
        print("✅ فایل نهایی موجودی با موفقیت ساخته شد.")
    except Exception as e:
        print(f"❌ خطا در ساخت فایل نهایی: {e}")
