'''
Slackとのインタラクティブ系
'''
from utils.config import (
    PRODUCTION, 
    BOT_TOKEN,
    APP_TOKEN,
    CHANNEL_TOKEN,
    BotInfo
)
from utils.command import get_message_from

# ログを出す時はアンコメント
if not PRODUCTION:
    import logging
    logging.basicConfig(level=logging.DEBUG)
    room_status = {
        "room_name": "DebugRoom", 
        "is_open": False, 
        "enter_user": [
            "test1", "test2", "test3", "test4"
        ], 
        "exit_user": [
            "test5", "test6", "test7", "test8"
        ]
    }
    



from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler


    
app = App(token=BOT_TOKEN)
botInfo = BotInfo(app.client)


@app.event("app_mention")
def mention(event, say):
    cmd = event['text'].lstrip(" ").replace(f"<@{ botInfo.user_id }>", "")
    if cmd == "":
        user_id = event["user"]
        say(f":wave: こんにちは <@{user_id}>さん!")
        return 
    if len(cmd.split(" ")) > 1:
        say(f"複数のコマンドを同時に実行するのは未対応です")
        return

    message_block = get_message_from(cmd, event, botInfo, room_status)

    say(
        text=message_block["text"], 
        blocks=message_block["blocks"]
    )
    

def run():
    handler = SocketModeHandler(app, APP_TOKEN)
    handler.start()