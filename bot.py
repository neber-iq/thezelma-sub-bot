import requests
import json
import os
from flask import Flask, request
from datetime import datetime
import pytz

app = Flask(__name__)

BOT_TOKEN = "8559348024:AAEjicYYRDPdSw58PrIC5MG_Qu49lYPOkbA"

ADMINS = [
    355449817,  # أنت
    133438395,  # صديقك
]

REQUIRED_CHANNELS = [
    "@thezelma1",
    "@thezelma3", 
    "@thezelma_tv",
    "@theze1ma"
]

PROTECTED_LINK = "https://t.me/theze1m"

users = []
blocked = []

WORLD_CUP_DATA_URL = "https://raw.githubusercontent.com/openfootball/worldcup.json/master/2026/worldcup.json"

# ================== دوال كأس العالم ==================
def fetch_worldcup_data():
    try:
        response = requests.get(WORLD_CUP_DATA_URL, timeout=15)
        if response.status_code == 200:
            data = response.json()
            if "matches" in data:
                return data["matches"]
            return []
        return []
    except:
        return []

def get_matches_today():
    today = datetime.now(pytz.timezone('Asia/Baghdad')).strftime("%Y-%m-%d")
    all_matches = fetch_worldcup_data()
    matches = []
    for match in all_matches:
        if match.get("date") == today:
            team1 = match.get("team1", "?")
            team2 = match.get("team2", "?")
            time = match.get("time", "?")
            ground = match.get("ground", "?")
            matches.append(f"⚽ {team1} 🆚 {team2}\n🕐 {time}\n🏟️ {ground}")
    return matches

def get_upcoming_matches(days=5):
    from datetime import timedelta
    today = datetime.now(pytz.timezone('Asia/Baghdad'))
    all_matches = fetch_worldcup_data()
    matches = []
    for match in all_matches:
        try:
            match_date = datetime.strptime(match.get("date", ""), "%Y-%m-%d")
            if today <= match_date <= today + timedelta(days=days):
                team1 = match.get("team1", "?")
                team2 = match.get("team2", "?")
                match_date_str = match.get("date", "?")
                time = match.get("time", "?")
                ground = match.get("ground", "?")
                matches.append(f"📅 {match_date_str}\n⚽ {team1} 🆚 {team2}\n🕐 {time}\n🏟️ {ground}")
        except:
            continue
    return matches

def get_all_matches():
    all_matches = fetch_worldcup_data()
    matches = []
    for match in all_matches:
        team1 = match.get("team1", "?")
        team2 = match.get("team2", "?")
        match_date = match.get("date", "?")
        time = match.get("time", "?")
        ground = match.get("ground", "?")
        matches.append(f"📅 {match_date}\n⚽ {team1} 🆚 {team2}\n🕐 {time}\n🏟️ {ground}")
    return matches

# ================== دوال البوت الأساسية ==================
def is_admin(user_id):
    return user_id in ADMINS

def is_blocked(user_id):
    return user_id in blocked

def add_user(user_id):
    if user_id not in users:
        users.append(user_id)

def get_user_count():
    return len(users)

