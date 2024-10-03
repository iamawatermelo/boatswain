from typing import Any, Dict
from slack_sdk.web.async_client import AsyncWebClient
from utils.env import env
from utils.views import views


async def handle_custom_response_btn(body: Dict[str, Any], client: AsyncWebClient):
    req = env.airtable.get_request(priv_thread_ts=body["message"]["ts"])

    await client.views_open(
        trigger_id=body["trigger_id"],
        view=views.custom_response(
            req["fields"]["content"], req["fields"]["identifier"]
        ),
    )


async def handle_custom_response(body: Dict[str, Any], client: AsyncWebClient):
    view = body["view"]

    req = env.airtable.get_request(pub_thread_ts=view["blocks"][0]["block_id"])
    env.airtable.update_request(
        pub_thread_ts=req["fields"]["identifier"],
        **{
            "status": "responded",
        }
    )

    user = await client.users_info(user=body["user"]["id"])

    for block in view["blocks"]:
        if block["block_id"] == "custom-response-input":
            await client.chat_postMessage(
                channel=env.slack_support_channel,
                text=view["state"]["values"]["custom-response-input"][
                    "custom-response-input"
                ]["value"],
                thread_ts=req["fields"]["identifier"],
                username=user["user"]["profile"]["display_name"]
                or user["user"]["real_name"],
                icon_url=user["user"]["profile"]["image_48"],
            )
            break
