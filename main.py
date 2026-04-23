
```python
import logging
import pandas as pd
from thefuzz import process
from telegram import ReplyKeyboardMarkup, Update, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler

# --- تنظیمات سجاد (اینجا را پر کن) ---
TOKEN = "توکن_ربات_بله_شما"
ADMIN_ID = "آیدی_عددی_شما" 
CASH_BRANDS = ["Hafner", "Optibelt", "Visiun", "Mashita", "Click"]

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

GET_PRODUCT, GET_COUNT = range(2)

def load_data():
    try:
        return pd.read_excel("prices.xlsx")
    except:
        return pd.DataFrame(columns=['code', 'name', 'brand', 'price'])

def start(update: Update, context: CallbackContext):
    context.user_data['cart'] = []
    update.message.reply_text(
        "سلام! به سیستم ثبت سفارش خوش آمدید.\nنام قطعه مورد نظر را بنویسید:",
        reply_markup=ReplyKeyboardMarkup([['ثبت نهایی']], resize_keyboard=True)
    )
    return GET_PRODUCT

def search_product(update: Update, context: CallbackContext):
    query = update.message.text
    if query == 'ثبت نهایی': return finish_order(update, context)
    df = load_data()
    choices = df['name'].tolist()
    results = process.extract(query, choices, limit=3)
    buttons = [[res[0]] for res in results if res[1] > 50]
    if not buttons:
        update.message.reply_text("پیدا نشد. دوباره تلاش کنید.")
        return GET_PRODUCT
    update.message.reply_text("کدام کالا؟", reply_markup=ReplyKeyboardMarkup(buttons + [['انصراف']], resize_keyboard=True))
    return GET_COUNT

def add_to_cart(update: Update, context: CallbackContext):
    product_name = update.message.text
    if product_name == 'انصراف': return start(update, context)
    df = load_data()
    product_info = df[df['name'] == product_name].iloc[0]
    context.user_data['current_item'] = product_info.to_dict()
    update.message.reply_text(f"تعداد برای {product_name}:", reply_markup=ReplyKeyboardRemove())
    return GET_COUNT

def get_count(update: Update, context: CallbackContext):
    try:
        count = int(update.message.text)
    except:
              update.message.reply_text("فقط عدد بفرستید.")
        return GET_COUNT
    
    item = context.user_data['current_item']
    item['count'] = count
    context.user_data['cart'].append(item)
    
    # منطق اپتی‌بلت
    if "Optibelt" in str(item['brand']) and "تسمه تایم" in str(item['name']):
        context.user_data['cart'].append({
            'code': 'Gift', 'name': 'تسمه دینام جفت (اپتی)', 'brand': 'Optibelt', 'price': 0, 'count': count
        })
        update.message.reply_text("✅ تسمه دینام جفت اضافه شد.")

    update.message.reply_text("اضافه شد. بعدی؟", reply_markup=ReplyKeyboardMarkup([['ثبت نهایی']], resize_keyboard=True))
    return GET_PRODUCT

def finish_order(update: Update, context: CallbackContext):
    cart = context.user_data.get('cart', [])
    if not cart: return start(update, context)
    
    report = "📝 صورت سفارش:\n\n"
    cash_sum, check_sum = 0, 0
    for i in cart:
        line = f"- {i['code']} | {i['name']} | {i['count']} عدد | {i['price']:,} ت\n"
        report += line
        if any(b in str(i['brand']) for b in CASH_BRANDS): cash_sum += i['price'] * i['count']
        else: check_sum += i['price'] * i['count']
    
    final_text = report + f"\nنقد: {cash_sum:,} | چکی: {check_sum:,}"
    update.message.reply_text(final_text + "\nثبت شد!")
    context.bot.send_message(chat_id=ADMIN_ID, text=f"سفارش جدید:\n{final_text}")
    return ConversationHandler.END

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    conv = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            GET_PRODUCT: [MessageHandler(Filters.text & ~Filters.command, search_product)],
            GET_COUNT: [MessageHandler(Filters.regex(r'^\d+$'), get_count), MessageHandler(Filters.text, add_to_cart)]
        },
        fallbacks=[CommandHandler('start', start)]
    )
    dp.add_handler(conv)
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
```

