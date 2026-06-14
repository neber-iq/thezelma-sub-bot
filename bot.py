import requests
import json
import os
from flask import Flask, request
from datetime import datetime

app = Flask(__name__)

# ================== إعدادات البوت ==================
BOT_TOKEN = "8559348024:AAEjicYYRDPdSw58PrIC5MG_Qu49lYPOkbA"

# ================== قائمة الأدمن ==================
ADMINS = [
    355449817,  # أنت - @kingiraq
    133438395,  # صديقك
]

# قنوات الاشتراك الإجباري
REQUIRED_CHANNELS = [
    "@thezelma1",
    "@thezelma3", 
    "@thezelma_tv",
    "@theze1ma"
]

PROTECTED_LINK = "https://t.me/theze1m"

# ================== قاعدة بيانات مؤقتة ==================
# هذي راح تتنحذف إذا أعاد البوت التشغيل
# للمشاريع الكبيرة تحتاج قاعدة بيانات حقيقية
users_db = {}  # {user_id: {"joined_date": "2024-01-01", "username": "..."}}
blocked_users = []

# ================== دوال مساعدة ==================
def is_admin(user_id):
    return user_id in ADMINS

def is_blocked(user_id):
    return user_id in blocked_users

def save_user(user_id, username=None):
    """حفظ مستخدم جديد"""
    if user_id not in users_db:
        users_db[user_id] = {
            "joined_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "username": username
        }
        return True
    return False

def get_user_count():
    """عدد المستخدمين"""
    return len(users_db)

def check_subscription(user_id):
    """التحقق من اشتراك المستخدم في جميع القنوات"""
    if is_blocked(user_id):
        return False
    
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
    """إرسال رسالة للمستخدم"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if keyboard:
        data["reply_markup"] = json.dumps({"inline_keyboard": keyboard})
    try:
        requests.post(url, data=data, timeout=10)
    except:
        pass

def edit_message(chat_id, message_id, text, keyboard=None):
    """تعديل رسالة موجودة"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText"
    data = {"chat_id": chat_id, "message_id": message_id, "text": text}
    if keyboard:
        data["reply_markup"] = json.dumps({"inline_keyboard": keyboard})
    try:
        requests.post(url, json=data)
    except:
        pass

def broadcast_to_all(message_text):
    """إرسال رسالة لجميع المستخدمين"""
    success_count = 0
    fail_count = 0
    
    for user_id in users_db.keys():
        try:
            send_message(user_id, message_text)
            success_count += 1
        except:
            fail_count += 1
    
    return success_count, fail_count

