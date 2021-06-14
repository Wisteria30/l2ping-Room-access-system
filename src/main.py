'''
ルートファイル（runするだけ）
'''

from mu_bot import run
from utils.config import (
    BOT_TOKEN,
    APP_TOKEN,
    CHANNEL_TOKEN
)

if __name__ == "__main__":
    print("BOT_TOKEN:", BOT_TOKEN)
    print("APP_TOKEN:", APP_TOKEN)
    print("CHANNEL_TOKEN:", CHANNEL_TOKEN)
    run()