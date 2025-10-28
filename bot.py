import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from requests_html import HTMLSession
import asyncio

BOT_TOKEN = os.environ.get('BOT_TOKEN', '8292852232:AAGk47XqZKocBTT3je-gco0NOPUr1I3TrC0')

logging.basicConfig(level=logging.INFO)
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
    """Process Aadhaar lookup with JavaScript rendering"""
    processing_msg = await update.message.reply_text("🔍 Processing with advanced method...")
    
    try:
        # Use HTMLSession to handle JavaScript
        session = HTMLSession()
        
        url = f"https://pkans.ct.ws/fetch.php?aadhaar={aadhaar}"
        
        # Send request with browser-like headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        response = session.get(url, headers=headers, timeout=30)
        
        # If we get JavaScript challenge, try to render it
        if '<script' in response.text and 'aes.js' in response.text:
            await processing_msg.edit_text("🔄 Bypassing security protection...")
            
            # Render JavaScript (this might work for simple challenges)
            await response.html.arender(timeout=20)
            
            # Get the rendered content
            rendered_content = response.html.html
            
            if 'aadhaar' in rendered_content.lower() or 'mobile' in rendered_content.lower():
                result = self.extract_data_from_html(rendered_content)
            else:
                result = "❌ Security protection could not be bypassed"
        else:
            result = response.text
        
        # Format and send result
        if len(result) > 4000:
            result = result[:4000] + "...\n[Response truncated]"
            
        await update.message.reply_text(
            f"✅ Aadhaar: {aadhaar}\n\n"
            f"📊 Data:\n{result}"
        )
        
    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text(f"❌ Advanced method failed: {str(e)}")
    
    try:
        await processing_msg.delete()
    except:
        pass

def extract_data_from_html(self, html_content):
    """Extract meaningful data from HTML content"""
    # Simple text extraction - you can enhance this
    lines = html_content.split('\n')
    data_lines = []
    
    for line in lines:
        line = line.strip()
        if line and len(line) > 10 and '<' not in line and '>' not in line:
            data_lines.append(line)
    
    return '\n'.join(data_lines[:20]) if data_lines else "No readable data found"

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🤖 Bot running with advanced method...")
    app.run_polling()

if __name__ == '__main__':
    main()
