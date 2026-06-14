import requests
import json
import os
from flask import Flask, request
from datetime import datetime

app = Flask(__name__)

BOT_TOKEN = "8559348024:AAEjicYYRDPdSw58PrIC5MG_Qu49lYPOkbA"

ADMINS = [
    355449817,  # أنت
    133438395,  # صديقك
]

users = []
blocked = []

REQUIRED_CHANNELS = [
    "@thezelma1",
    "@thezelma3", 
    "@thezelma_tv",
    "@theze1ma"
]

PROTECTED_LINK = "https://t.me/theze1m"

# ================== دوال رئيسية ==================
def is_admin(user_id):
    return user_id in ADMINS

def is_blocked(user_id):
    return user_id in blocked

def add_user(user_id):
    if user_id not in users:
        users.append(user_id)

def get_user_count():
    return len(users)

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

def handle_start(chat_id, user_id):
    add_user(user_id)
    if is_blocked(user_id):
        send_message(chat_id, "⛔ تم حظرك من هذا البوت.")
        return
    if check_subscription(user_id):
        keyboard = [[{"text": "🚀 فتح الرابط", "url": PROTECTED_LINK}]]
        send_message(chat_id, "✅ أنت مشترك! اضغط الزر:", keyboard)
    else:
        keyboard = []
        for ch in REQUIRED_CHANNELS:
            ch_name = ch.replace("@", "")
            keyboard.append([{"text": f"📢 اشترك بـ {ch}", "url": f"https://t.me/{ch_name}"}])
        keyboard.append([{"text": "✅ تأكد", "callback_data": "check"}])
        send_message(chat_id, "⚠️ اشترك بالقنوات ثم اضغط تأكد:", keyboard)

def handle_check(chat_id, message_id, user_id):
    if check_subscription(user_id):
        keyboard = [[{"text": "🚀 فتح الرابط", "url": PROTECTED_LINK}]]
        edit_message(chat_id, message_id, "🎉 تم! اضغط الزر:", keyboard)
    else:
        edit_message(chat_id, message_id, "❌ لم تكتمل الاشتراكات. جرب مرة ثانية.")

# ================== لوحة تحكم الأدمن بأزرار ==================
def admin_panel(chat_id, user_id):
    if not is_admin(user_id):
        send_message(chat_id, "⛔ للأدمن فقط")
        return
    
    keyboard = [
        [{"text": "📊 الإحصائيات", "callback_data": "stats"}],
        [{"text": "📢 قنوات الاشتراك", "callback_data": "channels"}],
        [{"text": "➕ إضافة قناة", "callback_data": "add_ch"}],
        [{"text": "➖ حذف قناة", "callback_data": "rem_ch"}],
        [{"text": "📨 إعلان", "callback_data": "broad"}],
        [{"text": "🚫 حظر مستخدم", "callback_data": "block_user"}],
        [{"text": "✅ إلغاء حظر", "callback_data": "unblock_user"}],
        [{"text": "📋 قائمة المستخدمين", "callback_data": "list_users"}],
        [{"text": "❌ إغلاق", "callback_data": "close"}]
    ]
    send_message(chat_id, "🔧 **لوحة تحكم الأدمن**\nاختر أحد الخيارات:", keyboard)

def show_stats(chat_id, message_id, user_id):
    if not is_admin(user_id):
        return
    text = f"""📊 **إحصائيات البوت**

👥 المستخدمين: {get_user_count()}
🚫 المحظورين: {len(blocked)}
👑 الأدمن: {len(ADMINS)}
📢 قنوات الاشتراك: {len(REQUIRED_CHANNELS)}

✅ الحالة: شغال
🕐 الوقت: {datetime.now().strftime('%Y-%m-%d %H:%M')}"""
    edit_message(chat_id, message_id, text)

def show_channels(chat_id, message_id, user_id):
    if not is_admin(user_id):
        return
    text = "📢 **قنوات الاشتراك:**\n\n"
    for i, ch in enumerate(REQUIRED_CHANNELS, 1):
        text += f"{i}. {ch}\n"
    edit_message(chat_id, message_id, text)

waiting_for = set()

def add_channel_mode(chat_id, message_id, user_id):
    if not is_admin(user_id):
        return
    edit_message(chat_id, message_id, "➕ أرسل اسم القناة (مثال: @newchannel)")
    waiting_for.add(f"addchannel_{chat_id}")

def rem_channel_mode(chat_id, message_id, user_id):
    if not is_admin(user_id):
        return
    edit_message(chat_id, message_id, "➖ أرسل اسم القناة للحذف (مثال: @oldchannel)")
    waiting_for.add(f"remchannel_{chat_id}")

