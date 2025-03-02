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

def load_users():
    try:
        with open(users_file, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_users(users):
    with open(users_file, "w", encoding="utf-8") as file:
        json.dump(users, file, ensure_ascii=False, indent=4)

def get_daily_word():
    try:
        response = requests.get(f"{DATABASE_BOT_URL}/get daily_word")
        if response.status_code == 200:
            return response.text.strip()
        else:
            return "❌ Ошибка получения слова дня."
    except requests.RequestException:
        return "❌ Не удалось связаться с базой данных."

def send_daily_message():
    while True:
        time.sleep(86400)  # Ждём 24 часа
        users = load_users()
        daily_word = get_daily_word()
        for user in users:
            bot.send_message(chat_id=user, text=f"📖 Слово дня: {daily_word}")

daily_thread = threading.Thread(target=send_daily_message, daemon=True)
daily_thread.start()

@app.route(f"/bot{TOKEN}", methods=["POST"])
def receive_update():
    update = request.get_json()
    if "message" in update:
        chat_id = update["message"]["chat"]["id"]
        text = update["message"].get("text", "").strip()
        
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
            try:
                response = requests.get(f"{DATABASE_BOT_URL}/get free_materials")
                if response.status_code == 200:
                    bot.send_message(chat_id=chat_id, text=response.text)
                else:
                    bot.send_message(chat_id=chat_id, text="❌ Ошибка получения материалов.")
            except requests.RequestException:
                bot.send_message(chat_id=chat_id, text="❌ Не удалось связаться с базой данных.")
        
        elif text == "🛒 Купить":
            bot.send_message(chat_id=chat_id, text="Для покупки переведите деньги на Kaspi и отправьте фото чека в этот чат.")
        
        elif text == "🌐 Полезные ресурсы":
            try:
                response = requests.get(f"{DATABASE_BOT_URL}/get resources")
                if response.status_code == 200:
                    bot.send_message(chat_id=chat_id, text=response.text)
                else:
                    bot.send_message(chat_id=chat_id, text="❌ Ошибка получения ресурсов.")
            except requests.RequestException:
                bot.send_message(chat_id=chat_id, text="❌ Не удалось связаться с базой данных.")
        
        elif text == "💡 Предложить идею":
            bot.send_message(chat_id=chat_id, text="Отправьте вашу идею, и мы её рассмотрим!")
    
    elif "photo" in update["message"]:  # Обработка фото чека
        chat_id = update["message"]["chat"]["id"]
        photos = update["message"]["photo"]
        if photos:
            photo_id = photos[-1]["file_id"]
            caption = f"📌 Новый чек от пользователя {chat_id}"
            bot.send_photo(chat_id=ADMIN_ID, photo=photo_id, caption=caption)
            bot.send_message(chat_id=chat_id, text="Чек отправлен админу. Ожидайте подтверждения.")
        else:
            bot.send_message(chat_id=chat_id, text="❌ Ошибка: фото не найдено.")
    
    return "OK"

if __name__ == "__main__":
    app.run(port=5001)
