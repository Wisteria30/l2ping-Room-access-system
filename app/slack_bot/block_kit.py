"""
ブロックキット用のt.Dictを作るのは冗長すぎるので，ここでまとめる
Block Kit: https://api.slack.com/block-kit
"""
import typing as t

from util import JSON


def create_header_from(
    plain_text: str,
) -> JSON:
    return {
        "type": "header",
        "text": {
            "type": "plain_text",
            "text": plain_text,
        },
    }


def create_simple_section_from(
    mrkdwn: str,
) -> JSON:
    return {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": mrkdwn,
        },
    }


def create_fields_from(
    args: t.Any,
) -> t.List[JSON]:
    fields = list()
    for arg in args:
        # t.Listなど対応
        if len(arg) > 0:
            for v in arg:
                fields.append({"type": "mrkdwn", "text": v})

        else:
            fields.append({"type": "mrkdwn", "text": arg})

    return fields


def create_section_on_filed_from(mrkdwn: str, *args: t.Any) -> JSON:
    if not len(args):
        return create_simple_section_from(mrkdwn)

    # ここら辺が原因かな
    fields = create_fields_from(args)

    return {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": mrkdwn,
        },
        "fields": fields,
    }


def create_divider() -> t.Dict[str, str]:
    return {"type": "divider"}


def create_enter_info_blockKit_from(
    room_status: JSON,
) -> t.List[JSON]:
    blocks = list()

    """施錠中"""
    if not room_status["is_open"]:
        blocks.append(create_header_from(f"{room_status['ROOM_NAME']} : 施錠中"))
        return blocks

    """解錠中"""
    blocks.append(create_header_from(f"{room_status['ROOM_NAME']} : 解錠中"))
    blocks.append(create_divider())

    blocks.append(
        create_section_on_filed_from("*入室者一覧*", room_status["enter_user"])
    )
    return blocks
