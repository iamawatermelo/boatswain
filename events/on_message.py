from utils.env import env

def handle_message(body, client, say):
    if body["event"]["channel"] != env.slack_support_channel:
        return
    
    subtype = body["event"].get("subtype")
    if subtype == "message_changed":
        handle_edited_message(body, client, say)
    elif subtype:
        say(f"I don't support this message subtype yet. `{subtype}`")
        return
    else:
        handle_new_message(body, client, say)
    
    

def handle_new_message(body, client, say):
    user = client.users_info(user=body["event"]["user"])

    msg = client.chat_postMessage(
        channel=env.slack_request_channel,
        blocks=body["event"]["blocks"],
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
        client.chat_delete(channel=env.slack_support_channel, ts=body["event"]["ts"])
        client.chat_delete(channel=env.slack_request_channel, ts=msg["ts"])


def handle_edited_message(body, client, say):
    import json
    print(json.dumps(body, indent=2))
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