def broadcast_mode(chat_id, message_id, user_id):
    if not is_admin(user_id):
        return
    edit_message(chat_id, message_id, "📨 أرسل الرسالة التي تريد إرسالها للجميع:")
    waiting_for.add(f"broadcast_{chat_id}")

def block_user_mode(chat_id, message_id, user_id):
    if not is_admin(user_id):
        return
    edit_message(chat_id, message_id, "🚫 أرسل معرف المستخدم (ID):")
    waiting_for.add(f"block_{chat_id}")

def unblock_user_mode(chat_id, message_id, user_id):
    if not is_admin(user_id):
        return
    edit_message(chat_id, message_id, "✅ أرسل معرف المستخدم (ID):")
    waiting_for.add(f"unblock_{chat_id}")

def list_users(chat_id, message_id, user_id):
    if not is_admin(user_id):
        return
    if not users:
        edit_message(chat_id, message_id, "📋 لا يوجد مستخدمين بعد.")
        return
    text = "📋 **قائمة المستخدمين:**\n\n"
    for i, uid in enumerate(users, 1):
        text += f"{i}. `{uid}`\n"
    edit_message(chat_id, message_id, text)

@app.route('/webhook', methods=['POST'])
def webhook():
    update = request.get_json()
    if not update:
        return "OK", 200
    
    if "message" in update:
        msg = update["message"]
        chat_id = msg["chat"]["id"]
        user_id = msg["from"]["id"]
        text = msg.get("text", "")
        
        if text == "/start":
            handle_start(chat_id, user_id)
        elif text == "/admin":
            admin_panel(chat_id, user_id)
        
        for task in list(waiting_for):
            if task == f"addchannel_{chat_id}":
                waiting_for.remove(task)
                if text.startswith("@"):
                    REQUIRED_CHANNELS.append(text)
                    send_message(chat_id, f"✅ تم إضافة {text}")
                else:
                    send_message(chat_id, "⚠️ يجب أن يبدأ اسم القناة بـ @")
            elif task == f"remchannel_{chat_id}":
                waiting_for.remove(task)
                if text in REQUIRED_CHANNELS:
                    REQUIRED_CHANNELS.remove(text)
                    send_message(chat_id, f"✅ تم حذف {text}")
                else:
                    send_message(chat_id, "❌ القناة غير موجودة")
            elif task == f"broadcast_{chat_id}":
                waiting_for.remove(task)
                success = 0
                for uid in users:
                    try:
                        send_message(uid, f"📢 **إعلان من الأدمن**\n\n{text}")
                        success += 1
                    except:
                        pass
                send_message(chat_id, f"✅ تم الإرسال إلى {success} مستخدم")
            elif task == f"block_{chat_id}":
                waiting_for.remove(task)
                try:
                    target = int(text)
                    if target in ADMINS:
                        send_message(chat_id, "⛔ لا يمكن حظر أدمن")
                    elif target in blocked:
                        send_message(chat_id, "ℹ️ المستخدم محظور بالفعل")
                    else:
                        blocked.append(target)
                        send_message(chat_id, f"✅ تم حظر {target}")
                except:
                    send_message(chat_id, "⚠️ معرف غير صالح")
            elif task == f"unblock_{chat_id}":
                waiting_for.remove(task)
                try:
                    target = int(text)
                    if target in blocked:
                        blocked.remove(target)
                        send_message(chat_id, f"✅ تم إلغاء حظر {target}")
                    else:
                        send_message(chat_id, "ℹ️ المستخدم غير محظور")
                except:
                    send_message(chat_id, "⚠️ معرف غير صالح")
    
    elif "callback_query" in update:
        cb = update["callback_query"]
        chat_id = cb["message"]["chat"]["id"]
        message_id = cb["message"]["message_id"]
        user_id = cb["from"]["id"]
        
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/answerCallbackQuery",
                      data={"callback_query_id": cb["id"]})
        
        data = cb["data"]
        if data == "check":
            handle_check(chat_id, message_id, user_id)
        elif data == "stats":
            show_stats(chat_id, message_id, user_id)
        elif data == "channels":
            show_channels(chat_id, message_id, user_id)
        elif data == "add_ch":
            add_channel_mode(chat_id, message_id, user_id)
        elif data == "rem_ch":
            rem_channel_mode(chat_id, message_id, user_id)
        elif data == "broad":
            broadcast_mode(chat_id, message_id, user_id)
        elif data == "block_user":
            block_user_mode(chat_id, message_id, user_id)
        elif data == "unblock_user":
            unblock_user_mode(chat_id, message_id, user_id)
        elif data == "list_users":
            list_users(chat_id, message_id, user_id)
        elif data == "close":
            edit_message(chat_id, message_id, "🔒 تم إغلاق اللوحة")
    
    return "OK", 200

@app.route('/')
def home():
    return "شغال!"

application = app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
