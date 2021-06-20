"""
Slackとのインタラクティブ系
"""
from config import Config
from slack_bot.bot_info import BotInfo
from slack_bot.command import get_message_from

# 開発環境の場合はログを出力
if not Config().PRODUCTION:
    import logging

    logging.basicConfig(level=logging.DEBUG)


import typing as t

from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler

# l2pingのために非同期にする
from slack_bolt.async_app import AsyncApp
from slack_bolt.context.say.async_say import AsyncSay
from slack_sdk.web.async_slack_response import AsyncSlackResponse
from util import JSON

app = AsyncApp(token=Config().BOT_TOKEN)
botInfo = BotInfo()
botInfo.setInfo(app.client)


@app.event("app_mention")  # type: ignore
async def mention(event: JSON, say: AsyncSay) -> None:
    cmd = event["text"].lstrip(" ").replace(f"<@{ botInfo.user_id }>", "")
    if cmd == "":
        user_id = event["user"]
        await say(f":wave: こんにちは <@{user_id}>さん!")
        return
    if len(cmd.split(" ")) > 2:
        await say("複数のコマンドを同時に実行するのは未対応です")
        return

    message_block = get_message_from(cmd, event, botInfo)

    await say(
        text=message_block["text"],
        blocks=message_block["blocks"],
    )


# app.client.chat_postMessageをラッピング
async def send_message(
    text: str = "",
    thread_ts: str = "",
    reply_broadcast: bool = False,
    blocks: t.Optional[t.List[JSON]] = None,
    channel: t.Optional[str] = Config().channel_id,
) -> AsyncSlackResponse:
    assert channel, "require: args:channel=xxxxx"

    return await app.client.chat_postMessage(
        channel=channel,
        text=text,
        blocks=blocks,
        thread_ts=thread_ts,
        reply_broadcast=reply_broadcast,
    )


async def run_slack_bot() -> None:
    """https://slack.dev/bolt-python/concepts#socket-mode"""
    handler = AsyncSocketModeHandler(app, Config().APP_TOKEN)
    await handler.start_async()  # type: ignore
