import requests
import json
import time
import os

# ================== إعدادات البوت ==================
# التوكن الجديد - احفظه في متغير بيئة للأمان
BOT_TOKEN = "8559348024:AAEfxx8RDsz6XH8H0lTV5zqV9mdXZ4PQVuA"

# قنوات الاشتراك الإجباري
REQUIRED_CHANNELS = [
    "@thezelma1",
    "@thezelma3", 
    "@thezelma_tv",
    "@theze1ma"
]

# الرابط المحمي (قناتك الخاصة)
PROTECTED_LINK = "https://t.me/theze1m"

# ================== دوال مساعدة ==================
def check_subscription(user_id):
    """التحقق من اشتراك المستخدم في جميع القنوات"""
    for channel in REQUIRED_CHANNELS:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/getChatMember"
        params = {"chat_id": channel, "user_id": user_id}
        try:
            r = requests.get(url, params=params, timeout=10)
            data = r.json()
            if not data.get("ok"):
                print(f"خطأ في التحقق من {channel}: {data}")
                return False
            status = data["result"]["status"]
            if status in ["left", "kicked"]:
                return False
        except Exception as e:
            print(f"استثناء في {channel}: {e}")
            return False
    return True

def send_message(chat_id, text, keyboard=None):
    """إرسال رسالة للمستخدم"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    if keyboard:
        data["reply_markup"] = json.dumps({"inline_keyboard": keyboard})
    try:
        requests.post(url, data=data, timeout=10)
    except Exception as e:
        print(f"خطأ في الإرسال: {e}")

# ================== معالجة الأوامر ==================
def handle_start(chat_id, user_id):
    """معالجة أمر /start"""
    if check_subscription(user_id):
        # مشترك ✅
        keyboard = [[{"text": "🚀 فتح قناة التطبيقات", "url": PROTECTED_LINK}]]
        send_message(chat_id, "✅ أنت مشترك في جميع القنوات المطلوبة!\n\nاضغط الزر أدناه للوصول إلى المحتوى:", keyboard)
    else:
        # غير مشترك ❌
        keyboard = []
        for ch in REQUIRED_CHANNELS:
            ch_name = ch.replace("@", "")
            keyboard.append([{"text": f"📢 اشترك في {ch}", "url": f"https://t.me/{ch_name}"}])
        keyboard.append([{"text": "🔍 تأكد من الاشتراك", "callback_data": "check"}])
        send_message(chat_id, "⚠️ للوصول إلى المحتوى المحمي، يجب عليك الاشتراك في القنوات التالية:\n\nبعد الاشتراك، اضغط على زر التأكيد.", keyboard)

def handle_callback(chat_id, message_id, user_id):
    """معالجة الضغط على زر التأكيد"""
    if check_subscription(user_id):
        keyboard = [[{"text": "🚀 فتح قناة التطبيقات", "url": PROTECTED_LINK}]]
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText"
        data = {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": "🎉 تم التأكيد! أنت الآن مشترك في جميع القنوات.\n\nاضغط الزر أدناه:",
            "reply_markup": json.dumps({"inline_keyboard": keyboard})
        }
        requests.post(url, json=data)
    else:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText"
        data = {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": "❌ لم تكتمل الاشتراكات بعد.\n\nيرجى الاشتراك في جميع القنوات ثم الضغط على زر التأكيد مجدداً."
        }
        requests.post(url, json=data)

# ================== التشغيل الرئيسي ==================
def main():
    print("🚀 جاري تشغيل البوت...")
    print("✅ البوت شغال يا جمهورية الزلم!")
    print("اضغط Ctrl + C لإيقاف البوت\n")
    
    last_update = 0
    
    while True:
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?offset={last_update+1}&timeout=30"
            response = requests.get(url, timeout=35)
            updates = response.json()
            
            if not updates.get("ok"):
                print(f"خطأ في الاتصال: {updates}")
                time.sleep(5)
                continue
            
            for update in updates.get("result", []):
                last_update = update["update_id"]
                
                # معالجة الرسائل
                if "message" in update:
                    msg = update["message"]
                    chat_id = msg["chat"]["id"]
                    user_id = msg["from"]["id"]
                    
                    if "text" in msg and msg["text"] == "/start":
                        handle_start(chat_id, user_id)
                
                # معالجة الأزرار
                elif "callback_query" in update:
                    cb = update["callback_query"]
                    chat_id = cb["message"]["chat"]["id"]
                    message_id = cb["message"]["message_id"]
                    user_id = cb["from"]["id"]
                    
                    # الرد على الضغطة
                    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/answerCallbackQuery", 
                                 data={"callback_query_id": cb["id"]})
                    
                    if cb["data"] == "check":
                        handle_callback(chat_id, message_id, user_id)
                        
        except Exception as e:
            print(f"خطأ رئيسي: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()