"""
メンションのコマンドはここで管理する
"""

from config import Config

# from util. import BotInfo, get_channel_id, set_channel_id
from slack_bot.bot_info import BotInfo
from util import JSON


def get_message_from(
    cmd: str,
    event: JSON,
    botInfo: BotInfo,
) -> JSON:
    assert cmd, "require cmd"
    cmd = cmd.strip()
    print(f"========= input cmd : { cmd } =========")

    message: JSON = {
        "text": "未対応のコマンドです",
        "blocks": list(),
    }

    if cmd == "version":
        assert botInfo, "require botInfo"
        message["text"] = f"現在のバージョンは *{ botInfo.version }* です"
    elif cmd == "enter":
        from slack_bot.block_kit import create_enter_info_blockKit_from
        from surveillance import Status

        message["text"] = cmd
        if Status().room_status:
            message["blocks"] = create_enter_info_blockKit_from(
                Status().room_status
            )
    elif cmd == "set_channel":
        # 冷静にこれ権限を付けないと誰でも変えれてしまう
        # TODO: 権限がある人が実行したかどうかを判断した上で変更可能にする（Falseの部分に権限関係を書けばいいはず）
        if event["user"] in ["xxxxx", "xxxxx"]:
            old_id = Config().channel_id
            if old_id:
                message[
                    "text"
                ] = f"送信先チャンネルを<{old_id}>から<{event['channel']}>に変更しました:+1:"
            else:
                message["text"] = f"<{event['channel']}>を送信先チャンネルとして登録しました:+1:"

            Config().channel_id = event["channel"]
            print("set channel to", Config().channel_id)
        else:
            message[
                "text"
            ] = f"<@{event['user']}>さんには送信チャンネルを変更する権限がありません:man-gesturing-no:"
    # TODO: 入退室の開始と終了を割り込めるようにする
    elif cmd == "start":
        message[
            "text"
        ] = "まだ入退室はメンションコマンドで制御できません:man-bowing:\n将来的には非同期処理を完全に理解できたら実装する予定です．"
    elif cmd == "stop":
        message[
            "text"
        ] = "まだ入退室はメンションコマンドで制御できません:man-bowing:\n将来的には非同期処理を完全に理解できたら実装する予定です．"

    return message
