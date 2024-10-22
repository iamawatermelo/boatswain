from slack_sdk.web.async_client import AsyncWebClient
from typing import Dict, Any

from utils.env import env
from utils.lock_thread import lock_thread


async def handle_mark_resolved(
    ts,
    resolver_id,
    client: AsyncWebClient,
    message: bool = True,
    custom_response: str | None = None,
):
    # channel_name = await client.conversations_info(channel=env.slack_support_channel)
    # if not channel_name["channel"]["is_channel"]:
    #     return
    # channel_name = channel_name["channel"]["name"]

    res = env.airtable.resolve_request(ts, resolver_id)
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
            text=custom_response
            or f"this post has been resolved by <@{resolver_id}>!\nif you have any more questions, please make a new post in <#{env.slack_support_channel}> and we'll be happy to help you out!",
        )

    # await lock_thread(thread_ts=res["fields"]["identifier"], channel_name=channel_name)

    # delete thread in req channel
    messages = await client.conversations_replies(
        channel=env.slack_request_channel, ts=ts
    )
    for message in messages["messages"]:
        await client.chat_delete(
            channel=env.slack_request_channel,
            ts=message["ts"],
            as_user=True,
            token=env.slack_user_token,
        )
