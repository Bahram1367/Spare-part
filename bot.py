import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes,
    CallbackQueryHandler, MessageHandler, filters
)
from config import TOKEN, ADMIN_IDS, FINAL_FILENAME
from utils import (
    add_user, is_user_approved, load_users
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# دکمه ها
def main_keyboard():
    keyboard = [[InlineKeyboardButton("📥 دریافت موجودی", callback_data='get_inventory')]]
    return InlineKeyboardMarkup(keyboard)

# دستور استارت
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if is_user_approved(user_id):
        await update.message.reply_text(
            "سلام! خوش آمدی.\nبرای دریافت موجودی از دکمه زیر استفاده کن.",
            reply_markup=main_keyboard()
        )
    else:
        await update.message.reply_text(
            "سلام! برای استفاده از ربات ابتدا باید درخواست عضویت بدهی.\n"
            "برای درخواست عضویت دستور /join را ارسال کن."
        )

# دستور درخواست عضویت
async def join_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id

    if is_user_approved(user_id):
        await update.message.reply_text("شما قبلاً عضو شده‌اید و نیازی به درخواست مجدد نیست.")
        return

    # پیام به ادمین ها با دکمه تایید و رد
    keyboard = [
        [
            InlineKeyboardButton("✅ تایید", callback_data=f"approve_{user_id}"),
            InlineKeyboardButton("❌ رد", callback_data=f"reject_{user_id}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    for admin_id in ADMIN_IDS:
        await context.bot.send_message(
            chat_id=admin_id,
            text=f"کاربر @{user.username or user.first_name} درخواست عضویت داده است.\nآیا تایید می‌کنید؟",
            reply_markup=reply_markup
        )

    await update.message.reply_text("درخواست شما ارسال شد. لطفاً منتظر تایید ادمین باشید.")

# هندلر دکمه‌های inline
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    user_id = query.from_user.id

    if data == 'get_inventory':
        if is_user_approved(user_id):
            try:
                with open(FINAL_FILENAME, 'rb') as f:
                    await query.message.reply_document(f, filename='موجودی.xlsx')
            except Exception as e:
                await query.message.reply_text("خطا در ارسال فایل موجودی. لطفاً بعداً تلاش کنید.")
        else:
            await query.message.reply_text("شما عضو ربات نیستید. ابتدا درخواست عضویت بدهید.")

    elif data.startswith("approve_") or data.startswith("reject_"):
        if user_id not in ADMIN_IDS:
            await query.message.reply_text("شما اجازه انجام این کار را ندارید.")
            return

        action, target_id_str = data.split("_")
        target_id = int(target_id_str)

        if action == "approve":
            added = add_user(target_id)
            if added:
                await query.edit_message_text(f"کاربر با آی‌دی {target_id} تایید شد و به لیست اعضا اضافه گردید.")
                try:
                    await context.bot.send_message(chat_id=target_id, text="عضویت شما تایید شد. اکنون می‌توانید از ربات استفاده کنید.")
                except:
                    pass
            else:
                await query.edit_message_text("کاربر قبلاً عضو شده است.")
        elif action == "reject":
            await query.edit_message_text(f"درخواست عضویت کاربر با آی‌دی {target_id} رد شد.")
            try:
                await context.bot.send_message(chat_id=target_id, text="متأسفانه درخواست عضویت شما رد شد.")
            except:
                pass

async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("دستور نامعتبر است. لطفاً از دستورهای موجود استفاده کنید.")

def main():
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('join', join_request))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.COMMAND, unknown_command))

    print("ربات شروع به کار کرد...")
    application.run_polling()

if __name__ == '__main__':
    main()
