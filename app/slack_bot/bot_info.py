import asyncio
import typing as t

from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.web.async_slack_response import AsyncSlackResponse
from util import Singleton


# BOT情報（とりあえず必要なものだけ）
class BotInfo(Singleton):
    def setup(self) -> None:
        self.__info = dict()
        self.__info["version"] = self.version = "1.0"

    def setInfo(self, client: AsyncWebClient) -> bool:
        print("\t--------- run client.auth_test() ------------")
        res: AsyncSlackResponse = asyncio.run(client.auth_test())
        if not res["ok"]:
            return False

        self.__info["bot_id"] = self.bot_id = res["bot_id"]
        self.__info["user_id"] = self.user_id = res["user_id"]
        return True

    def get_info(self) -> t.Dict[str, str]:
        return self.__info
