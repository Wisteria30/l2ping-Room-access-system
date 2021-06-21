"""
ルートファイル（runするだけ）
"""
import asyncio

from slack_bot import run_slack_bot
from surveillance import run_l2ping


async def main() -> None:
    # slack_botのプロセスとl2pingのプロセスは同時に非同期で実行する
    slack_bot = asyncio.create_task(run_slack_bot())
    l2ping = asyncio.create_task(run_l2ping())
    await slack_bot
    await l2ping


if __name__ == "__main__":
    asyncio.run(main())
