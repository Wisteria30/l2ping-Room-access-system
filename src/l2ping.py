import asyncio, atexit
from utils.config import (
    PRODUCTION,
    ROOM_NAME
)
from typing import List

from utils.block_kit import create_simple_section_from
# 密結合すぎてやばい．．．
from mu_bot import send_message

# 0は不在, 1は在籍（パブリックにおくべきかはわからない）
def set_monitor_user(new_monitor_user: dict = None) :
    global monitor_user
    monitor_user = new_monitor_user
    
def get_monitor_user() -> dict :
    global monitor_user
    if not monitor_user:
        set_monitor_user()
    return monitor_user

def set_room_status(new_room_status: dict = None) :
    global room_status
    room_status = new_room_status
    
def update_room_status():
    monitor_user = get_monitor_user()
    room_status = get_room_status()
    '''init'''
    room_status["is_open"] = 1 in monitor_user.values()
    room_status["enter_user"] = list()
    room_status["exit_user"]  = list()
    # 入室状況を更新する
    for user, status in monitor_user.items():
        if status:
            room_status["enter_user"].append(user)
        else:
            room_status["exit_user"].append(user)
    
def get_room_status() -> dict :
    global room_status
    if not room_status:
        set_room_status()
    return room_status

# ユーザとmacアドレスのjsonを取得する
def load_mac_address_from(filename: str = None) -> dict:
    if not PRODUCTION:
        return {
            "test1" : "00:00:5e:00:53:00",
            "test2" : "00:00:5e:00:53:01",
            "test3" : "00:00:5e:00:53:02"
        }
    try:
        import json
        json_file = json.load(f)
        return json_file["mac_address"]
    except FileNotFoundError:
        print("Can't load config file.")
        import sys
        sys.exit(1)
    
        
'''一定時間でl2pingを実行して，変更があればslack-botへ通知'''
def l2ping(
        mac_address_list: list = None,
        monitor_user: dict = None
    ) -> List[List[str]]:
    
    assert mac_address_list, "require : mac_address_list"
    monitor_user = get_monitor_user()
    
    new_enter_user = list()
    new_exit_user = list()
    print("------------ start ------------")
    for user, mac_address in mac_address_list.items():
        cmd = 'sudo l2ping -c 1 ' + mac_address
        try:
            print("------------ {} Connection start ------------".format(user))
            proc = subprocess.check_output(cmd.split()).decode()
            if '1 received' in proc and monitor_user[user] == 0:
                monitor_user[user] = 1
                new_enter_user.append(user)
                print("{} 入室".format(user))
        # ping失敗
        except:
            if monitor_user[user] == 1:
                monitor_user[user] = 0
                new_exit_user.append(user)
                print("{} 退室".format(user))
    
    set_monitor_user(new_monitor_user=monitor_user)
    return [new_enter_user, new_exit_user]


'''開発環境用l2ping'''
def l2ping_debug(
        mac_address_list: list = None
    ) -> List[List[str]]:
    
    assert mac_address_list, "require : mac_address_list"
    monitor_user = get_monitor_user()
    
    new_enter_user = list()
    new_exit_user = list()
    print("------------ start ------------")
    for i, (user, mac_address) in enumerate(mac_address_list.items()):
        if i%2 == 0:
            monitor_user[user] = 1
            new_enter_user.append(user)
        else:
            monitor_user[user] = 0
            new_exit_user.append(user)

    set_monitor_user(new_monitor_user=monitor_user)
    return [new_enter_user, new_exit_user]
  
async def run_l2ping(time: int = 5*60):
    # for dubug
    # time = 10
    await send_message(
        blocks=[create_simple_section_from("*==========入退室監視開始==========*")]
    )
    
    try:
        '''init'''
        mac_address_list = load_mac_address_from("secret.json")  
        set_monitor_user(
            new_monitor_user={key: 0 for key in mac_address_list}
        )
        set_room_status(
            new_room_status = {
                "is_open": False,
                "room_name": ROOM_NAME if PRODUCTION else "DebugRoom",
                "enter_user": [], 
        })
        l2ping_func = l2ping if PRODUCTION else l2ping_debug
        monitor_user = get_monitor_user()
        room_status = get_room_status()
        
        '''run'''
        while True:

            print("========= start l2ping ==========")
            '''update'''
            new_enter_user, new_exit_user = l2ping_func(mac_address_list)
            update_room_status()
            
            '''create_message'''        
            result = ""
            # 整形
            if not room_status["is_open"] and any(monitor_user.values()):
                status["is_open"] = True
                result += "Open\n"

            if new_enter_user:
                for user in new_enter_user:
                    result += "{} 入室\n".format(user)

            if new_exit_user:
                for user in new_exit_user:
                    result += "{} 退室\n".format(user)

            if room_status["is_open"] and not any(monitor_user.values()):
                room_status["is_open"] = False
                result += "Close\n"
            
            print(f"------------ monitor user ------------\n{monitor_user}")
            print(f"------------ room_status ------------\n{room_status}")
            
            print("========= end l2ping ==========")
            
            # 仮
            if result:
                await send_message(
                    blocks = [create_simple_section_from(result)]
                )
                
            print(f"========= sleep {time}sec ==========")
            await asyncio.sleep(time)
    finally:
        # dockerで強制終了するときは呼ばれないかも．
        await send_message(
            blocks=[create_simple_section_from("*==========入退室監視終了==========*")]
        )