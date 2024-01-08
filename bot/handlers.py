from telegram.ext import CommandHandler, MessageHandler, Filters
from bot.utils import get_style_reply_keyboard, rate_limiting
from bot.database import save_user_to_database
import requests
from bot import settings

def start(update, context):
    welcome_message = "Hi! I'm the AzeriTranslator bot. Send me a text, and I will translate it to Azerbaijani."
    update.message.reply_text(welcome_message, reply_markup=get_style_reply_keyboard())

def translate_text(text, style='formal'):
    headers = {
        "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
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
    user = update.effective_user
    user_data = {
        'user_id': user.id,
        'username': user.username or '',
        'first_name': user.first_name or '',
        'last_name': user.last_name or ''
    }
    save_user_to_database(user_data)
    input_text = update.message.text.strip()
    if input_text.startswith('/style_'):
        new_style = input_text.split('_')[1]
        context.user_data['style'] = new_style
        update.message.reply_text(f"Translation style changed to {new_style}. Please send me some text to translate.",
                                  reply_markup=get_style_reply_keyboard())
    else:
        style = context.user_data.get('style', 'formal')
        update.message.reply_text("Translating your text, please wait a moment...")
        translated_text = translate_text(input_text, style)
        update.message.reply_text(translated_text, reply_markup=get_style_reply_keyboard())

def handle_non_text(update, context):
    update.message.reply_text("Your message does not contain text. Please send me some text to translate.", reply_markup=get_style_reply_keyboard())

def register_handlers(dp):
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text, handle_message))
    dp.add_handler(MessageHandler(~Filters.text, handle_non_text))
