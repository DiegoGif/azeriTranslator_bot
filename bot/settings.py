import os

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')  # Make sure this line is correct
DATABASE_URL = os.getenv('DATABASE_URL')
RATE_LIMIT = 5  # seconds between messages
