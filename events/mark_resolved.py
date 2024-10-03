from slack_sdk.web.async_client import AsyncWebClient
from typing import Dict, Any

from utils.env import env


async def handle_mark_resolved(
    body: Dict[str, Any], client: AsyncWebClient, message: bool = True, custom_response: str | None = None
):
    res = env.airtable.resolve_request(body["message"]["ts"], body["user"]["id"])
    if not res:
        return

    await client.reactions_remove(
        channel=env.slack_support_channel,
        name="thinking_face",
        timestamp=res["fields"]["identifier"],
    )

    await client.reactions_add(
        channel=env.slack_support_channel,
        name="white_check_mark",
        timestamp=res["fields"]["identifier"],
    )

    if message:
        await client.chat_postMessage(
            channel=env.slack_support_channel,
            thread_ts=res["fields"]["identifier"],
            text=custom_response or f"this post has been resolved by <@{body['user']['id']}>!\nif you have any more questions, please make a new post in <#{env.slack_support_channel}> and we'll be happy to help you out!",
        )

    await client.chat_delete(
        channel=env.slack_request_channel, ts=body["message"]["ts"]
    )
