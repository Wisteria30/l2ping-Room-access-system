import os

# TOKEN
try:
    BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
except KeyError as e:
    print("require: export SLACK_BOT_TOKEN='xoxb-'")
    import sys
    sys.exit(1)
try:
    APP_TOKEN = os.environ["SLACK_APP_TOKEN"]
except KeyError as e:
    print("require: export SLACK_APP_TOKEN='xapp-'")
    sys.exit(1)

# TODO: 非同期が理解しきれていないくて現状デフォルトが設定されていないと監視できない．．．
def set_channel_id(new_channel_id):
    global channel_id
    channel_id = new_channel_id
    
def get_channel_id():
    global channel_id
    return channel_id
try:
    _CHANNEL_ID = os.environ["DEFAULT_SLACK_CHANNEL"]
except KeyError as e:
    _CHANNEL_ID = None
finally:
    set_channel_id(_CHANNEL_ID)

ROOM_NAME = ""
try:
    # なにかしら文字が入っていたら本番環境
    PRODUCTION = bool(os.environ["PRODUCTION"])
    if PRODUCTION:
        try:
            # 本番環境なら部屋名を必須にする
            ROOM_NAME = os.environ["ROOM_NAME"]
        except KeyError as e:
            print("require: export ROOM_NAME='my_room'")
            sys.exit(1)
except KeyError as e:
    PRODUCTION = None

    

# BOT情報（とりあえず必要なものだけ）  
class BotInfo():
    from slack_sdk.web import WebClient
    
    def __init__(self):
        self.__info = dict()
        self.__info['version'] = self.version = "1.0"
        
    async def setInfo(self, client: WebClient = None):
        assert client, "引数にWebClientを設定してください"
        '''
        {'ok': True, 'url': 'xxx', 'team': 'xxx', 'user': 'xxx', 
            'team_id': 'xxx', 'user_id': 'メンションで使われるやつ', 
            'bot_id': 'xxx', 'is_enterprise_install': False
        }
        '''
        print("\t--------- run client.auth_test() ------------")
        res = await client.auth_test()
        if not res['ok']:
            return False    
            
        self.__info['bot_id'] = self.bot_id = res['bot_id']
        self.__info['user_id'] = self.user_id = res['user_id']
    
    def get_info(self) -> dict:
        return self.__info