import time
from utils import generate_final_inventory

INTERVAL = 300  # 300 ثانیه = 5 دقیقه

def main():
    print("آپدیتر موجودی شروع به کار کرد...")
    while True:
        try:
            generate_final_inventory()
        except Exception as e:
            print(f"خطا در آپدیت موجودی: {e}")
        time.sleep(INTERVAL)

if __name__ == "__main__":
    main()
