class Views:
    def custom_response(self, msg: str, ts: str):
        return {
            "type": "modal",
            "callback_id": "custom_response_view",
            "title": {"type": "plain_text", "text": "Supporty", "emoji": True},
            "submit": {"type": "plain_text", "text": "Submit", "emoji": True},
            "close": {"type": "plain_text", "text": "Cancel", "emoji": True},
            "blocks": [
                {
                    "type": "section",
                    "block_id": ts,
                    "text": {
                        "type": "mrkdwn",
                        "text": f"How do you want to respond?\n```{msg}```",
                    },
                },
                {
                    "type": "input",
                    "block_id": "custom-response-input",
                    "element": {
                        "type": "plain_text_input",
                        "multiline": True,
                        "action_id": "custom-response-input",
                    },
                    "label": {"type": "plain_text", "text": "Response", "emoji": True},
                },
            ],
        }


views = Views()
