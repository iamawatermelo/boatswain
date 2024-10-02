from slack_bolt.async_app import AsyncApp
from slack_sdk.web.async_client import AsyncWebClient
from typing import Callable, Dict, Any

from utils.env import env
from events.on_message import handle_message
from events.mark_resolved import handle_mark_resolved

app = AsyncApp(token=env.slack_bot_token, signing_secret=env.slack_signing_secret)


@app.event("message")
async def handle_message_events(body: Dict[str, Any], client: AsyncWebClient, say):
    await handle_message(body, client, say)


@app.action("mark-resolved")
async def handle_mark_resolved_button(
    ack: Callable[[], None], body: Dict[str, Any], client: AsyncWebClient
):
    await ack()

    await handle_mark_resolved(body, client)


if __name__ == "__main__":
    app.start(port=env.port)
