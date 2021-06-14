import asyncio
import atexit
from typing import Dict, List

# 密結合すぎてやばい．．．
from mu_bot import send_message
from utils.block_kit import create_header_from, create_simple_section_from
from utils.config import PRODUCTION, ROOM_NAME


# スレッドのタイムスタンプを管理する
class Status(object):
    @classmethod
    def instance(cls):
        # シングルトン
        if not hasattr(cls, "_instance"):
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.ts: str = None
        # 0は不在, 1は在籍
        self.monitor_user: dict = None
        self.room_status: str = None

    def update_room_status(self):
        """init"""
        self.room_status["is_open"] = 1 in self.monitor_user.values()
        self.room_status["enter_user"] = self.room_status["exit_user"] = list()
        # 入室状況を更新する
        for user, status in self.monitor_user.items():
            if status:
                self.room_status["enter_user"].append(user)
            else:
                self.room_status["exit_user"].append(user)


# ユーザとmacアドレスのjsonを取得する
def load_mac_address_from(
    filename: str = None,
) -> dict:
    if not PRODUCTION:
        return {
            "test1": "00:00:5e:00:53:00",
            "test2": "00:00:5e:00:53:01",
            "test3": "00:00:5e:00:53:02",
        }
    try:
        import json

        json_file = json.load(f)
        return json_file["mac_address"]
    except FileNotFoundError:
        print("Can't load config file.")
        import sys

        sys.exit(1)


# 一定時間でl2pingを実行して，変更があればslack-botへ通知
def l2ping(
    mac_address_list: list = None,
) -> List[List[str]]:

    assert mac_address_list, "require : mac_address_list"

    new_enter_user = list()
    new_exit_user = list()
    monitor_user = Status.instance().monitor_user

    print("------------ start ------------")
    for (
        user,
        mac_address,
    ) in mac_address_list.items():
        cmd = "sudo l2ping -c 1 " + mac_address
        try:
            print("------------ {} Connection start ------------".format(user))
            proc = subprocess.check_output(cmd.split()).decode()
            if "1 received" in proc and monitor_user[user] == 0:
                monitor_user[user] = 1
                new_enter_user.append(user)
                print("{} 入室".format(user))
        # ping失敗
        except:
            if monitor_user[user] == 1:
                monitor_user[user] = 0
                new_exit_user.append(user)
                print("{} 退室".format(user))

    return [new_enter_user, new_exit_user]


# 開発環境用l2ping
def l2ping_debug(
    mac_address_list: list = None,
) -> List[List[str]]:

    assert mac_address_list, "require : mac_address_list"

    # 入退室を模倣するためにグローバルでカウントを持っておく
    global count
    try:
        count += 1
    except NameError as e:
        count = 1

    new_enter_user = list()
    new_exit_user = list()
    monitor_user = Status.instance().monitor_user
    for i, (user, mac_address) in enumerate(mac_address_list.items()):

        # 3回に一回退室
        if count != 0 and count % 3 == 0:
            monitor_user[user] = 0
            new_exit_user.append(user)
        # 退室以外入室処理
        else:
            monitor_user[user] = 1
            new_enter_user.append(user)

    return [new_enter_user, new_exit_user]


# l2ping結果を整形
def create_l2ping_result(
    new_enter_user: List[str], new_exit_user: List[str]
) -> dict:
    l2ping_result = {
        "room_state": dict(),
        "user_status": list(),
        "thread_ts": Status.instance().ts,  # NoneならOpen，それ以外はスレッドに返信する
    }

    monitor_user = Status.instance().monitor_user
    room_status = Status.instance().room_status
    # 整形
    if not room_status["is_open"] and any(monitor_user.values()):
        room_status["is_open"] = True
        # result += "Open\n"
        l2ping_result["room_state"] = {
            "is_open": room_status["is_open"],
            "message": f"{ROOM_NAME}:door: : Open",
        }

    if new_enter_user:
        for user in new_enter_user:
            l2ping_result["user_status"].append(f"*[入室]* { user }\n")

    if new_exit_user:
        for user in new_exit_user:
            l2ping_result["user_status"].append(f"*[退室]* { user }\n")

    if room_status["is_open"] and not any(monitor_user.values()):
        room_status["is_open"] = False
        l2ping_result["room_state"] = {
            "is_open": room_status["is_open"],
            "message": f"{ROOM_NAME}:door: : Close",
        }

    return l2ping_result


# l2ping結果をスラックに送信するメッセージ整形
async def send_l2ping_result_from(l2ping_result: dict) -> None:

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
            Status.instance().ts = req["ts"]
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
            thread_ts=Status.instance().ts,
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
                thread_ts=Status.instance().ts,
                reply_broadcast=True,
            )
            # スレッドのタイムスタンプを一応リセット
            Status.instance().ts = None


async def run_l2ping(time: int = 5 * 60) -> None:
    # for dubug
    if not PRODUCTION:
        time = 5

    await send_message(
        blocks=[
            create_simple_section_from(
                f"*========== {ROOM_NAME} : 入退室監視開始========== *"
            )
        ]
    )

    """init"""
    mac_address_list = load_mac_address_from("secret.json")
    Status.instance().monitor_user = {key: 0 for key in mac_address_list}
    Status.instance().room_status = {
        "is_open": False,
        "room_name": ROOM_NAME if PRODUCTION else "DebugRoom",
        "enter_user": [],
    }
    l2ping_func = l2ping if PRODUCTION else l2ping_debug

    try:
        room_status = Status.instance().room_status
        """run"""
        while True:

            print("========= start l2ping ==========")

            """update"""
            (
                new_enter_user,
                new_exit_user,
            ) = l2ping_func(mac_address_list)

            """create and send message to slack"""
            await send_l2ping_result_from(
                create_l2ping_result(new_enter_user, new_exit_user)
            )
            Status.instance().update_room_status()

            print(
                f"------------ monitor user ------------\n{Status.instance().monitor_user}"
            )
            print(
                f"------------ room_status ------------\n{Status.instance().room_status}"
            )
            print("========= end l2ping ==========")
            print(f"========= sleep {time}sec ==========")

            await asyncio.sleep(time)

    finally:
        # dockerで強制終了するときは呼ばれないかも．
        await send_message(
            blocks=[
                create_simple_section_from(
                    f"*========== {ROOM_NAME} : 入退室監視終了 ==========*"
                )
            ]
        )
