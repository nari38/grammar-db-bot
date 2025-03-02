import requests
from flask import Flask, request
import json

TOKEN = "YOUR_DATABASE_BOT_TOKEN"
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

app = Flask(__name__)

data_file = "database.json"

def load_data():
    try:
        with open(data_file, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"free_materials": [], "resources": [], "daily_word": ""}

def save_data(data):
    with open(data_file, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def send_message(chat_id, text):
    url = f"{BASE_URL}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text})

@app.route(f"/bot{TOKEN}", methods=["POST"])
def receive_update():
    update = request.get_json()
    if "message" in update:
        chat_id = update["message"]["chat"]["id"]
        text = update["message"].get("text", "")

        data = load_data()

        if text.startswith("/get"):
            parts = text.split(" ")
            if len(parts) == 2:
                category = parts[1]
                if category in data:
                    if isinstance(data[category], list):  # Если список, отправляем каждый элемент отдельно
                        for item in data[category]:
                            send_message(chat_id, item)
                    else:
                        send_message(chat_id, data[category])
                else:
                    send_message(chat_id, "❌ Нет данных в этой категории.")
            else:
                send_message(chat_id, "❌ Использование: /get category")

        elif text.startswith("/add"):
            parts = text.split(" ", 2)
            if len(parts) == 3:
                category, content = parts[1], parts[2]
                if category in data and isinstance(data[category], list):
                    data[category].append(content)
                else:
                    data[category] = [content]
                save_data(data)
                send_message(chat_id, f"✅ Добавлено в {category}!")
            else:
                send_message(chat_id, "❌ Использование: /add category content")

        elif text.startswith("/set_daily_word"):
            parts = text.split(" ", 1)
            if len(parts) == 2:
                data["daily_word"] = parts[1]
                save_data(data)
                send_message(chat_id, "✅ Слово дня обновлено!")
            else:
                send_message(chat_id, "❌ Использование: /set_daily_word слово")

    return "OK"

if __name__ == "__main__":
    app.run(port=5002)
