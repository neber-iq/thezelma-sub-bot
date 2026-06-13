import requests
import json
import os
from flask import Flask, request

app = Flask(__name__)

# ================== إعدادات البوت ==================
BOT_TOKEN = "8559348024:AAEjicYYRDPdSw58PrIC5MG_Qu49lYPOkbA"

REQUIRED_CHANNELS = [
    "@thezelma1",
    "@thezelma3", 
    "@thezelma_tv",
    "@theze1ma"
]

PROTECTED_LINK = "https://t.me/theze1m"

# ================== دوال مساعدة ==================
def check_subscription(user_id):
    for channel in REQUIRED_CHANNELS:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/getChatMember"
        params = {"chat_id": channel, "user_id": user_id}
        try:
            r = requests.get(url, params=params, timeout=10)
            data = r.json()
            if not data.get("ok"):
                return False
            status = data["result"]["status"]
            if status in ["left", "kicked"]:
                return False
        except:
            return False
    return True

def send_message(chat_id, text, keyboard=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if keyboard:
        data["reply_markup"] = json.dumps({"inline_keyboard": keyboard})
    try:
        requests.post(url, data=data, timeout=10)
    except:
        pass

def edit_message(chat_id, message_id, text, keyboard=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText"
    data = {"chat_id": chat_id, "message_id": message_id, "text": text}
    if keyboard:
        data["reply_markup"] = json.dumps({"inline_keyboard": keyboard})
    try:
        requests.post(url, json=data)
    except:
        pass

def handle_start(chat_id, user_id):
    if check_subscription(user_id):
        keyboard = [[{"text": "🚀 فتح قناة التطبيقات", "url": PROTECTED_LINK}]]
        send_message(chat_id, "✅ أنت مشترك في جميع القنوات!\n\nاضغط الزر أدناه:", keyboard)
    else:
        keyboard = []
        for ch in REQUIRED_CHANNELS:
            ch_name = ch.replace("@", "")
            keyboard.append([{"text": f"📢 اشترك في {ch}", "url": f"https://t.me/{ch_name}"}])
        keyboard.append([{"text": "🔍 تأكد", "callback_data": "check"}])
        send_message(chat_id, "⚠️ اشترك بالقنوات ثم اضغط تأكد:", keyboard)

def handle_callback(chat_id, message_id, user_id):
    if check_subscription(user_id):
        keyboard = [[{"text": "🚀 فتح", "url": PROTECTED_LINK}]]
        edit_message(chat_id, message_id, "🎉 تم! اضغط الزر:", keyboard)
    else:
        edit_message(chat_id, message_id, "❌ لسا ما اكتملت. جرب مرة ثانية.")

# ================== Webhook ==================
@app.route('/webhook', methods=['POST'])
def webhook():
    update = request.get_json()
    if not update:
        return "OK", 200
    
    if "message" in update:
        msg = update["message"]
        if "text" in msg and msg["text"] == "/start":
            handle_start(msg["chat"]["id"], msg["from"]["id"])
    
    elif "callback_query" in update:
        cb = update["callback_query"]
        chat_id = cb["message"]["chat"]["id"]
        message_id = cb["message"]["message_id"]
        user_id = cb["from"]["id"]
        
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/answerCallbackQuery",
                      data={"callback_query_id": cb["id"]})
        
        if cb["data"] == "check":
            handle_callback(chat_id, message_id, user_id)
    
    return "OK", 200

@app.route('/')
def home():
    return "البوت شغال يباشا!"

application = app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
