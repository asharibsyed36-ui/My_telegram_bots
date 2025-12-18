import telebot
import yt_dlp
import os
from telebot import types

# --- CONFIGURATION ---
# Your Bot Token
BOT_TOKEN = "8400640429:AAHrjsLer_tt1R0zhFlGe1gm9JcHE5uQvJI"
bot = telebot.TeleBot(BOT_TOKEN)
user_links = {}

# Support Link
OWNER_WHATSAPP = "https://wa.me/923232522768"

# --- KEYBOARDS ---

def get_main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton("📥 Download Video")
    btn2 = types.KeyboardButton("📞 Contact Support")
    markup.add(btn1, btn2)
    return markup

# --- COMMAND HANDLERS ---

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "<b>✨ Welcome to Multi-Downloader Pro!</b>\n\n"
        "I can download videos from:\n"
        "🔹 TikTok (No Watermark)\n"
        "🔹 Instagram (Reels)\n"
        "🔹 YouTube & Facebook\n\n"
        "<i>Please send me a valid video link to begin.</i>"
    )
    bot.send_message(
        message.chat.id, 
        welcome_text, 
        parse_mode="HTML", 
        reply_markup=get_main_keyboard()
    )

@bot.message_handler(func=lambda m: m.text == "📥 Download Video")
def ask_link(message):
    bot.send_message(message.chat.id, "🌐 <b>Please paste your video link below:</b>", parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text == "📞 Contact Support")
def contact_support(message):
    bot.send_message(message.chat.id, f"📲 <b>Contact Owner:</b>\n{OWNER_WHATSAPP}", parse_mode="HTML")

# --- LINK PROCESSING ---

@bot.message_handler(func=lambda m: m.text.startswith("http"))
def process_link(message):
    user_links[message.chat.id] = message.text
    
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("🎬 Video (HD / No Watermark)", callback_data="vid"),
        types.InlineKeyboardButton("🎵 Audio (MP3)", callback_data="aud")
    )
    
    bot.send_message(
        message.chat.id, 
        "✅ <b>Link Detected!</b>\nChoose your format:", 
        parse_mode="HTML", 
        reply_markup=markup
    )

# --- DOWNLOAD LOGIC ---

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    url = user_links.get(call.message.chat.id)
    if not url:
        bot.answer_callback_query(call.id, "⚠️ Error: Link expired. Please send it again.")
        return

    # Update status message
    bot.edit_message_text("⚡ <b>Downloading... Please wait.</b>", call.message.chat.id, call.message.message_id, parse_mode="HTML")

    file_id = f"{call.message.chat.id}_{call.message.message_id}"
    
    # yt-dlp Options
    if call.data == "vid":
        ydl_opts = {
            'format': 'best',
            'outtmpl': f'video_{file_id}.%(ext)s',
            'noplaylist': True,
        }
    else:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'audio_{file_id}.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            # Fix audio extension if needed
            if call.data == "aud":
                filename = filename.rsplit('.', 1)[0] + ".mp3"

        with open(filename, 'rb') as f:
            if call.data == "vid":
                bot.send_video(call.message.chat.id, f, caption="🔥 <b>Downloaded via Multi-Downloader Pro</b>", parse_mode="HTML")
            else:
                bot.send_audio(call.message.chat.id, f, caption="🎵 <b>Audio Extracted Successfully</b>", parse_mode="HTML")

        # Cleanup
        os.remove(filename)
        bot.delete_message(call.message.chat.id, call.message.message_id)

    except Exception as e:
        bot.send_message(call.message.chat.id, "❌ <b>Download Failed!</b>\nThe link is either private or unsupported.", parse_mode="HTML")
        print(f"Error detail: {e}")

# --- BOT POLLING ---
print("Professional Bot is starting on Render...")
bot.infinity_polling()
from flask import Flask
from threading import Thread

app = Flask(__name__)

@app.route('/')
def hello(): 
    return "Bot is Running!"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))

if __name__ == "__main__":
    Thread(target=run).start()
    bot.infinity_polling()
