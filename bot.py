import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

# توکن ربات تلگرام شما
TOKEN = 'YOUR_BOT_API_TOKEN'

# محصولات مصالح ساختمانی
products = {
    "Cement": 50000,
    "Bricks": 2000,
    "Steel": 100000,
    "Sand": 15000
}

# تابع شروع (Start) ربات
def start(update, context):
    user = update.message.from_user
    update.message.reply_text(f"سلام {user.first_name}! خوش آمدید به ربات فروش مصالح ساختمانی.\nبرای مشاهده محصولات، دستور /products رو وارد کنید.")

# نمایش لیست محصولات
def show_products(update, context):
    product_list = "\n".join([f"{name}: {price} تومان" for name, price in products.items()])
    update.message.reply_text(f"محصولات موجود:\n{product_list}\nبرای خرید محصول دستور /buy رو وارد کنید.")

# خرید محصول و ارسال فاکتور
def buy(update, context):
    product_name = ' '.join(context.args)
    if product_name not in products:
        update.message.reply_text("محصولی با این نام پیدا نشد. لطفا نام محصول را به درستی وارد کنید.")
        return

    price = products[product_name]
    invoice_file = create_invoice(product_name, price)

    update.message.reply_text(f"شما محصول {product_name} را به قیمت {price} تومان خریداری کردید. فاکتور به صورت فایل PDF برای شما ارسال شد.")
    update.message.reply_document(open(invoice_file, 'rb'))
    os.remove(invoice_file)  # حذف فایل بعد از ارسال

# ایجاد فاکتور PDF
def create_invoice(product_name, price):
    invoice_file = f'invoices/{product_name}_invoice.pdf'
    if not os.path.exists('invoices'):
        os.mkdir('invoices')
    
    c = canvas.Canvas(invoice_file, pagesize=letter)
    c.drawString(100, 750, f"فاکتور خرید محصول: {product_name}")
    c.drawString(100, 730, f"قیمت: {price} تومان")
    c.drawString(100, 710, f"تاریخ: {update.message.date.strftime('%Y-%m-%d %H:%M:%S')}")
    c.save()

    return invoice_file

# مدیریت خطا
def error(update, context):
    print(f"Error: {context.error}")

def main():
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # دستورات ربات
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("products", show_products))
    dispatcher.add_handler(CommandHandler("buy", buy, pass_args=True))
    
    # مدیریت خطا
    dispatcher.add_error_handler(error)

    # شروع ربات
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
