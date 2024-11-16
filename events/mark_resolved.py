from slack_sdk.web.async_client import AsyncWebClient

from utils.env import env
from utils.queue import add_message_to_delete_queue

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
            or f"This post has been marked as resolved by <@{resolver_id}>!\nIf you have any more questions, please make a new post in <#{env.slack_support_channel}> and we'll be happy to help you out!",
        )

    # await lock_thread(thread_ts=res["fields"]["identifier"], channel_name=channel_name)

    # delete thread in req channel
    messages = await client.conversations_replies(
        channel=env.slack_request_channel, ts=ts
    )
    for message in messages["messages"]:
        add_message_to_delete_queue(
            channel_id=env.slack_request_channel, message_ts=message["ts"]
        )
