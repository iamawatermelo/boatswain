from slack_sdk.web.async_client import AsyncWebClient
from typing import Dict, Any


from utils.env import env


async def handle_message(body: Dict[str, Any], client: AsyncWebClient, say):
    if body["event"]["channel"] != env.slack_support_channel:
        return

    if body["event"].get("thread_ts"):
        return

    subtype = body["event"].get("subtype")
    if subtype == "message_changed":
        await handle_edited_message(body, client)
    elif subtype == "message_deleted":
        await handle_deleted_message(body, client)
    elif subtype == "file_share":
        await handle_new_message(body, client, file=True)
    elif subtype:
        return
    else:
        await handle_new_message(body, client)


async def handle_new_message(body: Dict[str, Any], client: AsyncWebClient, file: bool = False):
    user = await client.users_info(user=body["event"]["user"])

    airtable_user = env.airtable.get_person(user["user"]["id"])
    if not airtable_user:
        forename = user["user"]["profile"]["first_name"]
        surname = user["user"]["profile"]["last_name"]
        slack_id = user["user"]["id"]
        email = user["user"]["profile"].get("email")
        env.airtable.create_person(forename, surname, email, slack_id)
        count = 0
    else:
        count = len(airtable_user.get("fields", {}).get("help_requests", []))

    await client.reactions_add(
        channel=env.slack_support_channel,
        name="thinking_face",
        timestamp=body["event"]["ts"],
    )

    if count == 0:
        await client.chat_postMessage(
            channel=env.slack_support_channel,
            thread_ts=body["event"]["ts"],
            text=f"hey there {user['user']['real_name']}! it looks like this is your first time in the support channel. We've recieved your question and will get back to you as soon as possible. In the meantime, feel free to check out our <https://hack.club/low-skies-faq|FAQ> for answers to common questions. If you have any more questions, please make a new post in <#{env.slack_support_channel}> so we can help you quicker!",
        )

    if file:
        files = body["event"]["files"]
        links = "\n".join([f"<{file['permalink']}|{file['name']}>" for file in files])
        body["event"]["text"] += f"\n\n{links}"

    thread_url = f"https://hackclub.slack.com/archives/{env.slack_support_channel}/p{body['event']['ts'].replace('.', '')}"
    new_blocks = (body["event"].get("blocks") or [{'type': 'rich_text', 'block_id': 'blockies', 'elements': [{'type': 'rich_text_section', 'elements': [{'type': 'text', 'text': 'There was no text submitted with the files'}]}]}]) + [
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"Submitted by <@{user['user']['id']}>. They have {count} other help requests. <{thread_url}|Go to thread>",
                }
            ],
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Direct to FAQ"},
                    "value": "direct-to-faq",
                    "action_id": "direct-to-faq",
                },
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Custom response"},
                    "value": "custom-response",
                    "action_id": "custom-response",
                },
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Mark Bug"},
                    "value": "mark-bug",
                    "action_id": "mark-bug",
                },
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Mark Resolved"},
                    "style": "primary",
                    "value": "mark-resolved",
                    "action_id": "mark-resolved",
                },
            ],
        },
    ]

    msg = await client.chat_postMessage(
        channel=env.slack_request_channel,
        blocks=new_blocks,
        text=body["event"]["text"],
        username=user["user"]["profile"]["real_name"],
        icon_url=user["user"]["profile"]["image_48"],
    )

    env.airtable.create_request(
        pub_thread_ts=body["event"]["ts"],
        content=body["event"]["text"],
        user_id=body["event"]["user"],
        priv_thread_ts=msg["ts"],
    )


async def handle_edited_message(body: Dict[str, Any], client: AsyncWebClient):
    user = await client.users_info(user=body["event"]["message"]["user"])

    old_ts = env.airtable.get_request(body["event"]["message"]["ts"])["fields"][
        "internal_thread"
    ]

    # fetch message
    msg = await client.conversations_history(
        channel=env.slack_request_channel, latest=old_ts, limit=1, inclusive=True
    )

    blocks = msg["messages"][0]["blocks"]
    new_blocks = body["event"]["message"]["blocks"]

    blocks[0] = new_blocks[0]

    await client.chat_update(
        channel=env.slack_request_channel,
        ts=old_ts,
        blocks=blocks,
        text=body["event"]["message"]["text"],
        username=user["user"]["profile"]["real_name"],
        icon_url=user["user"]["profile"]["image_48"],
    )

    env.airtable.update_request(
        pub_thread_ts=body["event"]["message"]["ts"],
        **{
            "content": body["event"]["message"]["text"],
        },
    )


async def handle_deleted_message(body: Dict[str, Any], client: AsyncWebClient):
    env.airtable.delete_req(body["event"]["previous_message"]["ts"])
    await client.chat_delete(
        channel=env.slack_request_channel,
        ts=body["event"]["previous_message"]["ts"],
        token=env.slack_user_token,
        as_user=True,
    )
