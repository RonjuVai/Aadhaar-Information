import os
import logging
import requests
import urllib3
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# SSL warnings disable
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuration
BOT_TOKEN = os.environ.get('BOT_TOKEN', '8292852232:AAGk47XqZKocBTT3je-gco0NOPUr1I3TrC0')

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
    """Process Aadhaar lookup with improved network handling"""
    processing_msg = await update.message.reply_text("🔍 Processing your request...")
    
    try:
        # Try with different approaches
        api_url = f"https://pkans.ct.ws/fetch.php?aadhaar={aadhaar}"
        
        # Create session with custom headers
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive'
        })
        
        # Try with verify=False first
        response = session.get(api_url, timeout=30, verify=False)
        
        if response.status_code == 200:
            result_text = f"""
✅ Aadhaar Lookup Successful
🔢 Number: {aadhaar}

📊 Data:
{response.text[:1800]}{'...' if len(response.text) > 1800 else ''}

💡 Source: Official API
            """
            await update.message.reply_text(result_text)
        else:
            await update.message.reply_text(f"❌ API returned status: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        await update.message.reply_text(
            "❌ Connection Error - Cannot reach API server\n\n"
            "Possible reasons:\n"
            "• API server is down\n" 
            "• Network restrictions\n"
            "• Try again later"
        )
    except requests.exceptions.Timeout:
        await update.message.reply_text("❌ Request timeout - Server is slow to respond")
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        await update.message.reply_text(f"❌ Error: {str(e)}")
    
    # Delete processing message
    try:
        await processing_msg.delete()
    except:
        pass

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🤖 Bot is running on Railway...")
    app.run_polling()

if __name__ == '__main__':
    main()
