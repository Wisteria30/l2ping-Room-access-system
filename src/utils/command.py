'''
メンションのコマンドはここで管理する
'''

from utils.config import (
    BotInfo,
)

from utils.block_kit import create_enter_blockKit_from


def get_message_from(
        cmd: str = None,
        event: dict = None,
        botInfo: BotInfo = None,
        room_status: dict = None) -> dict:
    assert cmd, "require cmd"
    cmd = cmd.strip()
    print(f"input cmd : { cmd }")
    
    massage = {
        "text": "未対応のコマンドです",
        "blocks" : None
    }
    
    if cmd == "version":
        assert botInfo, "require botInfo"
        massage["text"] = f"現在のバージョンは *{ botInfo.version }* です"
    elif cmd == "enter":
        assert room_status, "require room_status"
        massage['text'] = cmd
        massage['blocks'] = create_enter_blockKit_from(room_status)

    return massage
