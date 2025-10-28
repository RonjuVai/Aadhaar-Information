import os
import logging
from flask import Flask, request, jsonify
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import requests
import json

# Railway environment variables
BOT_TOKEN = os.environ.get('BOT_TOKEN', '8292852232:AAGk47XqZKocBTT3je-gco0NOPUr1I3TrC0')
API_URL = "https://pkans.ct.ws/fetch.php"
PORT = int(os.environ.get('PORT', 5000))
WEBHOOK_URL = os.environ.get('WEBHOOK_URL', '')

# Flask app for Railway
app = Flask(__name__)

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class AadhaarLookupBot:
    def __init__(self):
        self.bot_token = BOT_TOKEN
        self.application = None
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start command handler"""
        user = update.effective_user
        welcome_text = f"""
🔍 **Aadhaar Lookup Bot**

Hello {user.first_name}!

I can help you lookup Aadhaar card details using official API.

**How to Use:**
1. Send an Aadhaar number (12 digits)
2. Or use /lookup command
3. Get instant results

**Features:**
✅ Name & Father's Name
✅ Mobile Numbers
✅ Complete Address
✅ Circle Information
✅ Fast & Accurate

⚠️ **Note:** For authorized use only.
        """
        
        keyboard = [
            [InlineKeyboardButton("🔍 Lookup Now", callback_data="lookup_now")],
            [InlineKeyboardButton("📋 How to Use", callback_data="how_to_use")],
            [InlineKeyboardButton("🔒 Privacy", callback_data="privacy")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(welcome_text, reply_markup=reply_markup)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Help command handler"""
        help_text = """
📖 **How to Use This Bot:**

**Method 1:**
Simply send the 12-digit Aadhaar number directly to me.

**Method 2:**
Use /lookup command followed by Aadhaar number.

**Example:**
`/lookup 272756137481`
Or just send:
`272756137481`

**Information You'll Get:**
• Full Name
• Father's Name  
• Mobile Numbers
• Complete Address
• Circle & Location

🔒 **Privacy:** Your data is secure and not stored.
        """
        await update.message.reply_text(help_text)
    
    async def lookup_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Lookup command handler"""
        if not context.args:
            await update.message.reply_text(
                "📝 Usage: /lookup <Aadhaar Number>\n\n"
                "Example: /lookup 272756137481"
            )
            return
        
        aadhaar_number = context.args[0]
        await self.process_aadhaar_lookup(update, aadhaar_number)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle direct messages containing Aadhaar numbers"""
        message_text = update.message.text.strip()
        
        # Check if message is a 12-digit number (Aadhaar)
        if message_text.isdigit() and len(message_text) == 12:
            await self.process_aadhaar_lookup(update, message_text)
        else:
            await update.message.reply_text(
                "❌ Please send a valid 12-digit Aadhaar number.\n\n"
                "Example: 272756137481\n"
                "Or use: /lookup 272756137481"
            )
    
    async def process_aadhaar_lookup(self, update: Update, aadhaar_number: str):
        """Process Aadhaar lookup request"""
        try:
            # Show processing message
            processing_msg = await update.message.reply_text("🔄 Processing your Aadhaar lookup...")
            
            # API call
            api_response = await self.call_aadhaar_api(aadhaar_number)
            
            if api_response.get('success'):
                data = api_response['data']
                formatted_result = self.format_aadhaar_result(data, aadhaar_number)
                
                # Send result
                await update.message.reply_text(formatted_result, parse_mode='HTML')
                
                # Delete processing message
                await processing_msg.delete()
                
            else:
                await processing_msg.edit_text(f"❌ {api_response.get('error', 'Unknown error occurred')}")
                
        except Exception as e:
            logger.error(f"Aadhaar lookup error: {e}")
            await update.message.reply_text("❌ Error processing your request. Please try again.")
    
    async def call_aadhaar_api(self, aadhaar_number: str):
        """Call the Aadhaar lookup API"""
        try:
            params = {'aadhaar': aadhaar_number}
            response = requests.get(API_URL, params=params, timeout=30)
            
            if response.status_code == 200:
                # Try to parse JSON response
                try:
                    data = response.json()
                    return {'success': True, 'data': data}
                except json.JSONDecodeError:
                    # If not JSON, try to parse as text
                    text_response = response.text
                    return {'success': True, 'data': self.parse_text_response(text_response)}
            else:
                return {'success': False, 'error': f'API returned status code: {response.status_code}'}
                
        except requests.exceptions.Timeout:
            return {'success': False, 'error': 'API request timeout'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def parse_text_response(self, text_response: str):
        """Parse text response from API"""
        # This is a simplified parser - adjust based on actual API response format
        lines = text_response.split('\n')
        data = []
        
        current_record = {}
        for line in lines:
            if 'mobile' in line.lower():
                current_record['mobile'] = line.split(':')[-1].strip()
            elif 'name' in line.lower() and 'father' not in line.lower():
                current_record['name'] = line.split(':')[-1].strip()
            elif 'father' in line.lower() or 'fname' in line.lower():
                current_record['fname'] = line.split(':')[-1].strip()
            elif 'address' in line.lower():
                current_record['address'] = line.split(':')[-1].strip()
            elif 'circle' in line.lower():
                current_record['circle'] = line.split(':')[-1].strip()
        
        if current_record:
            data.append(current_record)
        
        return data
    
    def format_aadhaar_result(self, data: list, aadhaar_number: str):
        """Format the Aadhaar lookup result"""
        if not data:
            return "❌ No data found for the provided Aadhaar number."
        
        result_text = f"""
🔍 <b>Aadhaar Lookup Result</b>
📊 <b>Aadhaar Number:</b> <code>{aadhaar_number}</code>
────────────────────
"""
        
        for i, record in enumerate(data, 1):
            if len(data) > 1:
                result_text += f"\n📑 <b>Record {i}:</b>\n"
            
            result_text += f"""
👤 <b>Name:</b> {record.get('name', 'N/A')}
👨‍👦 <b>Father's Name:</b> {record.get('fname', 'N/A')}
📞 <b>Mobile:</b> {record.get('mobile', 'N/A')}
📱 <b>Alternate Mobile:</b> {record.get('alt', 'N/A')}
🏠 <b>Address:</b> {record.get('address', 'N/A')}
🌍 <b>Circle:</b> {record.get('circle', 'N/A')}
🆔 <b>Record ID:</b> {record.get('id', 'N/A')}
"""
        
        result_text += """
────────────────────
⚠️ <i>For authorized use only</i>
🔒 <i>Data source: Official API</i>
"""
        
        return result_text
    
    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle inline button clicks"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "lookup_now":
            await query.edit_message_text(
                "🔍 <b>Aadhaar Lookup</b>\n\n"
                "Please send the 12-digit Aadhaar number.\n\n"
                "<code>Example: 272756137481</code>",
                parse_mode='HTML'
            )
        elif query.data == "how_to_use":
            await query.edit_message_text(
                "📖 <b>How to Use:</b>\n\n"
                "1. Send 12-digit Aadhaar number\n"
                "2. Wait for processing\n"
                "3. Get detailed information\n\n"
                "<b>Example:</b>\n"
                "<code>272756137481</code>\n\n"
                "Or use: /lookup 272756137481",
                parse_mode='HTML'
            )
        elif query.data == "privacy":
            await query.edit_message_text(
                "🔒 <b>Privacy Policy</b>\n\n"
                "• Your data is not stored\n"
                "• Lookup history is not saved\n"
                "• Secure API connection\n"
                "• No personal information collected\n\n"
                "⚠️ For authorized purposes only",
                parse_mode='HTML'
            )
    
    def setup_handlers(self):
        """Setup bot handlers"""
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("lookup", self.lookup_command))
        
        # Message handler
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        # Callback query handler
        self.application.add_handler(CallbackQueryHandler(self.button_handler))
    
    async def setup_webhook(self):
        """Setup webhook for Railway"""
        if WEBHOOK_URL:
            webhook_url = f"{WEBHOOK_URL}/webhook"
            await self.application.bot.set_webhook(webhook_url)
            logger.info(f"Webhook set to: {webhook_url}")
    
    def run(self):
        """Run the bot"""
        # Create application
        self.application = Application.builder().token(self.bot_token).build()
        
        # Setup handlers
        self.setup_handlers()
        
        # Flask route for webhook
        @app.route('/webhook', methods=['POST'])
        async def webhook():
            """Webhook route for Telegram"""
            update = Update.de_json(request.get_json(), self.application.bot)
            await self.application.process_update(update)
            return 'OK'
        
        @app.route('/')
        def home():
            """Home route"""
            return jsonify({
                "status": "Bot is running",
                "service": "Aadhaar Lookup Bot",
                "version": "1.0"
            })
        
        @app.route('/health')
        def health():
            """Health check route"""
            return jsonify({"status": "healthy"})
        
        # Start the Flask app
        if WEBHOOK_URL:
            # Webhook mode for production
            import asyncio
            asyncio.run(self.setup_webhook())
            logger.info("Starting in webhook mode...")
        else:
            # Polling mode for development
            logger.info("Starting in polling mode...")
            self.application.run_polling()

# Create bot instance
bot = AadhaarLookupBot()

# Railway will run this
if __name__ == '__main__':
    bot.run()
    app.run(host='0.0.0.0', port=PORT, debug=False)