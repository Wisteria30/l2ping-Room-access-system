import os

from util import Singleton


class Config(Singleton):
    # initではなく定義したsetupを呼ぶことで一度だけセットアップされる
    def setup(self) -> None:
        # argsでもいいかも（現状なにかしらセットされている時点でTrue）
        self.PRODUCTION = bool(os.getenv("PRODUCTION"))

        # os.getenv:なければNone（エラーハンドリングは別途行いたいので）
        self.BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
        self.APP_TOKEN = os.getenv("SLACK_APP_TOKEN")
        self.channel_id = os.getenv("DEFAULT_SLACK_CHANNEL")

        self.ROOM_NAME = (
            os.getenv("ROOM_NAME") if self.PRODUCTION else "DebugRoom"
        )

        self.validate()

    def validate(self) -> None:
        print("\t-- validate start -- ")
        assert self.BOT_TOKEN, "require: export SLACK_BOT_TOKEN='xoxb-'"
        assert self.APP_TOKEN, "require: export SLACK_APP_TOKEN='xapp-'"
        # TODO: 非同期が理解しきれていないくて現状デフォルトが設定されていないと監視できない．．．
        assert (
            self.channel_id
        ), "require: DEFAULT_SLACK_CHANNEL=<Destination channel ID>'"

        # 本番環境のときは現状必ずROOM_NAMEを指定する
        # TODO: start-stopコマンドを実現したら，スタート時にルーム名を決めてもらうようにする
        if self.PRODUCTION:
            assert (
                self.ROOM_NAME
            ), "[PRODUCTION] require: export ROOM_NAME='my_room'"
        print("all evaluations are passed!!!")
        print("\t-- validate end -- ")
        self.show_config()

    def show_config(self) -> None:
        print("\t-- show config -- ")
        print("BOT_TOKEN :", self.BOT_TOKEN)
        print("APP_TOKEN :", self.APP_TOKEN)
        print("channel_id :", self.channel_id)
        if self.PRODUCTION:
            print("[PRODUCTION] ROOM_NAME :", self.ROOM_NAME)
        else:
            print("ROOM_NAME:", self.ROOM_NAME)


if __name__ == "__main__":
    Config()  # init
    Config().show_config()  # non init
