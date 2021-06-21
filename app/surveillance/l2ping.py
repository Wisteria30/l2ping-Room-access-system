import asyncio
import subprocess
from typing import Any, Dict, List, Union

from config import Config

# 密結合すぎてやばい．．．
from slack_bot import send_message
from slack_bot.block_kit import create_header_from, create_simple_section_from
from surveillance.status import Status
from util import JSON


# ユーザとmacアドレスのjsonを取得する
def load_mac_address_from(
    filename: str,
) -> Union[Dict[str, str], Any]:
    if not Config().PRODUCTION:
        return {
            "test1": "00:00:5e:00:53:00",
            "test2": "00:00:5e:00:53:01",
            "test3": "00:00:5e:00:53:02",
        }
    try:
        with open("secret.json") as f:
            import json

            mac_address_dict: JSON = json.load(f)
        return mac_address_dict["mac_address"]
    except FileNotFoundError:
        print("Can't load config file.")
        import sys

        sys.exit(1)


# 一定時間でl2pingを実行して，変更があればslack-botへ通知
def l2ping(mac_address_dict: JSON) -> List[List[str]]:

    assert mac_address_dict, "require : mac_address_dict"

    new_enter_user = list()
    new_exit_user = list()
    monitor_user = Status().monitor_user

    print("------------ start ------------")
    for (
        user,
        mac_address,
    ) in mac_address_dict.items():
        cmd = "sudo l2ping -c 1 " + mac_address
        try:
            print("------------ {} Connection start ------------".format(user))
            proc = subprocess.check_output(cmd.split()).decode()
            if "1 received" in proc and monitor_user[user] == 0:
                monitor_user[user] = 1
                new_enter_user.append(user)
                print("{} 入室".format(user))
        # ping失敗（subprocess.CalledProcessError？ひとまずExceptionでmypy通す）
        except Exception:
            if monitor_user[user] == 1:
                monitor_user[user] = 0
                new_exit_user.append(user)
                print("{} 退室".format(user))

    return [new_enter_user, new_exit_user]


# 入退室を模倣するためにグローバルでカウントを持っておく（try-exceptだとmypyにnot definedって怒られる）
l2ping_run_count = 0


# 開発環境用l2ping
def l2ping_debug(mac_address_dict: JSON) -> List[List[str]]:

    assert mac_address_dict, "require : mac_address_dict"

    # 入退室を模倣するためにグローバルでカウントを持っておく
    global l2ping_run_count
    l2ping_run_count += 1

    new_enter_user = list()
    new_exit_user = list()
    monitor_user = Status().monitor_user
    for num, user in enumerate(mac_address_dict.keys()):

        # もう少しいろんな状況で実験する
        # 3回に一回強制退室
        if l2ping_run_count != 0 and l2ping_run_count % 3 == 0:
            if monitor_user[user]:
                monitor_user[user] = 0
                new_exit_user.append(user)
        # 初回: user3まで入室させない（1人の場合のテスト）
        elif l2ping_run_count < 3:
            if num == 0 and not monitor_user[user]:
                monitor_user[user] = 1
                new_enter_user.append(user)
        # 2回目: 2人入室させる
        elif l2ping_run_count >= 4 and l2ping_run_count < 6:
            if num < 2:
                if not monitor_user[user]:
                    monitor_user[user] = 1
                    new_enter_user.append(user)
        # それ以外入室処理
        else:
            # すでにログイン済みならばスルー
            if not monitor_user[user]:
                monitor_user[user] = 1
                new_enter_user.append(user)

    return [new_enter_user, new_exit_user]


