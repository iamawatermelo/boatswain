from slack_bolt import App
from utils.env import env
from events.on_message import handle_message

app = App(
    token=env.slack_bot_token,
    signing_secret=env.slack_signing_secret
)

@app.event("message")
def handle_message_events(body, client, say):
    handle_message(body, client, say)

if __name__ == "__main__":
    app.start(port=int(env.port))