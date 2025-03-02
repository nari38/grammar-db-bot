import requests
import telegram
from flask import Flask, request
import threading
import time
import json

TOKEN = "YOUR_MAIN_BOT_TOKEN"
DATABASE_BOT_URL = "http://your-database-bot-url/botYOUR_DATABASE_BOT_TOKEN"
ADMIN_ID = "YOUR_TELEGRAM_ID"  # Замени на свой Telegram ID

bot = telegram.Bot(token=TOKEN)
app = Flask(__name__)

users_file = "users.json"
confirmed_purchases = "confirmed.json"

def load_users():
    try:
        with open(users_file, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_users(users):
    with open(users_file, "w", encoding="utf-8") as file:
        json.dump(users, file, ensure_ascii=False, indent=4)

def load_confirmed():
    try:
        with open(confirmed_purchases, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_confirmed(data):
    with open(confirmed_purchases, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def send_daily_message():
    while True:
        time.sleep(86400)  # Ждём 24 часа
        users = load_users()
        response = requests.post(DATABASE_BOT_URL, json={"message": {"chat": {"id": users[0]}, "text": "/get daily_word"}})
        daily_word = response.text
        for user in users:
            bot.send_message(chat_id=user, text=f"📖 Слово дня: {daily_word}")

daily_thread = threading.Thread(target=send_daily_message)
daily_thread.start()

@app.route(f"/bot{TOKEN}", methods=["POST"])
def receive_update():
    update = request.get_json()
    if "message" in update:
        chat_id = update["message"]["chat"]["id"]
        text = update["message"].get("text", "")
        
        users = load_users()
        if chat_id not in users:
            users.append(chat_id)
            save_users(users)
        
        if text == "/start":
            keyboard = telegram.ReplyKeyboardMarkup([
                ["📚 Бесплатные материалы", "🛒 Купить"],
                ["🌐 Полезные ресурсы", "💡 Предложить идею"]
            ], resize_keyboard=True)
            bot.send_message(chat_id=chat_id, text="Добро пожаловать в Grammar & Chill!", reply_markup=keyboard)
            
        elif text == "📚 Бесплатные материалы":
            response = requests.post(DATABASE_BOT_URL, json={"message": {"chat": {"id": chat_id}, "text": "/get free_materials"}})
            bot.send_message(chat_id=chat_id, text=response.text)
            
        elif text == "🛒 Купить":
            bot.send_message(chat_id=chat_id, text="Для покупки переведите деньги на Kaspi и отправьте фото чека в этот чат.")
            
        elif text == "🌐 Полезные ресурсы":
            response = requests.post(DATABASE_BOT_URL, json={"message": {"chat": {"id": chat_id}, "text": "/get resources"}})
            bot.send_message(chat_id=chat_id, text=response.text)
            
        elif text == "💡 Предложить идею":
            bot.send_message(chat_id=chat_id, text="Отправьте вашу идею, и мы её рассмотрим!")
        
        elif text.startswith("/confirm") and str(chat_id) == ADMIN_ID:  # Подтверждение оплаты
            parts = text.split()
            if len(parts) == 2:
                user_id = parts[1]
                confirmed = load_confirmed()
                confirmed[user_id] = True
                save_confirmed(confirmed)
                bot.send_message(chat_id=user_id, text="✅ Оплата подтверждена! Вот ваш материал:")
                bot.send_document(chat_id=user_id, document=open("paid_material.pdf", "rb"))  # Заменить на нужный файл
                bot.send_message(chat_id=chat_id, text=f"Покупка подтверждена для пользователя {user_id}.")
            else:
                bot.send_message(chat_id=chat_id, text="Использование: /confirm USER_ID")
        
        elif text.startswith("/add_material") and str(chat_id) == ADMIN_ID:  # Добавление материала
            parts = text.split(" ", 2)
            if len(parts) == 3:
                category, content = parts[1], parts[2]
                response = requests.post(DATABASE_BOT_URL, json={"message": {"chat": {"id": chat_id}, "text": f"/add {category} {content}"}})
                bot.send_message(chat_id=chat_id, text=response.text)
            else:
                bot.send_message(chat_id=chat_id, text="Использование: /add_material category content")
    
    elif "photo" in update["message"]:  # Обработка фото чека
        chat_id = update["message"]["chat"]["id"]
        photo = update["message"]["photo"][-1]["file_id"]  # Берём самое крупное фото
        caption = f"📌 Новый чек от пользователя {chat_id}"
        bot.send_photo(chat_id=ADMIN_ID, photo=photo, caption=caption)
        bot.send_message(chat_id=chat_id, text="Чек отправлен админу. Ожидайте подтверждения.")
    
    return "OK"

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5001)))

