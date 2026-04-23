
```python
import logging
import pandas as pd
from thefuzz import process
from telegram import ReplyKeyboardMarkup, Update, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler

# --- تنظیمات اختصاصی سجاد ---
TOKEN = "توکن_ربات_بله_شما"
ADMIN_ID = "آیدی_عددی_شما" 

# لیست برندهای نقدی سجاد (برای تفکیک فاکتور)
CASH_BRANDS = ["Hafner", "Optibelt", "Visiun", "Mashita", "Click"]

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
GET_PRODUCT, GET_COUNT = range(2)

def load_data():
    try:
        return pd.read_excel("prices.xlsx")
    except:
        return pd.DataFrame(columns=['code', 'name', 'brand', 'price'])

def start(update: Update, context: CallbackContext):
    context.user_data['cart'] = []
    update.message.reply_text(
        "سلام سجاد عزیز! به سیستم ثبت سفارش خوش آمدید.\nنام کالا یا برند را جستجو کنید:",
        reply_markup=ReplyKeyboardMarkup([['🛒 تایید و دریافت فاکتور']], resize_keyboard=True)
    )
    return GET_PRODUCT

def search_product(update: Update, context: CallbackContext):
    query = update.message.text
    if query == '🛒 تایید و دریافت فاکتور': return finish_order(update, context)
    
    df = load_data()
    choices = df['name'].tolist()
    results = process.extract(query, choices, limit=5)
    buttons = [[res[0]] for res in results if res[1] > 50]
    
    if not buttons:
        update.message.reply_text("موردی یافت نشد. لطفاً نام کالا را دقیق‌تر وارد کنید.")
        return GET_PRODUCT
    
    update.message.reply_text("کدام قطعه مورد نظر است؟", 
                              reply_markup=ReplyKeyboardMarkup(buttons + [['❌ انصراف']], resize_keyboard=True))
    return GET_COUNT

def add_to_cart(update: Update, context: CallbackContext):
    product_name = update.message.text
    if product_name == '❌ انصراف': return start(update, context)
    
    df = load_data()
    product_info = df[df['name'] == product_name].iloc[0]
    context.user_data['current_item'] = product_info.to_dict()
    
    # هشدار نقدی بودن برندهای خاص سجاد
    brand = str(product_info['brand'])
    msg = f"تعداد مورد نیاز برای {product_name}:"

    if any(b.lower() in brand.lower() for b in CASH_BRANDS):
        msg = f"⚠️ توجه: برند {brand} نقدی است.\n\n" + msg

    update.message.reply_text(msg, reply_markup=ReplyKeyboardRemove())
    return GET_COUNT

def get_count(update: Update, context: CallbackContext):
    try:
        count = int(update.message.text)
    except:
        update.message.reply_text("لطفاً فقط عدد (تعداد) را وارد کنید.")
        return GET_COUNT

    item = context.user_data['current_item']
    item['count'] = count
    context.user_data['cart'].append(item)

    # --- منطق هوشمند تسمه اپتی‌بلت ---
    if "Optibelt" in str(item['brand']) and "تسمه تایم" in str(item['name']):
        context.user_data['cart'].append({
            'code': 'DYNAMO-PAIR', 'name': 'تسمه دینام (جفت اجباری)', 'brand': 'Optibelt', 'price': 0, 'count': count
        })
        update.message.reply_text("✅ تسمه دینام جفت به سبد اضافه شد.")

    update.message.reply_text(f"✅ ثبت شد. کالای بعدی؟", 
                              reply_markup=ReplyKeyboardMarkup([['🛒 تایید و دریافت فاکتور']], resize_keyboard=True))
    return GET_PRODUCT

def finish_order(update: Update, context: CallbackContext):
    cart = context.user_data.get('cart', [])
    if not cart: return start(update, context)

    cash_items, check_items = [], []
    cash_total, check_total = 0, 0

    for i in cart:
        price = i.get('price', 0)
        total = price * i['count']
        if any(b.lower() in str(i['brand']).lower() for b in CASH_BRANDS):
            cash_items.append(i)
            cash_total += total
        else:
            check_items.append(i)
            check_total += total

    # ساخت متن فاکتور تفکیک شده
    report = "📄 **فاکتور نهایی سفارش**\n\n"
    
    if cash_items:
        report += "💰 **بخش نقدی (برندهای انحصاری):**\n"
        for i in cash_items:
            report += f"- {i['name']} ({i['count']} عدد)\n"
        report += f"💵 جمع نقدی: {cash_total:,} تومان\n\n"

    if check_items:
        report += "📝 **بخش چکی (روال بازار):**\n"
        for i in check_items:
            report += f"- {i['name']} ({i['count']} عدد)\n"
        report += f"💳 جمع چکی: {check_total:,} تومان\n\n"

    report += "--------------------------\n"
    report += f"🚩 **جمع کل فاکتور: {cash_total + check_total:,} تومان**"
    
    # ارسال برای سجاد و مشتری
    context.bot.send_message(chat_id=ADMIN_ID, text=f"🔔 سفارش جدید:\n\n{report}")
    update.message.reply_text(report + "\n\n✅ سفارش شما ثبت شد. برای هماهنگی تماس می‌گیریم.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    conv = ConversationHandler(
        entry_points=[CommandHandler('start', start), MessageHandler(Filters.text & ~Filters.command, search_product)],
        states={
            GET_PRODUCT: [MessageHandler(Filters.text & ~Filters.command, search_product)],
            GET_COUNT: [MessageHandler(Filters.text & ~Filters.command, get_count)],
        },
        fallbacks=[CommandHandler('start', start)]
    )
    dp.add_handler(conv)
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
```

### 📋 چک‌لیست نهایی برای گیت‌هاب:
۱. **`requirements.txt`**: شامل اون ۴ تا کتابخونه که قبلاً گفتم.
۲. **`prices.xlsx`**: فایل قیمت‌ها با ستون‌های درست.
۳. **`main.py`**: همین کد بالا (با توکن خودت).


