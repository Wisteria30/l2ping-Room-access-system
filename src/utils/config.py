import os

# TOKEN
BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
APP_TOKEN = os.environ["SLACK_APP_TOKEN"]
try:
    CHANNEL_TOKEN = os.environ["DEFAULT_SLACK_CHANNEL"]
except KeyError as e:
    CHANNEL_TOKEN = None
try:
    # なにかしら文字が入っていたら本番環境
    PRODUCTION = bool(os.environ["PRODUCTION"])
except KeyError as e:
    PRODUCTION = None


    

# BOT情報（とりあえず必要なものだけ）  
class BotInfo():
    from slack_sdk.web import WebClient
    
    def __init__(self, client: WebClient = None):
        self.__info = dict()
        self.__info['version'] = self.version = "1.0"
        self.__setInfo__(client)
        
    def __setInfo__(self, client: WebClient = None):
        assert client, "引数にWebClientを設定してください"
        '''
        {'ok': True, 'url': 'xxx', 'team': 'xxx', 'user': 'xxx', 
            'team_id': 'xxx', 'user_id': 'メンションで使われるやつ', 
            'bot_id': 'xxx', 'is_enterprise_install': False
        }
        '''
        print("\t--------- run client.auth_test() ------------")
        res = client.auth_test()
        if not res['ok']:
            return False    
            
        self.__info['bot_id'] = self.bot_id = res['bot_id']
        self.__info['user_id'] = self.user_id = res['user_id']
    
    def get_info(self) -> dict:
        return self.__info