from slack_sdk.web.async_client import AsyncWebClient
from typing import Dict, Any

from utils.env import env


async def handle_mark_resolved(body: Dict[str, Any], client: AsyncWebClient):
    res = env.airtable.resolve_request(body["message"]["ts"], body["user"]["id"])
    if not res:
        return

    await client.reactions_add(
        channel=env.slack_support_channel,
        name="white_check_mark",
        timestamp=res["fields"]["identifier"],
    )

    await client.chat_delete(
        channel=env.slack_request_channel, ts=body["message"]["ts"]
    )
