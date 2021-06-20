import typing as t

from util import JSON, Singleton


# 入退室に関する状態を管理
class Status(Singleton):
    def setup(self) -> None:
        # ひとまずパブリック変数（必要とならばプライベートにする）
        # スレッドのタイムスタンプ
        self.ts: str = ""
        # 0は不在, 1は在籍
        self.monitor_user: t.Dict[str, int] = dict()
        # 部屋の状況（解錠中か:bool，部屋名:str，入室者は誰か:list）
        self.room_status: JSON = dict()

    def update_room_status(self) -> None:
        """init"""
        self.room_status["is_open"] = 1 in self.monitor_user.values()
        self.room_status["enter_user"] = self.room_status["exit_user"] = list()
        # 入室状況を更新する
        for user, status in self.monitor_user.items():
            if status:
                self.room_status["enter_user"].append(user)
