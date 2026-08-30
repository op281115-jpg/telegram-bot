import os
import threading
import sqlite3
import telebot
from flask import Flask, render_template_string, request, jsonify

TOKEN = "8658262212:AAF3NjvQVA-stiFrKw9ZzLAx260cnUVPU"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

PORT = int(os.environ.get("PORT", 5000))

# Database Initialization
def init_db():
    conn = sqlite3.connect("bot_users.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            name TEXT,
            balance INTEGER
        )
    """)
    conn.commit()
    conn.close()

init_db()

# Web App HTML Page (M9 Style UI ပုံစံငယ်)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="my">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sham Game Mini App</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        body { background-color: #1a1a2e; color: white; font-family: sans-serif; text-align: center; margin: 0; padding: 20px; }
        .table { background: #0f3460; border-radius: 20px; padding: 20px; margin-top: 20px; box-shadow: 0 0 20px rgba(0,0,0,0.5); }
        .balance { font-size: 20px; color: #ffd700; margin-bottom: 15px; }
        .btn { background: #e94560; color: white; border: none; padding: 12px 25px; font-size: 16px; border-radius: 8px; cursor: pointer; margin-top: 15px; }
    </style>
</head>
<body>
    <h2>ရှမ်းကိုးမား (M9 Style)</h2>
    <div class="balance">လက်ကျန်ငွေ: <span id="userBalance">1000</span> Kyats</div>
    <div class="table">
        <p>ဖဲချပ်ဝိုင်း</p>
        <button class="btn" onclick="dealCards()">ဖဲထိုးမည်</button>
    </div>
    <script>
        let tg = window.Telegram.WebApp;
        tg.expand(); // Screen အပြည့်ချဲ့ရန်
        
        function dealCards() {
            alert("ဖဲဝေနေပါပြီ...");
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

# Telegram Bot Commands
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = telebot.types.InlineKeyboardMarkup()
    web_app_url = "https://sham-game.onrender.com" 
    markup.add(telebot.types.InlineKeyboardButton("🎮 ဂိမ်းစရန် (M9 App)", web_app=telebot.types.WebAppInfo(url=web_app_url)))
    bot.send_message(message.chat.id, "ကြိုဆိုပါတယ်! အောက်ပါခလုတ်ကိုနှိပ်၍ ဂိမ်းကို ဖွင့်ပါ။", reply_markup=markup)

# Run Telegram Bot in Background Thread
def run_bot():
    bot.infinity_polling()

if __name__ == '__main__':
    t = threading.Thread(target=run_bot)
    t.daemon = True
    t.start()
    app.run(host='0.0.0.0', port=PORT)
