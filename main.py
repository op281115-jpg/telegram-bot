import telebot
from flask import Flask, render_template_string, request
import random

TOKEN = '8658262212:AAGtRZaF0dE4lKyvsIv-eBdSgUgb6xs2xqc'
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Telegram Webhook အလိုအလျောက် ချိတ်ဆက်ရန်
WEBHOOK_URL = "https://telegram-bot-sbc4.onrender.com/webhook"
bot.remove_webhook()
bot.set_webhook(url=WEBHOOK_URL)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="my">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>M9 ရှမ်းကိုးမီး & ငါးပစ်ဂိမ်း</title>
    <style>
        body { font-family: sans-serif; background-color: #1a1a1a; color: white; text-align: center; margin: 0; padding: 20px; }
        .container { max-width: 400px; margin: auto; background: #2a2a2a; padding: 20px; border-radius: 10px; }
        button { background: #ff4757; color: white; border: none; padding: 10px 20px; font-size: 16px; border-radius: 5px; cursor: pointer; margin-top: 10px; }
        button:hover { background: #ff6b81; }
    </style>
</head>
<body>
    <div class="container">
        <h2>🃏 ရှမ်းကိုးမီး & ငါးပစ်ဂိမ်း</h2>
        <p>လက်ကျန်ငွေ: <span id="userBalance">10000</span> ကျပ်</p>
        <p>စားပွဲငွေ: <span id="tableBalance">0</span> ကျပ်</p>
        <p>အိုးစုငွေ: <span id="potAmount">0</span> ကျပ်</p>
        <button onclick="placeBet(1000)">၁၀၀၀ ကျပ် လောင်းမည်</button>
    </div>
    <script>
        let balance = 10000;
        let pot = 0;
        function placeBet(amount) {
            if (balance >= amount) {
                balance -= amount;
                pot += amount;
                document.getElementById('userBalance').innerText = balance;
                document.getElementById('tableBalance').innerText = balance;
                document.getElementById('potAmount').innerText = pot.toLocaleString();
                alert(amount + " ကျပ် လောင်းလိုက်ပါပြီ!");
            } else {
                alert("လက်ကျန်ငွေ မလုံလောက်ပါ!!");
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/webhook', methods=['POST'])
def webhook():
    json_str = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = telebot.types.InlineKeyboardMarkup()
    web_app = telebot.types.WebAppInfo(url="https://telegram-bot-sbc4.onrender.com")
    markup.add(telebot.types.InlineKeyboardButton("🃏 ရှမ်းကိုးမီး & ငါးပစ်ဂိမ်း", web_app=web_app))
    bot.reply_to(message, "မင်္ဂလာပါ! M9 ရှမ်းကိုးမီး ဂိမ်းကို စတင်ဆော့ကစားနိုင်ပါပြီ။", reply_markup=markup)

def create_deck():
    suits = ['♠', '♥', '♦', '♣']
    values = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
    deck = [{'suit': suit, 'val': val} for suit in suits for val in values]
    random.shuffle(deck)
    return deck

def get_card_value(card):
    if card['val'] in ['10', 'J', 'Q', 'K']:
        return 0
    if card['val'] == 'A':
        return 1
    return int(card['val'])

def calculate_score(cards):
    total = sum(get_card_value(card) for card in cards)
    score = total % 10
    is_shan = len(cards) == 3 and score in [8, 9]
    return score, is_shan

@app.route('/api/shankoemee/play', methods=['POST'])
def play_shankoemee():
    return {"status": "success", "message": "Game logic active"}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
    
