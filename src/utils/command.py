'''
メンションのコマンドはここで管理する
'''

import asyncio
from utils.config import (
    BotInfo,
    set_channel_id,
    get_channel_id
)




def get_message_from(
        cmd: str = None,
        event: dict = None,
        botInfo: BotInfo = None
    ) -> dict:
    assert cmd, "require cmd"
    cmd = cmd.strip()
    print(f"========= input cmd : { cmd } =========")
    
    message = {
        "text": "未対応のコマンドです",
        "blocks" : None
    }
    import sys
    sys.path.append("../")
    
    if cmd == "version":
        assert botInfo, "require botInfo"
        message["text"] = f"現在のバージョンは *{ botInfo.version }* です"
    elif cmd == "enter":
        from l2ping import get_room_status
        from utils.block_kit import create_enter_blockKit_from
        message['text'] = cmd
        message['blocks'] = create_enter_blockKit_from(get_room_status())
    elif cmd == "set_channel":
        old_id = get_channel_id()
        if not old_id:
            message['text'] = f"<{event['channel']}>を送信先チャンネルとして登録しました:+1:"
        else:
            message['text'] = f"送信先チャンネルを<{old_id}>から<{event['channel']}>に変更しました:+1:"
        set_channel_id(event['channel'])
        print("set channel to", get_channel_id())
    # TODO: 入退室の開始と終了を割り込めるようにする
    elif cmd == "start":
        message['text'] = "まだ入退室はメンションコマンドで制御できません:man-bowing:\n将来的には非同期処理を完全に理解できたら実装する予定です．"
    elif cmd == "stop":
        message['text'] = "まだ入退室はメンションコマンドで制御できません:man-bowing:\n将来的には非同期処理を完全に理解できたら実装する予定です．"
        
    return message
