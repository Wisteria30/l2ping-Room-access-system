import subprocess
import json
import time
import sys
import requests

try:
    with open('secret.json') as f:
        df = json.load(f)
        slack_webhook_uri = df["slack_webhook_uri"]
        mac_address_list = df["mac_address"]
except:
    print("Can't load config file.")
    sys.exit(1)

# 0は不在, 1は在籍
monitor_user = {k: 0 for k, v in mac_address_list.items()}
status = {
        "is_open": False, "enter_user": [], "exit_user": []
}

while True:
    status["enter_user"] = []
    status["exit_user"] = []
    result = ""
    
    print("------------ start ------------")
    for user, mac_address in mac_address_list.items():
        cmd = 'sudo l2ping -c 1 ' + mac_address
        try:
            print("------------ {} Connection start ------------".format(user))
            proc = subprocess.check_output(cmd.split()).decode()
            if '1 received' in proc and monitor_user[user] == 0:
                monitor_user[user] = 1
                status["enter_user"].append(user)
                print("{} Enter Room".format(user))
        except:
            if monitor_user[user] == 1:
                monitor_user[user] = 0
                status["exit_user"].append(user)
                print("{} Exit Room".format(user))

    print("------------ monitor user ------------")
    print(monitor_user)
    print("------------ status ------------")
    print(status)

    # 整形
    if not status["is_open"] and any(monitor_user.values()):
        status["is_open"] = True
        result += "Open\n"

    if status["enter_user"]:
        for i in status["enter_user"]:
            result += "{} Enter Room\n".format(i)

    if status["exit_user"]:
        for i in status["exit_user"]:
            result += "{} Exit Room\n".format(i)

    if not status["is_open"] and not any(monitor_user.values()):
        status["is_open"] = False
        result += "Close\n"

    # POST
    if result:
        requests.post(
            slack_webhook_uri, data=json.dumps({"text": result}, ensure_ascii=False).encode("utf-8")
        )

    # 5分待ち
    time.sleep(60 * 5)
