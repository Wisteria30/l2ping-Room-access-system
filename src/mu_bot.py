'''
Slackとのインタラクティブ系
'''
import asyncio
from utils.config import (
    PRODUCTION, 
    BOT_TOKEN,
    APP_TOKEN,
    get_channel_id,
    BotInfo
)
from utils.command import get_message_from

# 開発環境の場合はログを出力
if not PRODUCTION:
    import logging
    logging.basicConfig(level=logging.DEBUG)
    


# l2pingのために非同期にする
from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler

    
app = AsyncApp(token=BOT_TOKEN)
botInfo = BotInfo()
asyncio.run(botInfo.setInfo(app.client))


@app.event("app_mention")
async def mention(event, say):
    cmd = event['text'].lstrip(" ").replace(f"<@{ botInfo.user_id }>", "")
    if cmd == "":
        user_id = event["user"]
        await say(f":wave: こんにちは <@{user_id}>さん!")
        return 
    if len(cmd.split(" ")) > 2:
        await say(f"複数のコマンドを同時に実行するのは未対応です")
        return

    message_block = get_message_from(cmd, event, botInfo)

    await say(
        text=message_block["text"], 
        blocks=message_block["blocks"]
    )
    
async def send_message(text: str = "", blocks: list = None, channel: str = get_channel_id()):
    assert channel, "require: args:channel=xxxxx"
    await app.client.chat_postMessage(
        channel=channel,
        text=text,
        blocks=blocks,
    )

async def run_slack_bot():
    '''https://slack.dev/bolt-python/concepts#socket-mode'''
    handler = AsyncSocketModeHandler(app, APP_TOKEN)
    await handler.start_async()