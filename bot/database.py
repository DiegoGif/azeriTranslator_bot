import psycopg2
from bot.settings import DATABASE_URL

def save_user_to_database(user_data):
    conn = psycopg2.connect(DATABASE_URL, sslmode='disable')
    with conn.cursor() as cur:
        cur.execute('''CREATE TABLE IF NOT EXISTS users
                       (user_id integer PRIMARY KEY, username text, first_name text, last_name text)''')
        cur.execute("INSERT INTO users (user_id, username, first_name, last_name) VALUES (%s, %s, %s, %s) ON CONFLICT (user_id) DO NOTHING",
                    (user_data['user_id'], user_data['username'], user_data['first_name'], user_data['last_name']))
        conn.commit()
    conn.close()
