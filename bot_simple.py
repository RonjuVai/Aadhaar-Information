import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

BOT_TOKEN = os.environ.get('BOT_TOKEN', '8292852232:AAGk47XqZKocBTT3je-gco0NOPUr1I3TrC0')

async def start(update: Update, context):
    await update.message.reply_text("🔍 Aadhaar Bot - Send Aadhaar number")

async def handle_message(update: Update, context):
    text = update.message.text.strip()
    
    if text.isdigit() and len(text) == 12:
        await update.message.reply_text("🔄 Processing...")
        
        try:
            response = requests.get(f"https://pkans.ct.ws/fetch.php?aadhaar={text}")
            if response.status_code == 200:
                result = f"🔍 Aadhaar: {text}\n\nData:\n{response.text[:500]}..."
                await update.message.reply_text(result)
            else:
                await update.message.reply_text("❌ API Error")
        except:
            await update.message.reply_text("❌ Network Error")
    else:
        await update.message.reply_text("❌ Send 12-digit number")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    
    print("🤖 Bot running...")
    app.run_polling()

if __name__ == '__main__':
    main()
