
import logging
import requests
from telegram import KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from functools import wraps
from time import time

# Replace 'your-openai-api-key' with your actual OpenAI API key
openai_api_key = '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'

# Replace 'your-telegram-bot-token' with your actual Telegram bot token
TELEGRAM_TOKEN = '6684672461:AAEIISCJLFXM9i4xqXoOR3JGtC2wFRIVKGg'

# Rate limiting settings
RATE_LIMIT = 5  # seconds between messages

# Dictionary to keep track of user timestamps
user_timestamps = {}

def rate_limited(update, context):
    user_id = update.effective_user.id
    current_time = time()

    # Check if user has sent a message recently
    if user_id in user_timestamps and current_time - user_timestamps[user_id] < RATE_LIMIT:
        update.message.reply_text("You're doing that too much. Please wait a moment before trying again.")
        return True
    
    # Update the timestamp for the user's last message
    user_timestamps[user_id] = current_time
    return False

def rate_limiting(func):
    @wraps(func)
    def wrapper(update, context, *args, **kwargs):
        if not rate_limited(update, context):
            return func(update, context, *args, **kwargs)
    return wrapper

def get_style_reply_keyboard():
    keyboard = [
        [KeyboardButton("/style_formal"), KeyboardButton("/style_informal")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

def start(update, context):
    welcome_message = "Hi! I'm the AzeriTranslator bot. Send me a text, and I will translate it to Azerbaijani."
    update.message.reply_text(welcome_message, reply_markup=get_style_reply_keyboard())

def translate_text(text, style='formal'):
    headers = {
        "Authorization": f"Bearer {openai_api_key}",
        "Content-Type": "application/json"
    }

    # Craft the prompt based on the desired style
    style_text = 'in an informal style' if style == 'informal' else 'in a formal style'
    prompt_text = f"Translate this text into Azerbaijani {style_text}: {text}"

    data = {
        "model": "gpt-4-1106-preview",
        "messages": [
            {"role": "system", "content": prompt_text},
            {"role": "user", "content": text}
        ]
    }

    try:
        response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=data)
        response.raise_for_status()
        response_json = response.json()
        return response_json['choices'][0]['message']['content']
    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed: {e}")
        return "Sorry, I couldn't translate your text at this time."

@rate_limiting
def handle_message(update, context):
    input_text = update.message.text.strip()
    
    # If it's a style command from the button, update the style
    if input_text.startswith('/style_'):
        new_style = input_text.split('_')[1]
        context.user_data['style'] = new_style
        update.message.reply_text(f"Translation style changed to {new_style}. Please send me some text to translate.",
                                  reply_markup=get_style_reply_keyboard())
    else:
        # Proceed with translation for normal text
        style = context.user_data.get('style', 'formal')
        update.message.reply_text("Translating your text, please wait a moment...")
        translated_text = translate_text(input_text, style)
        update.message.reply_text(translated_text, reply_markup=get_style_reply_keyboard())

def handle_non_text(update, context):
    update.message.reply_text("Your message does not contain text. Please send me some text to translate.", reply_markup=get_style_reply_keyboard())

def main():
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text, handle_message))  # Handles text messages
    dp.add_handler(MessageHandler(~Filters.text, handle_non_text))  # Handles all other updates that aren't text messages
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
