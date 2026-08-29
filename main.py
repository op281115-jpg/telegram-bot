import random
import sqlite3
import threading
import time
import telebot
from telebot import apihelper, types

# PythonAnywhere အတွက် Proxy ချိတ်ဆက်ရန်
proxy_url = "http://proxy.server:3128"
apihelper.proxy = {"http": proxy_url, "https": proxy_url}

TOKEN = "
8658262212:AAGVbXDb7fa9G_zg8Of3qvFDA5MDN5hxmnM"
ADMIN_ID = 8762194121

bot = telebot.TeleBot(TOKEN)

# Chat တစ်ခုချင်းစီအလိုက် ဂိမ်းအခြေအနေ သီးသန့်ဖြစ်စေရန် (Multiple Chats Support)
active_games = {}

def get_chat_game(chat_id):
    if chat_id not in active_games:
        active_games[chat_id] = {"status": False, "bets": {}}
    return active_games[chat_id]

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

def get_user(user_id, name="User"):
    conn = sqlite3.connect("bot_users.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT balance, name FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    
    if row is None:
        balance = 1000  # အကောင့်အသစ်ဖွင့်ပါက ပထမဦးဆုံးရမည့် Coin ပမာဏ
        cursor.execute("INSERT INTO users (user_id, name, balance) VALUES (?, ?, ?)", (user_id, name, balance))
        conn.commit()
    else:
        balance, saved_name = row
        if saved_name != name:
            cursor.execute("UPDATE users SET name = ? WHERE user_id = ?", (name, user_id))
            conn.commit()
            
    conn.close()
    return {"balance": balance, "name": name}

def update_user_balance(user_id, amount_change):
    conn = sqlite3.connect("bot_users.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    if row:
        new_balance = row[0] + amount_change
        cursor.execute("UPDATE users SET balance = ? WHERE user_id = ?", (new_balance, user_id))
        conn.commit()
        conn.close()
        return new_balance
    conn.close()
    return None

def get_user_balance(user_id):
    conn = sqlite3.connect("bot_users.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else 0

def reply_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn_game = types.KeyboardButton("🎲 ဂိမ်းစတင်ရန်")
    btn_profile = types.KeyboardButton("👤 လက်ကျန်နှင့် ID စစ်ရန်")
    btn_deposit = types.KeyboardButton("💵 Coin ဝယ်ယူရန်")
    btn_withdraw = types.KeyboardButton("🏧 Coin ထုတ်ရန်")
    markup.add(btn_game, btn_profile)
    markup.add(btn_deposit, btn_withdraw)
    return markup

def trigger_game_start(chat_id):
    game = get_chat_game(chat_id)
    game["status"] = True
    game["bets"] = {}
    
    game_markup = types.InlineKeyboardMarkup(row_width=2)
    btn_o100 = types.InlineKeyboardButton("🔴 မာ (100 Coin)", callback_data="bet_Odd_100")
    btn_e100 = types.InlineKeyboardButton("🔵 စုံ (100 Coin)", callback_data="bet_Even_100")
    btn_o500 = types.InlineKeyboardButton("🔴 မာ (500 Coin)", callback_data="bet_Odd_500")
    btn_e500 = types.InlineKeyboardButton("🔵 စုံ (500 Coin)", callback_data="bet_Even_500")
    btn_o1000 = types.InlineKeyboardButton("🔴 မာ (1000 Coin)", callback_data="bet_Odd_1000")
    btn_e1000 = types.InlineKeyboardButton("🔵 စုံ (1000 Coin)", callback_data="bet_Even_1000")
    btn_o5000 = types.InlineKeyboardButton("🔴 မာ (5000 Coin)", callback_data="bet_Odd_5000")
    btn_e5000 = types.InlineKeyboardButton("🔵 စုံ (5000 Coin)", callback_data="bet_Even_5000")
    
    game_markup.add(btn_o100, btn_e100)
    game_markup.add(btn_o500, btn_e500)
    game_markup.add(btn_o1000, btn_e1000)
    game_markup.add(btn_o5000, btn_e5000)
    
    bot.send_message(chat_id, 
        "🎲 <b>ဂိမ်းစတင်ပါပြီ!</b>\n"
        "🍀 <b>အနိုင်များပါစေရှင့်!</b>\n\n"
        "၁၅ စက္ကန့်အတွင်း လောင်းလိုသော Coin ပမာဏနှင့် 🔴 မာ / 🔵 စုံ ကို ရွေးချယ်ပါခင်ဗျာ。",
        parse_mode="HTML", reply_markup=game_markup
    )
    
    threading.Thread(target=run_game_timer, args=(chat_id,)).start()

@bot.message_handler(commands=['start'])
def start_cmd(message):
    user_id = message.from_user.id
    name = message.from_user.first_name
    user = get_user(user_id, name)
    
    msg = (
        f"👋 <b>မင်္ဂလာပါ {name}!</b>\n"
        f"🎲 Telegram Dice Gambling Bot မှ ကြိုဆိုပါသည်။\n\n"
        f"🆔 <b>သင့် အကောင့် ID:</b> <code>{user_id}</code>\n"
        f"🪙 <b>လက်ကျန် Coin:</b> {user['balance']} Coins\n\n"
        f"အောက်ပါ မီနူးခလုတ်များမှတစ်ဆင့် အလွယ်တကူ အသုံးပြုနိုင်ပါသည်။"
    )
    bot.send_message(message.chat.id, msg, parse_mode="HTML", reply_markup=reply_keyboard())

@bot.message_handler(func=lambda message: True)
def text_handler(message):
    user_id = message.from_user.id
    name = message.from_user.first_name
    get_user(user_id, name)
    text = message.text
    
    if text == "🎲 ဂိမ်းစတင်ရန်":
        trigger_game_start(message.chat.id)
    elif text == "👤 လက်ကျန်နှင့် ID စစ်ရန်":
        current_balance = get_user_balance(user_id)
        msg = (
            f"👤 <b>အကောင့် အချက်အလက်</b>\n\n"
            f"📝 <b>အမည်:</b> {name}\n"
            f"🆔 <b>ကစားသူ ID:</b> <code>{user_id}</code>\n"
            f"🪙 <b>လက်ကျန် Coin:</b> {current_balance} Coins"
        )
        bot.send_message(message.chat.id, msg, parse_mode="HTML", reply_markup=reply_keyboard())
    elif text == "💵 Coin ဝယ်ယူရန်":
        msg = (
            f"💵 <b>Coin ဝယ်ယူရန် နည်းလမ်း</b>\n\n"
            f"အောက်ပါ ဖုန်းနံပါတ်များသို့ KPay / Wave Money ဖြင့် လွှဲနိုင်ပါသည်-\n\n"
            f"📱 <b>KPay:</b> <code>09670606627</code> (အမည်: <b>Hnin Wai Wai Aung</b>)\n"
            f"📱 <b>Wave Money:</b> <code>09765523636</code> (အမည်: <b>Phyo Htet Kyaw</b>)\n\n"
            f"📷 <b>ငွေလွှဲပြီးပါက ငွေလွှဲပြေစာပုံ (Screenshot) နှင့်တကွ အောက်ပါအတိုင်း စာရိုက်ပို့ပေးပါရှင့်။</b>\n\n"
            f"<code>/deposit &lt;ဝယ်ယူမည့် Coin ပမာဏ&gt; &lt;လုပ်ငန်းစဉ်နံပါတ် နောက်ဆုံး၆လုံး&gt;</code>"
        )
        bot.send_message(message.chat.id, msg, parse_mode="HTML", reply_markup=reply_keyboard())
    elif text == "🏧 Coin ထုတ်ရန်":
        msg = (
            f"🏧 <b>Coin ငွေသားထုတ်ယူရန် နည်းလမ်း</b>\n\n"
            f"Coin ထုတ်လိုပါက အောက်ပါပုံစံအတိုင်း **တစ်ကြောင်းတည်း** စာရိုက်ပို့ပေးပါ-\n\n"
            f"<code>/withdraw &lt;ထုတ်မည့် Coin ပမာဏ&gt; &lt;ဖုန်းနံပါတ်&gt; &lt;အကောင့်အမည်&gt;</code>"
        )
        bot.send_message(message.chat.id, msg, parse_mode="HTML", reply_markup=reply_keyboard())

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id
    name = call.from_user.first_name
    chat_id = call.message.chat.id
    get_user(user_id, name)
    current_balance = get_user_balance(user_id)
    game = get_chat_game(chat_id)
    
    if call.data == "start_game":
        bot.answer_callback_query(call.id)
        trigger_game_start(chat_id)
        
    elif call.data.startswith("bet_"):
        if not game["status"]:
            bot.answer_callback_query(call.id, "ဂိမ်း အချိန်ကုန်သွားပါပြီ။ ဂိမ်းသစ် ပြန်စပါခင်ဗျာ။")
            return
            
        if user_id in game["bets"]:
            bot.answer_callback_query(call.id, "သင် လောင်းကြေး ထပ်ထားပြီးပါပြီ။")
            return
            
        parts = call.data.split("_")
        choice = parts[1]
        amount = int(parts[2])
        
        if current_balance < amount:
            bot.answer_callback_query(call.id, "လက်ကျန် Coin မလုံလောက်ပါ၊ Coin ထပ်ဝယ်ပါ!", show_alert=True)
            return
            
        update_user_balance(user_id, -amount)
        game["bets"][user_id] = {"choice": choice, "amount": amount}
        
        choice_str = "🔴 မာ" if choice == "Odd" else "🔵 စုံ"
        bot.answer_callback_query(call.id, f"သင့် လောင်းကြေး ({choice_str} - {amount} Coins) အောင်မြင်ပါသည်။")
        bot.send_message(chat_id, f"✅ {name} (ID: <code>{user_id}</code>) မှ <b>{choice_str}</b> ကို <b>{amount} Coins</b> လောင်းလိုက်ပါပြီ။", parse_mode="HTML")

def run_game_timer(chat_id):
    time.sleep(15)
    game = get_chat_game(chat_id)
    
    if not game["status"]:
        return
        
    bot.send_message(chat_id, "🔴 <b>လောင်းကြေးပိတ်ပါပြီ!</b>\n🎲 အန်စာတုံး လှည့်နေပါပြီ...", parse_mode="HTML")
    
    dice_msg = bot.send_dice(chat_id, emoji="🎲")
    dice_value = dice_msg.dice.value
    time.sleep(3)
    
    is_even = (dice_value % 2 == 0)
    result_type = "Even" if is_even else "Odd"
    result_str = f"🔵 စုံ" if is_even else f"🔴 မာ"
    
    winners = []
    conn = sqlite3.connect("bot_users.db", check_same_thread=False)
    cursor = conn.cursor()
    
    for uid, bet_info in game["bets"].items():
        cursor.execute("SELECT balance, name FROM users WHERE user_id = ?", (uid,))
        row = cursor.fetchone()
        balance = row[0] if row else 0
        uname = row[1] if row else "User"
        
        is_win = (bet_info["choice"] == result_type)
        
        if is_win:
            win_amount = bet_info["amount"] * 3
            update_user_balance(uid, win_amount)
            winners.append(f"• {uname} (ID: <code>{uid}</code>) (+{win_amount} Coins)")
            
    conn.close()
    
    msg = f"🎯 <b>အန်စာတုံး ရလဒ်:</b> {result_str} ({dice_value})\n\n"
    if winners:
        msg += "🏆 <b>အနိုင်ရရှိသူများ:</b>\n" + "\n".join(winners)
    else:
        msg += "🏆 <b>အနိုင်ရရှိသူများ:</b>\nမည်သူမျှ အနိုင်မရရှိပါ။ (ဒိုင် အနိုင်ရသည်)"
        
    game["status"] = False
    game["bets"] = {}
    
    replay_markup = types.InlineKeyboardMarkup()
    btn_replay = types.InlineKeyboardButton("🎲 နောက်တစ်ပွဲ ထပ်လောင်းမည်", callback_data="start_game")
    replay_markup.add(btn_replay)
    
    bot.send_message(chat_id, msg, parse_mode="HTML", reply_markup=replay_markup)

@bot.message_handler(commands=['addbalance'])
def add_balance_cmd(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ သင်သည် Admin မဟုတ်ပါ။")
        return
    try:
        args = message.text.split()
        target_id = int(args[1])
        amount = int(args[2])
        update_user_balance(target_id, amount)
        new_bal = get_user_balance(target_id)
        bot.reply_to(message, f"✅ ကစားသူ ID <code>{target_id}</code> ထံသို့ Coin {amount} ဖြည့်သွင်းပြီးပါပြီ။ လက်ကျန် Coin: {new_bal} Coins", parse_mode="HTML")
        try:
            bot.send_message(target_id, f"🎉 သင့် အကောင့် (ID: <code>{target_id}</code>) ထဲသို့ Coin <b>{amount} Coins</b> ဖြည့်သွင်းပေးလိုက်ပါပြီ!\n🪙 လက်ကျန် Coin: {new_bal} Coins", parse_mode="HTML")
        except:
            pass
    except Exception:
        bot.reply_to(message, "⚠️ ရိုက်နည်းမှာ: <code>/addbalance &lt;user_id&gt; &lt;amount&gt;</code>", parse_mode="HTML")

@bot.message_handler(commands=['paid'])
def paid_cmd(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ သင်သည် Admin မဟုတ်ပါ။")
        return
    try:
        args = message.text.split()
        target_id = int(args[1])
        bot.reply_to(message, f"✅ ကစားသူ ID <code>{target_id}</code> ထံသို့ ငွေလွှဲပြီးကြောင်း အကြောင်းကြားစာ ပို့ပြီးပါပြီ။", parse_mode="HTML")
        try:
            bot.send_message(target_id, "✅ <b>ငွေလွှဲလိုက်ပါပြီ အဆင်ပြေပါစေရှင့်။</b> 🙏", parse_mode="HTML")
        except:
            pass
    except Exception:
        bot.reply_to(message, "⚠️ ရိုက်နည်းမှာ: <code>/paid &lt;user_id&gt;</code>", parse_mode="HTML")

@bot.message_handler(commands=['deposit'])
def deposit_cmd(message):
    try:
        args = message.text.split()
        amount = int(args[1])
        txn_id = args[2]
        user_id = message.from_user.id
        name = message.from_user.first_name
        get_user(user_id, name)
        
        bot.reply_to(message, f"✅ Coin ဝယ်ယူမှု တောင်းဆိုချက် ({amount} Coins) နှင့် ပြေစာကို Admin ထံ ပေးပို့လိုက်ပါပြီ။ စစ်ဆေးပြီးပါက Coin ထည့်သွင်းပေးပါမည်။")
        admin_msg = (
            f"📩 <b>Coin ဝယ်ယူရန် တောင်းဆိုမှု ရောက်ရှိလာပါသည်!</b>\n\n"
            f"👤 အမည်: {name}\n"
            f"🆔 ကစားသူ ID: <code>{user_id}</code>\n"
            f"🪙 ဝယ်ယူမည့် ပမာဏ: <b>{amount} Coins</b>\n"
            f"🔢 လုပ်ငန်းစဉ်နံပါတ်: <code>{txn_id}</code>\n\n"
            f"👉 <b>Coin ထည့်ပေးရန်:</b>\n<code>/addbalance {user_id} {amount}</code>"
        )
        bot.send_message(ADMIN_ID, admin_msg, parse_mode="HTML")
    except Exception:
        bot.reply_to(message, "⚠️ ရိုက်နည်း လွဲမှားနေပါသည်။\nဥပမာ- <code>/deposit 5000 123456</code>", parse_mode="HTML")

@bot.message_handler(commands=['withdraw'])
def withdraw_cmd(message):
    try:
        args = message.text.split()
        if len(args) < 4:
            bot.reply_to(message, "⚠️ ရိုက်နည်း လွဲမှားနေပါသည်။ (တစ်ကြောင်းတည်း ရိုက်ရန် လိုအပ်သည်)\nဥပမာ- <code>/withdraw 2000 09765523636 Mg lay</code>", parse_mode="HTML")
            return
            
        amount = int(args[1])
        phone = args[2]
        account_name = " ".join(args[3:])
        user_id = message.from_user.id
        name = message.from_user.first_name
        get_user(user_id, name)
        current_balance = get_user_balance(user_id)
        
        if amount < 1000:
            bot.reply_to(message, "❌ အနည်းဆုံး ထုတ်ယူနိုင်သည့် Coin ပမာဏမှာ ၁၀၀၀ ဖြစ်ပါသည်။")
            return
        if current_balance < amount:
            bot.reply_to(message, f"❌ သင့် လက်ကျန် Coin မလုံလောက်ပါ။ (လက်ကျန်: {current_balance} Coins)")
            return
            
        update_user_balance(user_id, -amount)
        bot.reply_to(message, f"✅ Coin ငွေထုတ်ယူရန် တောင်းဆိုမှု ({amount} Coins) ကို ပေးပို့လိုက်ပါပြီ။ ခဏစောင့်ပေးပါရှင့်။")
        
        admin_msg = (
            f"📢 <b>Coin ထုတ်ယူရန် တောင်းဆိုမှု ရောက်ရှိလာပါသည်!</b>\n\n"
            f"👤 ကစားသူ အမည်: {name}\n"
            f"🆔 ကစားသူ ID: <code>{user_id}</code>\n"
            f"🪙 ထုတ်မည့် ပမာဏ: <b>{amount} Coins</b>\n"
            f"📱 ဖုန်းနံပါတ်: <code>{phone}</code>\n"
            f"💳 အကောင့်အမည်: <code>{account_name}</code>\n\n"
            f"👉 <b>ငွေလွှဲပြီးပါက:</b>\n<code>/paid {user_id}</code>\n"
            f"👉 <b>Coin ပြန်အမ်းရန်:</b>\n<code>/addbalance {user_id} {amount}</code>"
        )
        bot.send_message(ADMIN_ID, admin_msg, parse_mode="HTML")
    except Exception:
        bot.reply_to(message, "⚠️ ရိုက်နည်း လွဲမှားနေပါသည်။\nဥပမာ- <code>/withdraw 2000 09765523636 Mg lay</code>", parse_mode="HTML")

bot.polling(none_stop=True)
