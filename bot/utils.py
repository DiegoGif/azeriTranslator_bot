from bot.settings import RATE_LIMIT
from telegram import KeyboardButton, ReplyKeyboardMarkup
from functools import wraps
import time

user_timestamps = {}

def rate_limited(update, context):
    user_id = update.effective_user.id
    current_time = time.time()
    if user_id in user_timestamps and current_time - user_timestamps[user_id] < RATE_LIMIT:
        update.message.reply_text("You're doing that too much. Please wait a moment before trying again.")
        return True
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
