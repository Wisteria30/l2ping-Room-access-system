'''
ルートファイル（runするだけ）
'''
import asyncio
from mu_bot import run_slack_bot
from l2ping import run_l2ping
from utils.config import (
    BOT_TOKEN,
    APP_TOKEN,
    get_channel_id
)


async def main():
    print("BOT_TOKEN:", BOT_TOKEN)
    print("APP_TOKEN:", APP_TOKEN)
    print("CHANNEL_ID:", get_channel_id())
    # slack_botのプロセスとl2pingのプロセスは同時に非同期で実行する
    slack_bot = asyncio.create_task(run_slack_bot())
    l2ping = asyncio.create_task(run_l2ping())
    await slack_bot
    await l2ping
    
if __name__ == "__main__":
    asyncio.run(main())