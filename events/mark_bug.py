from slack_sdk.web.async_client import AsyncWebClient
from typing import Any, Dict

from utils.env import env
from events.mark_resolved import handle_mark_resolved

async def handle_mark_bug(body: Dict[str, Any], client: AsyncWebClient):
    ts = body["message"]["ts"]
    env.airtable.update_request(
        priv_thread_ts=ts,
        **{
            "status": "responded",
            "bug_report": True,
        }
    )

    await handle_mark_resolved(body=body, client=client, custom_response=f"thanks for reporting this bug! the team will try and get it fixed as soon as possible!\nif you have any more questions, please make a new post in <#{env.slack_support_channel}> and we'll be happy to help you out!")
