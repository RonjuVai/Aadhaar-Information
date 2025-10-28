import os
import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Configuration
BOT_TOKEN = os.environ.get('BOT_TOKEN', '8292852232:AAGk47XqZKocBTT3je-gco0NOPUr1I3TrC0')

# Multiple API endpoints for backup
API_ENDPOINTS = [
    "https://pkans.ct.ws/fetch.php",
    # আপনি অন্যান্য API endpoints যোগ করতে পারেন
]

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔍 Aadhaar Lookup Bot\n\n"
        "Send 12-digit Aadhaar number to get details.\n\n"
        "Example: 272756137481"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    
    if text.isdigit() and len(text) == 12:
        await process_aadhaar(update, text)
    else:
        await update.message.reply_text("❌ Please send valid 12-digit Aadhaar number")

async def process_aadhaar(update: Update, aadhaar: str):
    """Process Aadhaar lookup with multiple fallbacks"""
    processing_msg = await update.message.reply_text("🔍 Processing...")
    
    result = None
    used_api = None
    for api_url in API_ENDPOINTS:
        try:
            logger.info(f"Trying API: {api_url}")
            response = requests.get(f"{api_url}?aadhaar={aadhaar}", timeout=15)
            if response.status_code == 200 and response.text.strip():
                result = response.text
                used_api = api_url
                logger.info(f"Success with API: {api_url}")
                break
            else:
                logger.warning(f"API {api_url} returned status {response.status_code}")
        except Exception as e:
            logger.error(f"Error with API {api_url}: {e}")
            continue
    
    try:
        await processing_msg.delete()
    except:
        pass
    
    if result:
        # Format result nicely
        # If the result is JSON, we can parse it, but if it's text, we display as is.
        formatted = f"""
✅ Aadhaar: {aadhaar}

📊 Data Found:
{result[:1500]}{'...' if len(result) > 1500 else ''}

🔗 Source: {used_api}
        """
        await update.message.reply_text(formatted)
    else:
        await update.message.reply_text(
            "❌ Could not fetch data. Possible reasons:\n"
            "• API server is down\n"
            "• Network issue\n"
            "• Invalid Aadhaar number\n\n"
            "Please try again later."
        )

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🤖 Bot running...")
    app.run_polling()

if __name__ == '__main__':
    main()
