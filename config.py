
python
import os
from dotenv import load_dotenv
‌
load_dotenv()
‌
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")
‌
# تنظیمات برندهای نقدی سجاد
CASH_BRANDS = ["Hafner", "Optibelt", "Visiun", "Mashita", "Click"]
‌
# تنظیمات رندر
PORT = int(os.environ.get('PORT', 8000))
