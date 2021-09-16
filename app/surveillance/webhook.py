"""
Slackだけじゃなく，どこかしらのサーバへ入室状況を反映させる場合に使う
"""

import base64
import json
import urllib.request
from typing import Any, Dict, List, Tuple

from config import Config
from surveillance.status import Status
from util import JSON, Singleton


class WebHook(Singleton):
    def setup(self) -> None:
        self.api_url, self.header = self._get_webhook_config()

    # これもシングルトンとして持っておく？？
    def _get_webhook_config(self) -> Tuple[str, Dict[str, str]]:
        webhook_dict: JSON = Config().secret_json["webhook"]
        api_url = webhook_dict["url"]
        username, password = list(webhook_dict["basic_auth"].items())[0]
        header = self._create_json_header_and_basic_user(username, password)
        return api_url, header

    def _create_json_header_and_basic_user(
        self, username: str, password: str
    ) -> Dict[str, str]:
        basic_user_and_pasword = base64.b64encode(
            "{}:{}".format(username, password).encode("utf-8")
        )
        header: Dict[str, str] = {
            "Authorization": "Basic " + basic_user_and_pasword.decode("utf-8"),
            "Content-Type": "application/json",
        }
        return header

    def send_request_from(
        self, request: urllib.request.Request
    ) -> Any:  # JSON or List[JSON]
        try:
            with urllib.request.urlopen(request) as res:
                body = json.loads(res.read())
        except Exception as e:
            body = {"Exception": e}

        return body

    def _get(self, url: str, params: JSON) -> List[JSON]:
        if params:
            url = "{}?{}".format(url, urllib.parse.urlencode(params))
        request = urllib.request.Request(url, headers=self.header)

        response: List[JSON] = self.send_request_from(request)
        return response

    def _put(self, url: str, data: JSON) -> JSON:
        request = urllib.request.Request(
            url, json.dumps(data).encode(), headers=self.header, method="PUT"
        )

        response: JSON = self.send_request_from(request)
        return response

    def webhook_for_room_status(self) -> JSON:
        status: JSON = Status().room_status
        # まずROOM_NAMEでidを絞る
        user_status: List[JSON] = self._get(
            url=self.api_url, params={"ROOM_NAME": status["ROOM_NAME"]}
        )

        if user_status:
            url: str = f"{self.api_url}/{user_status[0]['id']}"

        return self._put(url=url, data=status)
