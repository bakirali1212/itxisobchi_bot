import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
def parse_admin_ids():
    ids = os.getenv('ADMIN_ID', '')
    return [int(i.strip()) for i in ids.split(',') if i.strip()]
ADMIN_ID = parse_admin_ids()
GROUP_ID = int(os.getenv('GROUP_ID', '-1'))

