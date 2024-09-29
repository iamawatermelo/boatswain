from slack_sdk.web.async_client import AsyncWebClient
from typing import Dict, Any

from utils.env import env

import time


async def handle_mark_resolved(body: Dict[str, Any], client: AsyncWebClient):
    res = env.airtable.resolve_request(body["message"]["ts"], body["user"]["id"])
    if not res:
        return

    msg = await client.conversations_history(
        channel=env.slack_request_channel,
        latest=body["message"]["ts"],
        limit=1,
        inclusive=True
    )

    blocks = msg["messages"][0]["blocks"]
    new_blocks = []

    for i, block in enumerate(blocks):
        if block["type"] == "rich_text":
            new_blocks.append(block)
        if block["type"] == "context":
            blocks[i]["elements"][0]["text"] = f"Resolved by <@{body['user']['id']}> at {time.strftime('%H:%M:%S %d/%m/%y %Z')}"
            new_blocks.append(block)

    await client.chat_update(
        channel=env.slack_request_channel,
        ts=body["message"]["ts"],
        text=msg["messages"][0]["text"],
        blocks=new_blocks
    )
