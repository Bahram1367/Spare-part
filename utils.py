import pandas as pd
import requests
from io import BytesIO
from config import FILE_URLS, FINAL_FILE_NAME

def download_excel(url):
    response = requests.get(url)
    response.raise_for_status()
    return pd.read_excel(BytesIO(response.content))

def generate_final_inventory():
    print("📥 شروع دانلود و پردازش فایل‌ها...")

    inventory_df = download_excel(FILE_URLS['inventory'])

    brand_dfs = []
    for url in FILE_URLS['brands']:
        df = download_excel(url)
        brand_dfs.append(df)

    combined_brands = pd.concat(brand_dfs, ignore_index=True)

    combined_brands.drop_duplicates(subset=["کدکالا", "نام کالا"], keep="last", inplace=True)

    merged_df = pd.merge(inventory_df, combined_brands, on=["کدکالا", "نام کالا"], how="inner")

    merged_df.sort_values(by="نام کالا", inplace=True)

    merged_df.to_excel(FINAL_FILE_NAME, index=False)
    print(f"✅ فایل نهایی '{FINAL_FILE_NAME}' ساخته شد.")
