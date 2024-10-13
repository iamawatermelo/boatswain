from slack_sdk.web.async_client import AsyncWebClient
from typing import Dict, Any


from utils.env import env


async def handle_message(body: Dict[str, Any], client: AsyncWebClient, say):
    if body["event"]["channel"] not in [
        env.slack_support_channel,
        env.slack_request_channel,
    ]:
        return

    subtype = body["event"].get("subtype")
    if body["event"].get("subtype", None) not in [
        None,
        "message_changed",
        "message_deleted",
        "file_share",
    ]:
        return

    match body["event"]["channel"]:
        case env.slack_support_channel:
            match subtype:
                case None | "file_share":
                    if body["event"].get("thread_ts"):
                        await handle_new_support_response(body, client)
                    else:
                        await handle_new_message(body, client)
                case "message_changed":
                    if body["event"].get("previous_message").get("thread_ts"):
                        await handle_edited_message(
                            body,
                            client,
                            ts=body["event"]["previous_message"]["thread_ts"],
                        )
                case "message_deleted":
                    await handle_deleted_message(body, client)

        case env.slack_request_channel:
            match subtype:
                case None | "file_share":
                    if body["event"].get("thread_ts"):
                        await handle_new_request_message(body, client)
                case "message_changed":
                    if body["event"].get("previous_message").get("thread_ts"):
                        await handle_edited_message(
                            body,
                            client,
                            ts=body["event"]["previous_message"]["thread_ts"],
                        )


async def handle_new_support_response(body: Dict[str, Any], client: AsyncWebClient):
    req = env.airtable.get_request(body["event"]["thread_ts"])
    if not req:
        return

    if req["fields"]["status"] == "resolved":
        # make sure the sender is not in the requests channel
        sender_id = body["event"]["user"]
        support_team = await client.conversations_members(channel=env.slack_request_channel)
        if sender_id in support_team["members"]:
            return
        await client.chat_postMessage(
            channel=env.slack_support_channel,
            thread_ts=req["fields"]["identifier"],
            text=f"this thread has been resolved - please make a new post in <#{env.slack_support_channel}> if you have any more questions!",
        )
        return

    req_msg = await client.conversations_history(
        channel=env.slack_request_channel,
        latest=req["fields"]["internal_thread"],
        limit=1,
        inclusive=True,
    )

    if not req_msg:
        return

    user = await client.users_info(user=body["event"]["user"])
    text = body["event"].get("text", "")

    if body["event"].get("files"):
        files = body["event"]["files"]
        for file in files:
            filename = file["name"]
            if files.index(file) > 0:
                text += f", <{file['permalink']}|{filename}>"
            else:
                text += f"\n<{file['permalink']}|{filename}>"

    await client.chat_postMessage(
        channel=env.slack_request_channel,
        thread_ts=req["fields"]["internal_thread"],
        text=text,
        username=user["user"]["profile"]["display_name"],
        icon_url=user["user"]["profile"]["image_48"],
    )


async def handle_new_message(body: Dict[str, Any], client: AsyncWebClient):
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

    thread_url = f"https://hackclub.slack.com/archives/{env.slack_support_channel}/p{body['event']['ts'].replace('.', '')}"
    new_blocks = [
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
        text="",
        username=user["user"]["profile"]["display_name"],
        icon_url=user["user"]["profile"]["image_48"],
    )

    env.airtable.create_request(
        pub_thread_ts=body["event"]["ts"],
        content=body["event"]["text"],
        user_id=body["event"]["user"],
        priv_thread_ts=msg["ts"],
    )


async def handle_edited_message(body: Dict[str, Any], client: AsyncWebClient, ts: str):
    return  # Will be implemented later
    if body["event"]["channel"] == env.slack_support_channel:
        req = env.airtable.get_request(pub_thread_ts=ts)
    else:
        req = env.airtable.get_request(priv_thread_ts=ts)

    if not req:
        print("no req")
        return

    text: str = body["event"]["message"]["text"]
    if ":shushing_face:" in text:
        return

    user_id = body.get("event", {}).get("message", {}).get("user")
    print(user_id)
    user = await client.users_info(user="U054VC2KM9P")

    if body["event"]["message"].get("files"):
        files = body["event"]["message"]["files"]
        for file in files:
            filename = file["name"]
            if files.index(file) > 0:
                text += f", <{file['permalink']}|{filename}>"
            else:
                text += f"\n<{file['permalink']}|{filename}>"

    await client.chat_update(
        channel=(
            env.slack_request_channel
            if body["event"]["channel"] == env.slack_support_channel
            else env.slack_support_channel
        ),
        ts=(
            req["fields"]["internal_thread"]
            if body["event"]["channel"] == env.slack_support_channel
            else req["fields"]["identifier"]
        ),
        text=text,
        username=user["user"]["profile"]["display_name"],
        icon_url=user["user"]["profile"]["image_48"],
    )


async def handle_deleted_message(body: Dict[str, Any], client: AsyncWebClient):
    env.airtable.delete_req(body["event"]["previous_message"]["ts"])
    msg = await client.conversations_history(
        channel=env.slack_request_channel,
        latest=body["event"]["previous_message"]["ts"],
        limit=1,
        inclusive=True,
    )
    if msg:
        await client.chat_delete(
            channel=env.slack_request_channel,
            ts=body["event"]["previous_message"]["ts"],
            token=env.slack_user_token,
            as_user=True,
        )


async def handle_new_request_message(body: Dict[str, Any], client: AsyncWebClient):
    req = env.airtable.get_request(priv_thread_ts=body["event"]["thread_ts"])
    if not req:
        return

    text: str = body["event"]["text"]
    if ":shushing_face:" in text:
        return

    user = await client.users_info(user=body["event"]["user"])
    text = body["event"].get("text", "")

    if body["event"].get("files"):
        files = body["event"]["files"]
        for file in files:
            filename = file["name"]
            if files.index(file) > 0:
                text += f", <{file['permalink']}|{filename}>"
            else:
                text += f"\n<{file['permalink']}|{filename}>"

    await client.chat_postMessage(
        channel=env.slack_support_channel,
        thread_ts=req["fields"]["identifier"],
        text=text,
        username=user["user"]["profile"]["display_name"],
        icon_url=user["user"]["profile"]["image_48"],
    )