def get_stats():
    """إحصائيات البوت"""
    stats = f"""📊 <b>إحصائيات البوت</b>

👥 <b>المستخدمين:</b> {get_user_count()}
🚫 <b>المحظورين:</b> {len(blocked_users)}
👑 <b>الأدمن:</b> {len(ADMINS)}
📢 <b>قنوات الاشتراك:</b> {len(REQUIRED_CHANNELS)}

✅ <b>الحالة:</b> شغال
🕐 <b>آخر تحديث:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    return stats

def get_channels_list():
    """قائمة القنوات"""
    channels = "<b>📢 قنوات الاشتراك الإجباري:</b>\n\n"
    for i, ch in enumerate(REQUIRED_CHANNELS, 1):
        channels += f"{i}. {ch}\n"
    return channels

# ================== معالجة الأوامر ==================
def handle_start(chat_id, user_id, username=None):
    """معالجة أمر /start"""
    save_user(user_id, username)
    
    if is_blocked(user_id):
        send_message(chat_id, "⛔ تم حظرك من استخدام هذا البوت. للاستفسار تواصل مع الأدمن.")
        return
    
    if check_subscription(user_id):
        keyboard = [[{"text": "🚀 فتح قناة التطبيقات", "url": PROTECTED_LINK}]]
        send_message(chat_id, "✅ أنت مشترك في جميع القنوات!\n\nاضغط الزر أدناه:", keyboard)
    else:
        keyboard = []
        for ch in REQUIRED_CHANNELS:
            ch_name = ch.replace("@", "")
            keyboard.append([{"text": f"📢 اشترك في {ch}", "url": f"https://t.me/{ch_name}"}])
        keyboard.append([{"text": "🔍 تأكد من الاشتراك", "callback_data": "check"}])
        send_message(chat_id, "⚠️ للوصول إلى المحتوى المحمي، يجب عليك الاشتراك في القنوات التالية:\n\nبعد الاشتراك، اضغط على زر التأكيد.", keyboard)

def handle_callback(chat_id, message_id, user_id):
    """معالجة الضغط على زر التأكيد"""
    if is_blocked(user_id):
        edit_message(chat_id, message_id, "⛔ حسابك محظور من استخدام البوت.")
        return
    
    if check_subscription(user_id):
        keyboard = [[{"text": "🚀 فتح", "url": PROTECTED_LINK}]]
        edit_message(chat_id, message_id, "🎉 تم التأكيد! أنت الآن مشترك.\n\nاضغط الزر أدناه:", keyboard)
    else:
        edit_message(chat_id, message_id, "❌ لم تكتمل الاشتراكات بعد.\n\nيرجى الاشتراك في جميع القنوات ثم الضغط على زر التأكيد مجدداً.")

# ================== أوامر الأدمن ==================
def handle_stats(chat_id, user_id):
    """إرسال الإحصائيات"""
    if not is_admin(user_id):
        send_message(chat_id, "⛔ هذا الأمر مخصص للأدمن فقط.")
        return
    stats = get_stats()
    send_message(chat_id, stats)

def handle_broadcast(chat_id, user_id, message):
    """إرسال رسالة لجميع المستخدمين"""
    if not is_admin(user_id):
        send_message(chat_id, "⛔ هذا الأمر مخصص للأدمن فقط.")
        return
    
    if not message:
        send_message(chat_id, "⚠️ يجب كتابة رسالة بعد الأمر.\nمثال: `/broadcast مرحبا جميعاً`")
        return
    
    send_message(chat_id, "⏳ جاري إرسال الرسالة إلى جميع المستخدمين...")
    success, fail = broadcast_to_all(message)
    send_message(chat_id, f"✅ تم الإرسال بنجاح إلى {success} مستخدم.\n❌ فشل الإرسال إلى {fail} مستخدم.")

def handle_block(chat_id, user_id, target_id):
    """حظر مستخدم"""
    if not is_admin(user_id):
        send_message(chat_id, "⛔ هذا الأمر مخصص للأدمن فقط.")
        return
    
    try:
        target_id = int(target_id)
    except:
        send_message(chat_id, "⚠️ يجب كتابة معرف المستخدم.\nمثال: `/block 123456789`")
        return
    
    if target_id in ADMINS:
        send_message(chat_id, "⛔ لا يمكن حظر أدمن.")
        return
    
    if target_id not in blocked_users:
        blocked_users.append(target_id)
        send_message(chat_id, f"✅ تم حظر المستخدم `{target_id}`.")
    else:
        send_message(chat_id, f"ℹ️ المستخدم `{target_id}` محظور بالفعل.")

def handle_unblock(chat_id, user_id, target_id):
    """إلغاء حظر مستخدم"""
    if not is_admin(user_id):
        send_message(chat_id, "⛔ هذا الأمر مخصص للأدمن فقط.")
        return
    
    try:
        target_id = int(target_id)
    except:
        send_message(chat_id, "⚠️ يجب كتابة معرف المستخدم.\nمثال: `/unblock 123456789`")
        return
    
    if target_id in blocked_users:
        blocked_users.remove(target_id)
        send_message(chat_id, f"✅ تم إلغاء حظر المستخدم `{target_id}`.")
    else:
        send_message(chat_id, f"ℹ️ المستخدم `{target_id}` غير محظور.")

def handle_channels(chat_id, user_id):
    """عرض قنوات الاشتراك"""
    if not is_admin(user_id):
        send_message(chat_id, "⛔ هذا الأمر مخصص للأدمن فقط.")
        return
    channels = get_channels_list()
    send_message(chat_id, channels)

def handle_addchannel(chat_id, user_id, channel):
    """إضافة قناة جديدة"""
    if not is_admin(user_id):
        send_message(chat_id, "⛔ هذا الأمر مخصص للأدمن فقط.")
        return
    
    if not channel:
        send_message(chat_id, "⚠️ يجب كتابة اسم القناة.\nمثال: `/addchannel @newchannel`")
        return
    
    if not channel.startswith("@"):
        channel = "@" + channel
    
    if channel in REQUIRED_CHANNELS:
        send_message(chat_id, f"ℹ️ القناة {channel} موجودة بالفعل.")
    else:
        REQUIRED_CHANNELS.append(channel)
        send_message(chat_id, f"✅ تم إضافة القناة {channel}.")

def handle_removechannel(chat_id, user_id, channel):
    """حذف قناة"""
    if not is_admin(user_id):
        send_message(chat_id, "⛔ هذا الأمر مخصص للأدمن فقط.")
        return
    
    if not channel:
        send_message(chat_id, "⚠️ يجب كتابة اسم القناة.\nمثال: `/removechannel @channel`")
        return
    
    if not channel.startswith("@"):
        channel = "@" + channel
    
    if channel in REQUIRED_CHANNELS:
        REQUIRED_CHANNELS.remove(channel)
        send_message(chat_id, f"✅ تم حذف القناة {channel}.")
    else:
        send_message(chat_id, f"ℹ️ القناة {channel} غير موجودة.")

# ================== Webhook ==================
@app.route('/webhook', methods=['POST'])
def webhook():
    update = request.get_json()
    if not update:
        return "OK", 200
    
    # معالجة الرسائل
    if "message" in update:
        msg = update["message"]
        chat_id = msg["chat"]["id"]
        user_id = msg["from"]["id"]
        username = msg["from"].get("username", "لا يوجد")
        
        if "text" in msg:
            text = msg["text"]
            
            if text == "/start":
                handle_start(chat_id, user_id, username)
            
            elif text == "/admin":
                if is_admin(user_id):
                    keyboard = [
                        [{"text": "📊 إحصائيات", "callback_data": "stats"}],
                        [{"text": "📢 قنوات الاشتراك", "callback_data": "channels"}],
                        [{"text": "❌ إغلاق", "callback_data": "close"}]
                    ]
                    send_message(chat_id, "✨ <b>لوحة تحكم الأدمن</b>\nاختر أحد الخيارات:", keyboard)
                else:
                    send_message(chat_id, "⛔ هذا الأمر مخصص للأدمن فقط.")
            
            # أوامر الأدمن النصية
            elif text.startswith("/stats"):
                handle_stats(chat_id, user_id)
            
            elif text.startswith("/broadcast"):
                msg_parts = text.split(" ", 1)
                broadcast_msg = msg_parts[1] if len(msg_parts) > 1 else ""
                handle_broadcast(chat_id, user_id, broadcast_msg)
            
            elif text.startswith("/block"):
                msg_parts = text.split(" ")
                target = msg_parts[1] if len(msg_parts) > 1 else ""
                handle_block(chat_id, user_id, target)
            
            elif text.startswith("/unblock"):
                msg_parts = text.split(" ")
                target = msg_parts[1] if len(msg_parts) > 1 else ""
                handle_unblock(chat_id, user_id, target)
            
            elif text == "/channels":
                handle_channels(chat_id, user_id)
            
            elif text.startswith("/addchannel"):
                msg_parts = text.split(" ", 1)
                channel = msg_parts[1] if len(msg_parts) > 1 else ""
                handle_addchannel(chat_id, user_id, channel)
            
            elif text.startswith("/removechannel"):
                msg_parts = text.split(" ", 1)
                channel = msg_parts[1] if len(msg_parts) > 1 else ""
                handle_removechannel(chat_id, user_id, channel)
    
    # معالجة الأزرار
    elif "callback_query" in update:
        cb = update["callback_query"]
        chat_id = cb["message"]["chat"]["id"]
        message_id = cb["message"]["message_id"]
        user_id = cb["from"]["id"]
        
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/answerCallbackQuery",
                      data={"callback_query_id": cb["id"]})
        
        if cb["data"] == "check":
            handle_callback(chat_id, message_id, user_id)
        
        elif cb["data"] == "stats":
            if is_admin(user_id):
                stats = get_stats()
                edit_message(chat_id, message_id, stats)
            else:
                edit_message(chat_id, message_id, "⛔ غير مصرح")
        
        elif cb["data"] == "channels":
            if is_admin(user_id):
                channels = get_channels_list()
                edit_message(chat_id, message_id, channels)
            else:
                edit_message(chat_id, message_id, "⛔ غير مصرح")
        
        elif cb["data"] == "close":
            edit_message(chat_id, message_id, "🔒 تم إغلاق لوحة التحكم.")
    
    return "OK", 200

@app.route('/')
def home():
    return "البوت شغال يباشا! 🚀"

application = app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