def send_message(chat_id, text, keyboard=None, reply_keyboard=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if keyboard:
        data["reply_markup"] = json.dumps({"inline_keyboard": keyboard})
    if reply_keyboard:
        data["reply_markup"] = json.dumps({"keyboard": reply_keyboard, "resize_keyboard": True, "one_time_keyboard": False})
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

def send_main_keyboard(chat_id):
    """إرسال الكيبورد الرئيسي للجميع (كأس العالم + فتح الرابط)"""
    reply_keyboard = [
        ["🏆 كأس العالم", "🚀 فتح الرابط"]
    ]
    send_message(chat_id, "✅ مرحباً بك! اختر أحد الخيارات من القائمة أدناه:", reply_keyboard=reply_keyboard)

def handle_start(chat_id, user_id):
    add_user(user_id)
    if is_blocked(user_id):
        send_message(chat_id, "⛔ تم حظرك من هذا البوت.")
        return
    if check_subscription(user_id):
        send_main_keyboard(chat_id)
    else:
        keyboard = []
        for ch in REQUIRED_CHANNELS:
            ch_name = ch.replace("@", "")
            keyboard.append([{"text": f"📢 اشترك بـ {ch}", "url": f"https://t.me/{ch_name}"}])
        keyboard.append([{"text": "✅ تأكد", "callback_data": "check"}])
        send_message(chat_id, "⚠️ للوصول إلى المحتوى، اشترك بالقنوات ثم اضغط تأكد:", keyboard)

def handle_check(chat_id, message_id, user_id):
    if check_subscription(user_id):
        send_main_keyboard(chat_id)
        edit_message(chat_id, message_id, "✅ تم التأكيد!")
    else:
        edit_message(chat_id, message_id, "❌ لم تكتمل الاشتراكات. جرب مرة ثانية.")

# ================== قائمة كأس العالم (للكل) ==================
def worldcup_menu(chat_id, message_id, user_id):
    """قائمة كأس العالم - تظهر للجميع (أدمن وعادي)"""
    keyboard = [
        [{"text": "📅 مباريات اليوم", "callback_data": "wc_today"}],
        [{"text": "🗓️ المباريات القادمة", "callback_data": "wc_upcoming"}],
        [{"text": "🏟️ جميع المباريات", "callback_data": "wc_all"}],
        [{"text": "🔙 رجوع", "callback_data": "main_menu"}]
    ]
    edit_message(chat_id, message_id, "🏆 **كأس العالم 2026**\nاختر أحد الخيارات:", keyboard)

def show_today_matches(chat_id, message_id, user_id):
    matches = get_matches_today()
    if matches:
        text = "⚽ **مباريات اليوم:**\n\n" + "\n\n".join(matches)
    else:
        text = "ℹ️ لا توجد مباريات اليوم."
    keyboard = [[{"text": "🔙 رجوع", "callback_data": "worldcup_menu"}]]
    edit_message(chat_id, message_id, text, keyboard)

def show_upcoming_matches(chat_id, message_id, user_id):
    matches = get_upcoming_matches(5)
    if matches:
        text = "🗓️ **المباريات القادمة (خلال 5 أيام):**\n\n" + "\n\n".join(matches)
    else:
        text = "ℹ️ لا توجد مباريات قادمة في هذه الفترة."
    keyboard = [[{"text": "🔙 رجوع", "callback_data": "worldcup_menu"}]]
    edit_message(chat_id, message_id, text, keyboard)

def show_all_matches(chat_id, message_id, user_id):
    matches = get_all_matches()
    if matches:
        text = "🏟️ **جميع مباريات كأس العالم:**\n\n" + "\n\n".join(matches)
    else:
        text = "ℹ️ لا توجد مباريات مسجلة حالياً."
    keyboard = [[{"text": "🔙 رجوع", "callback_data": "worldcup_menu"}]]
    edit_message(chat_id, message_id, text, keyboard)

def main_menu(chat_id, message_id, user_id):
    send_main_keyboard(chat_id)
    edit_message(chat_id, message_id, "✅ **القائمة الرئيسية**")

# ================== لوحة تحكم الأدمن (منفصلة) ==================
def admin_panel(chat_id, user_id):
    """هذي تظهر بس للأدمن اللي يكتب /admin"""
    if not is_admin(user_id):
        send_message(chat_id, "⛔ هذا الأمر مخصص للأدمن فقط.")
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
🕐 الوقت: {datetime.now(pytz.timezone('Asia/Baghdad')).strftime('%Y-%m-%d %H:%M')}"""
    edit_message(chat_id, message_id, text)

def show_channels(chat_id, message_id, user_id):
    if not is_admin(user_id):
        return
    if not REQUIRED_CHANNELS:
        text = "📢 لا توجد قنوات اشتراك حالياً."
    else:
        text = "📢 **قنوات الاشتراك الحالية:**\n\n"
        for i, ch in enumerate(REQUIRED_CHANNELS, 1):
            text += f"{i}. {ch}\n"
    edit_message(chat_id, message_id, text)

waiting_for = set()

def add_channel_mode(chat_id, message_id, user_id):
    if not is_admin(user_id):
        return
    edit_message(chat_id, message_id, "➕ **إضافة قناة جديدة**\n\nأرسل اسم القناة (مثال: @newchannel)\nأو اضغط /cancel للإلغاء")
    waiting_for.add(f"addchannel_{chat_id}")

def rem_channel_mode(chat_id, message_id, user_id):
    if not is_admin(user_id):
        return
    if not REQUIRED_CHANNELS:
        edit_message(chat_id, message_id, "❌ لا توجد قنوات لحذفها.")
        return
    keyboard = [[{"text": f"❌ {ch}", "callback_data": f"delch_{ch}"}] for ch in REQUIRED_CHANNELS]
    keyboard.append([{"text": "🔙 رجوع", "callback_data": "admin_back"}])
    edit_message(chat_id, message_id, "➖ **اختر القناة للحذف:**", keyboard)

def broadcast_mode(chat_id, message_id, user_id):
    if not is_admin(user_id):
        return
    edit_message(chat_id, message_id, "📨 **إرسال إعلان**\n\nأرسل الرسالة التي تريد إرسالها للجميع:")
    waiting_for.add(f"broadcast_{chat_id}")

def block_user_mode(chat_id, message_id, user_id):
    if not is_admin(user_id):
        return
    edit_message(chat_id, message_id, "🚫 **حظر مستخدم**\n\nأرسل معرف المستخدم (ID):")
    waiting_for.add(f"block_{chat_id}")

def unblock_user_mode(chat_id, message_id, user_id):
    if not is_admin(user_id):
        return
    edit_message(chat_id, message_id, "✅ **إلغاء حظر**\n\nأرسل معرف المستخدم (ID):")
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

def cancel_action(chat_id, user_id):
    for task in list(waiting_for):
        if task.endswith(f"_{chat_id}"):
            waiting_for.remove(task)
            send_message(chat_id, "✅ تم إلغاء العملية.")
            return
    send_message(chat_id, "ℹ️ لا توجد عملية نشطة للإلغاء.")

def add_channel(channel_name):
    if not channel_name.startswith("@"):
        channel_name = "@" + channel_name
    if channel_name not in REQUIRED_CHANNELS:
        REQUIRED_CHANNELS.append(channel_name)
        return True, channel_name
    return False, channel_name

def remove_channel(channel_name):
    if channel_name in REQUIRED_CHANNELS:
        REQUIRED_CHANNELS.remove(channel_name)
        return True, channel_name
    return False, channel_name

def handle_text_message(chat_id, user_id, text):
    """معالجة الأزرار من الكيبورد (الكل يقدر يضغط عليها)"""
    if text == "🏆 كأس العالم":
        # تظهر قائمة كأس العالم للجميع
        keyboard = [
            [{"text": "📅 مباريات اليوم", "callback_data": "wc_today"}],
            [{"text": "🗓️ المباريات القادمة", "callback_data": "wc_upcoming"}],
            [{"text": "🏟️ جميع المباريات", "callback_data": "wc_all"}],
            [{"text": "🔙 رجوع", "callback_data": "main_menu"}]
        ]
        send_message(chat_id, "🏆 **كأس العالم 2026**\nاختر أحد الخيارات:", keyboard)
    elif text == "🚀 فتح الرابط":
        keyboard = [[{"text": "🚀 فتح الرابط", "url": PROTECTED_LINK}]]
        send_message(chat_id, "اضغط الزر أدناه لفتح الرابط المحمي:", keyboard)

# ================== Webhook ==================
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
            admin_panel(chat_id, user_id)  # فقط للأدمن
        elif text == "/cancel":
            cancel_action(chat_id, user_id)
        elif text in ["🏆 كأس العالم", "🚀 فتح الرابط"]:
            handle_text_message(chat_id, user_id, text)  # الكل يقدر يضغط
        
        # معالجة المدخلات للأدمن
        for task in list(waiting_for):
            if task == f"addchannel_{chat_id}":
                waiting_for.remove(task)
                success, channel = add_channel(text)
                if success:
                    send_message(chat_id, f"✅ تم إضافة {channel}")
                else:
                    send_message(chat_id, f"ℹ️ {channel} موجودة بالفعل")
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
        elif data == "worldcup_menu":
            worldcup_menu(chat_id, message_id, user_id)  # الكل
        elif data == "wc_today":
            show_today_matches(chat_id, message_id, user_id)  # الكل
        elif data == "wc_upcoming":
            show_upcoming_matches(chat_id, message_id, user_id)  # الكل
        elif data == "wc_all":
            show_all_matches(chat_id, message_id, user_id)  # الكل
        elif data == "main_menu":
            send_main_keyboard(chat_id)
            edit_message(chat_id, message_id, "✅ **القائمة الرئيسية**")
        
        # أوامر الأدمن (تتطلب صلاحية)
        elif data == "stats":
            if is_admin(user_id):
                show_stats(chat_id, message_id, user_id)
        elif data == "channels":
            if is_admin(user_id):
                show_channels(chat_id, message_id, user_id)
        elif data == "add_ch":
            if is_admin(user_id):
                add_channel_mode(chat_id, message_id, user_id)
        elif data == "rem_ch":
            if is_admin(user_id):
                rem_channel_mode(chat_id, message_id, user_id)
        elif data == "broad":
            if is_admin(user_id):
                broadcast_mode(chat_id, message_id, user_id)
        elif data == "block_user":
            if is_admin(user_id):
                block_user_mode(chat_id, message_id, user_id)
        elif data == "unblock_user":
            if is_admin(user_id):
                unblock_user_mode(chat_id, message_id, user_id)
        elif data == "list_users":
            if is_admin(user_id):
                list_users(chat_id, message_id, user_id)
        elif data == "admin_back":
            if is_admin(user_id):
                admin_panel(chat_id, user_id)
        elif data == "close":
            edit_message(chat_id, message_id, "🔒 تم إغلاق اللوحة")
        elif data.startswith("delch_"):
            if is_admin(user_id):
                channel = data.replace("delch_", "")
                success, channel = remove_channel(channel)
                if success:
                    send_message(chat_id, f"✅ تم حذف {channel}")
                else:
                    send_message(chat_id, f"❌ {channel} غير موجودة")
                show_channels(chat_id, message_id, user_id)
    
    return "OK", 200

@app.route('/')
def home():
    return "شغال!"

application = app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
