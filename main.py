import os
import telebot
from flask import Flask, render_template_string, request, jsonify

TOKEN = '8658262212:AAE3xQ5O5BqNaq-JScpAPsXwdrNqkJ03w1w'
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Full M9 Style UI (Lobby, Rooms & Game Table)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="my">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>M9 ရှမ်းကိုးမား</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: sans-serif; }
        body { background-color: #0b0f19; color: #fff; overflow-x: hidden; }
        .screen { display: none; width: 100vw; height: 100vh; position: relative; background: radial-gradient(circle, #1a233a 0%, #07090e 100%); }
        .active { display: flex; flex-direction: column; justify-content: space-between; }
        
        /* Lobby Style */
        .lobby-header { display: flex; justify-content: space-between; align-items: center; padding: 15px; background: rgba(0,0,0,0.5); }
        .user-info { display: flex; align-items: center; gap: 10px; }
        .avatar { width: 45px; height: 45px; border-radius: 50%; border: 2px solid gold; background: #333; }
        .balance-box { background: rgba(255,215,0,0.1); border: 1px solid gold; padding: 5px 12px; border-radius: 20px; color: gold; font-weight: bold; }
        .lobby-body { display: flex; flex-direction: column; align-items: center; justify-content: center; flex: 1; gap: 20px; }
        .menu-btn { width: 80%; max-width: 300px; padding: 15px; background: linear-gradient(135deg, #f39c12, #d35400); border: none; border-radius: 25px; color: white; font-size: 18px; font-weight: bold; cursor: pointer; text-align: center; box-shadow: 0 4px 15px rgba(243,156,18,0.4); }

        /* Room Selection Style */
        .room-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; padding: 20px; width: 100%; max-width: 500px; margin: auto; }
        .room-card { background: linear-gradient(135deg, #16a085, #2980b9); border-radius: 12px; padding: 15px; text-align: center; cursor: pointer; border: 1px solid #48dbfb; box-shadow: 0 4px 10px rgba(0,0,0,0.3); }
        .room-card h3 { font-size: 18px; margin-bottom: 5px; color: #f1c40f; }
        .room-card p { font-size: 13px; color: #dfe6e9; }

        /* Game Table Style */
        .table-container { width: 100%; height: 100%; background: radial-gradient(circle, #27ae60 0%, #145a32 100%); position: relative; display: flex; flex-direction: column; justify-content: space-between; padding: 10px; }
        .table-top { display: flex; justify-content: space-between; align-items: center; }
        .pot-box { background: rgba(0,0,0,0.4); padding: 5px 15px; border-radius: 10px; border: 1px solid gold; color: gold; font-weight: bold; text-align: center; }
        
        .card-table-felt { flex: 1; position: relative; border: 5px solid #d4ac0d; border-radius: 100px; margin: 10px; display: flex; justify-content: center; align-items: center; }
        
        .controls-panel { display: flex; justify-content: space-around; padding: 10px; background: rgba(0,0,0,0.6); border-radius: 15px; }
        .bet-btn { background: #8e44ad; border: 2px solid #f39c12; color: white; padding: 10px 15px; border-radius: 10px; font-weight: bold; cursor: pointer; }
        .max-btn { background: #c0392b; border: 2px solid white; color: white; padding: 10px 20px; border-radius: 10px; font-weight: bold; cursor: pointer; }
        .back-btn { background: #333; color: white; border: 1px solid #777; padding: 8px 15px; border-radius: 8px; cursor: pointer; }
    </style>
</head>
<body>

    <!-- 1. LOBBY SCREEN -->
    <div id="lobbyScreen" class="screen active">
        <div class="lobby-header">
            <div class="user-info">
                <div class="avatar"></div>
                <span>ID: 36880561</span>
            </div>
            <div class="balance-box">🪙 <span id="userBalance">1000</span> Kyats</div>
        </div>
        <div class="lobby-body">
            <button class="menu-btn" onclick="showRooms()">🎮 ဖဲချပ်ဝိုင်း (Play)</button>
            <button class="menu-btn" style="background: linear-gradient(135deg, #8e44ad, #3498db);" onclick="alert('ကြော်ငြာနှင့်လက်ဆောင်များ')">🎁 လက်ဆောင်များ</button>
            <button class="menu-btn" style="background: linear-gradient(135deg, #27ae60, #2980b9);" onclick="alert('Rank စာရင်း')">🏆 Ranking</button>
        </div>
    </div>

    <!-- 2. ROOM SELECTION SCREEN -->
    <div id="roomScreen" class="screen">
        <div class="lobby-header">
            <button class="back-btn" onclick="showLobby()">⬅ နောက်သို့</button>
            <h2>အခန်းရွေးချယ်ရန်</h2>
            <div class="balance-box">🪙 1000</div>
        </div>
        <div class="room-grid">
            <div class="room-card" onclick="joinTable('လွယ်လွယ်', 100)">
                <h3>လွယ်လွယ်</h3>
                <p>ဝင်ကြေး: 100 - 100,000</p>
            </div>
            <div class="room-card" onclick="joinTable('အလယ်အလတ်', 1000)">
                <h3>အလယ်အလတ်</h3>
                <p>ဝင်ကြေး: 1,000 - more</p>
            </div>
            <div class="room-card" onclick="joinTable('ခက်ခဲဖျာ', 3000)">
                <h3>ခက်ခဲဖျာ</h3>
                <p>ဝင်ကြေး: 3,000 - 300,000</p>
            </div>
            <div class="room-card" onclick="joinTable('စူပါခက်', 5000)">
                <h3>စူပါခက်</h3>
                <p>ဝင်ကြေး: 5,000 - 500,000</p>
            </div>
        </div>
    </div>

    <!-- 3. GAME TABLE SCREEN -->
    <div id="gameScreen" class="screen">
        <div class="table-container">
            <div class="table-top">
                <button class="back-btn" onclick="showRooms()">⬅ ထွက်မည်</button>
                <div class="pot-box">Pot: <span id="potAmount">1,000</span> Kyats</div>
                <div class="balance-box">🪙 <span id="tableBalance">1000</span></div>
            </div>
            
            <div class="card-table-felt">
                <p style="color: rgba(255,255,255,0.6); font-weight: bold;" id="roomTitleDisplay">စားပွဲခုံ</p>
            </div>

            <div class="controls-panel">
                <button class="bet-btn" onclick="placeBet(200)">200</button>
                <button class="bet-btn" onclick="placeBet(500)">500</button>
                <button class="bet-btn" onclick="placeBet(700)">700</button>
                <button class="max-btn" onclick="placeBet(1000)">Max: 1K</button>
            </div>
        </div>
    </div>

    <script>
        let balance = 1000;
        let pot = 1000;

        function showRooms() {
            document.getElementById('lobbyScreen').classList.remove('active');
            document.getElementById('gameScreen').classList.remove('active');
            document.getElementById('roomScreen').classList.add('active');
        }

        function showLobby() {
            document.getElementById('roomScreen').classList.remove('active');
            document.getElementById('gameScreen').classList.remove('active');
            document.getElementById('lobbyScreen').classList.add('active');
        }

        let currentRoomStake = 100;
        function joinTable(roomName, stake) {
            currentRoomStake = stake;
            document.getElementById('roomScreen').classList.remove('active');
            document.getElementById('gameScreen').classList.add('active');
            document.getElementById('roomTitleDisplay').innerText = roomName + " (ဝင်ကြေး: " + stake + ")";
        }

        function placeBet(amount) {
            if(balance >= amount) {
                balance -= amount;
                pot += amount;
                document.getElementById('userBalance').innerText = balance;
                document.getElementById('tableBalance').innerText = balance;
                document.getElementById('potAmount').innerText = pot.toLocaleString();
                alert(amount + " ကျပ် လောင်းလိုက်ပါပြီ!");
            } else {
                alert("လက်ကျန်ငွေ မလုံလောက်ပါ။");
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
    web_app = telebot.types.WebAppInfo(url="https://sham-game.onrender.com")
    markup.add(telebot.types.InlineKeyboardButton("🃏 ရှမ်းကိုးမား ကစားရန်", web_app=web_app))
    bot.reply_to(message, "မင်္ဂလာပါ! M9 ရှမ်းကိုးမား ဂိမ်းကို စတင်ဆော့ကစားရန် အောက်ပါခလုတ်ကို နှိပ်ပါ။", reply_markup=markup)
import random

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
def play_shan_koe_mee():
    deck = create_deck()
    player_hand = [deck.pop(), deck.pop(), deck.pop()]
    banker_hand = [deck.pop(), deck.pop(), deck.pop()]
    
    p_score, p_shan = calculate_score(player_hand)
    b_score, b_shan = calculate_score(banker_hand)
    
    if p_shan and not b_shan:
        winner = 'Player Wins (Shan!)'
    elif not p_shan and b_shan:
        winner = 'Banker Wins (Shan!)'
    elif p_score > b_score:
        winner = 'Player Wins'
    elif p_score < b_score:
        winner = 'Banker Wins'
    else:
        winner = 'Draw'
        
    return jsonify({
        'player': {'hand': player_hand, 'score': p_score, 'isShan': p_shan},
        'banker': {'hand': banker_hand, 'score': b_score, 'isShan': b_shan},
        'winner': winner
    })
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
    