# l2ping結果を整形
def create_l2ping_result(
    new_enter_user: List[str], new_exit_user: List[str]
) -> JSON:
    l2ping_result = {
        "room_state": dict(),
        # "user_status": list(),
        "thread_ts": Status().ts,  # NoneならOpen，それ以外はスレッドに返信する
    }
    # "Collection[str]" has no attribute "append"  [attr-defined]を回避
    user_status: List[str] = list()

    monitor_user = Status().monitor_user
    room_status = Status().room_status
    # 整形
    if not room_status["is_open"] and any(monitor_user.values()):
        room_status["is_open"] = True
        # result += "Open\n"
        l2ping_result["room_state"] = {
            "is_open": room_status["is_open"],
            "message": f"{Config().ROOM_NAME}:door: : Open",
        }

    if new_enter_user:
        for user in new_enter_user:
            user_status.append(f"*[入室]* { user }\n")
            # l2ping_result["user_status"].append(f"*[入室]* { user }\n")

    if new_exit_user:
        for user in new_exit_user:
            user_status.append(f"*[退室]* { user }\n")
            # l2ping_result["user_status"].append(f"*[退室]* { user }\n")

    if room_status["is_open"] and not any(monitor_user.values()):
        room_status["is_open"] = False
        l2ping_result["room_state"] = {
            "is_open": room_status["is_open"],
            "message": f"{Config().ROOM_NAME}:door: : Close",
        }

    l2ping_result["user_status"] = user_status
    return l2ping_result


# l2ping結果をスラックに送信するメッセージ整形
async def send_l2ping_result_from(l2ping_result: JSON) -> None:

    # 送信しないなら即座に返す
    if not (l2ping_result["room_state"] or l2ping_result["user_status"]):
        return

    """Open"""
    if l2ping_result["room_state"]:
        if l2ping_result["room_state"]["is_open"]:
            print("Sending open message")
            req = await send_message(
                blocks=[
                    create_header_from(l2ping_result["room_state"]["message"])
                ]
            )
            # スレッドのタイムスタンプを設定
            Status().ts = req["ts"]
            # 送信の安定性のために少し待機
            await asyncio.sleep(1)

    """入退室処理"""
    if l2ping_result["user_status"]:
        user_blocks = list()
        for m in l2ping_result["user_status"]:
            print(f"Log: {m}")
            user_blocks.append(create_simple_section_from(m))

        await send_message(
            blocks=user_blocks,
            thread_ts=Status().ts,
        )
        # 送信の安定性のために少し待機
        await asyncio.sleep(1)

    """Close"""
    if l2ping_result["room_state"]:
        if not l2ping_result["room_state"]["is_open"]:
            print("Sending close message")

            # スレッドとチャットに対して送信
            await send_message(
                blocks=[
                    create_header_from(l2ping_result["room_state"]["message"])
                ],
                thread_ts=Status().ts,
                reply_broadcast=True,
            )
            # スレッドのタイムスタンプを一応リセット
            Status().ts = ""


async def run_l2ping(time: int = 5 * 60) -> None:
    # for dubug
    if not Config().PRODUCTION:
        time = 5

    await send_message(
        blocks=[
            create_simple_section_from(
                f"*========== {Config().ROOM_NAME} : 入退室監視開始========== *"
            )
        ]
    )

    """init"""
    # 以下をコンフィグに持っていくのもいいけど，そうすると常にmac_address_listが必要になる？
    mac_address_dict = load_mac_address_from("secret.json")
    Status().monitor_user = {key: 0 for key in mac_address_dict}
    Status().room_status = {
        "is_open": False,
        "ROOM_NAME": Config().ROOM_NAME if Config().PRODUCTION else "DebugRoom",
        "enter_user": [],
    }
    l2ping_func = l2ping if Config().PRODUCTION else l2ping_debug

    try:
        """run"""
        while True:

            print("========= start l2ping ==========")

            """update"""
            (
                new_enter_user,
                new_exit_user,
            ) = l2ping_func(mac_address_dict)

            """create and send message to slack"""
            await send_l2ping_result_from(
                create_l2ping_result(new_enter_user, new_exit_user)
            )
            Status().update_room_status()

            print(
                f"------------ monitor user ------------\n{Status().monitor_user}"
            )
            print(
                f"------------ room_status ------------\n{Status().room_status}"
            )
            print("========= end l2ping ==========")
            print(f"========= sleep {time}sec ==========")

            await asyncio.sleep(time)

    finally:
        # dockerで強制終了するときは呼ばれないかも．
        await send_message(
            blocks=[
                create_simple_section_from(
                    f"*========== {Config().ROOM_NAME} : 入退室監視終了 ==========*"
                )
            ]
        )
