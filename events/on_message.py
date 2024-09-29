from utils.env import env

def handle_message(body, client, say):
    if body["event"]["channel"] != env.slack_support_channel:
        return

    subtype = body["event"].get("subtype")
    if subtype == "message_changed":
        handle_edited_message(body, client)
    if subtype == "message_deleted":
        handle_deleted_message(body, client)
    elif subtype:
        say(f"I don't support this message subtype yet. `{subtype}`")
        return
    else:
        handle_new_message(body, client)



def handle_new_message(body, client):
    user = client.users_info(user=body["event"]["user"])

    count = len(env.airtable.get_person(user["user"]["id"])["fields"]["help_requests"])

    new_blocks = body["event"]["blocks"] + [
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"Submitted by <@{user['user']['id']}>. They have {count} help requests."
                }
            ]
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Direct to FAQ"
                    },
                    "value": "direct-to-faq",
                    "action_id": "direct-to-faq"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Custom response"
                    },
                    "value": "custom-response",
                    "action_id": "custom-response"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Mark Resolved"
                    },
                    "style": "primary",
                    "value": "mark-resolved",
                    "action_id": "mark-resolved"
                }
            ]
        }
    ]

    msg = client.chat_postMessage(
        channel=env.slack_request_channel,
        blocks=new_blocks,
        text=body["event"]["text"],
        username=user["user"]["profile"]["real_name"],
        icon_url=user["user"]["profile"]["image_48"]
    )

    res = env.airtable.create_request(
        pub_thread_ts=body["event"]["ts"],
        content=body["event"]["text"],
        user_id=body["event"]["user"],
        priv_thread_ts=msg["ts"]
    )

    if not res:
        # Delete the message
        client.chat_delete(channel=env.slack_support_channel, ts=body["event"]["ts"], token=env.slack_user_token, as_user=True)
        client.chat_delete(channel=env.slack_request_channel, ts=msg["ts"], token=env.slack_user_token, as_user=True)
        client.chat_postEphemeral(
            channel=env.slack_support_channel,
            user=body["event"]["user"],
            text="You are not registered in our system. Please *insert method to get logged in airtable* before creating a request."
        )


def handle_edited_message(body, client, say):
    user = client.users_info(user=body["event"]["message"]["user"])

    old_ts = env.airtable.get_request(body["event"]["message"]["ts"])["fields"]["internal_thread"]
    
    client.chat_update(
        channel=env.slack_request_channel,
        ts=old_ts,
        blocks=body["event"]["message"]["blocks"],
        text=body["event"]["message"]["text"],
        username=user["user"]["profile"]["real_name"],
        icon_url=user["user"]["profile"]["image_48"]
    )

    env.airtable.update_request(
        pub_thread_ts=body["event"]["message"]["ts"],
        **{
            "content": body["event"]["message"]["text"],
        }
    )


def handle_deleted_message(body, client):
    env.airtable.delete_req(body["event"]["previous_message"]["ts"])
    client.chat_delete(channel=env.slack_request_channel, ts=body["event"]["previous_message"]["ts"], token=env.slack_user_token, as_user=True)
