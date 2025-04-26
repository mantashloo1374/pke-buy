import telebot
from config import TELEGRAM_TOKEN, ZARINPAL_MERCHANT_ID

bot = telebot.TeleBot(TELEGRAM_TOKEN)

products = {
    "سیمان": {"price_per_unit": 50000, "units": ["عدد", "تن", "مترمکعب"]},
    "آجر": {"price_per_unit": 2000, "units": ["عدد", "تن"]},
    "شن و ماسه": {"price_per_unit": 150000, "units": ["تن", "مترمکعب"]},
}

cart = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "سلام! خوش اومدی به فروشگاه مصالح ساختمانی.\nبرای دیدن محصولات /products رو بزن.")

@bot.message_handler(commands=['products'])
def list_products(message):
    text = "لیست محصولات:\n"
    for name, info in products.items():
        text += f"- {name} ({', '.join(info['units'])}) - قیمت هر واحد: {info['price_per_unit']} تومان\n"
    text += "\nلطفا اسم محصولی که میخوای رو بفرست."
    bot.send_message(message.chat.id, text)
    bot.register_next_step_handler(message, select_product)

def select_product(message):
    product_name = message.text
    if product_name in products:
        cart[message.chat.id] = {"product": product_name}
        units = products[product_name]["units"]
        markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
        for u in units:
            markup.add(u)
        bot.send_message(message.chat.id, "واحد مورد نظر رو انتخاب کن:", reply_markup=markup)
        bot.register_next_step_handler(message, select_unit)
    else:
        bot.send_message(message.chat.id, "محصول نامعتبره. دوباره /products رو بزن.")

def select_unit(message):
    unit = message.text
    product_name = cart[message.chat.id]["product"]
    if unit in products[product_name]["units"]:
        cart[message.chat.id]["unit"] = unit
        bot.send_message(message.chat.id, "چه تعداد میخوای بخری؟ (یک عدد بفرست)")
        bot.register_next_step_handler(message, select_quantity)
    else:
        bot.send_message(message.chat.id, "واحد نامعتبره. دوباره /products رو بزن.")

def select_quantity(message):
    try:
        quantity = int(message.text)
        cart[message.chat.id]["quantity"] = quantity
        generate_invoice(message)
    except ValueError:
        bot.send_message(message.chat.id, "لطفا یه عدد معتبر بفرست.")

def generate_invoice(message):
    item = cart[message.chat.id]
    price = products[item["product"]]["price_per_unit"]
    total = price * item["quantity"]
    payment_link = f"https://www.zarinpal.com/pg/StartPay/{ZARINPAL_MERCHANT_ID}?Amount={total//10}" # زرین پال ریال میخواد
    text = f"""فاکتور خرید:

محصول: {item['product']}
واحد: {item['unit']}
تعداد: {item['quantity']}
مبلغ کل: {total:,} تومان

برای پرداخت روی لینک زیر کلیک کن:
{payment_link}
"""
    bot.send_message(message.chat.id, text)

bot.infinity_polling()
