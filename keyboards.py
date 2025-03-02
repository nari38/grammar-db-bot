from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def main_menu():
    keyboard = [
        [InlineKeyboardButton("📚 Бесплатные материалы", callback_data="free_materials")],
        [InlineKeyboardButton("🛒 Купить", callback_data="buy")],
        [InlineKeyboardButton("🔗 Полезные ресурсы", callback_data="resources")],
        [InlineKeyboardButton("💡 Отправить идею", callback_data="send_idea")],
    ]
    return InlineKeyboardMarkup(keyboard)

def buy_menu():
    keyboard = [
        [InlineKeyboardButton("💳 Оплатить через Kaspi", callback_data="pay_kaspi")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")],
    ]
    return InlineKeyboardMarkup(keyboard)
