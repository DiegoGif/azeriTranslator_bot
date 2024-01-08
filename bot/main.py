from telegram.ext import Updater
import logging
from bot.handlers import register_handlers
from bot.settings import TELEGRAM_TOKEN

def main():
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher
    register_handlers(dp)
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
