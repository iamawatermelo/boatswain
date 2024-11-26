from typing import Any, Dict


def get_modal() -> Dict[str, Any]:
    return {
        "title": {"type": "plain_text", "text": "Create macro", "emoji": True},
        "submit": {"type": "plain_text", "text": "Create"},
        "type": "modal",
        "callback_id": "create_macro",
        "close": {"type": "plain_text", "text": "Cancel", "emoji": True},
        "blocks": [
            {
                "type": "input",
                "block_id": "name",
                "element": {"type": "plain_text_input", "action_id": "name"},
                "label": {"type": "plain_text", "text": "Macro name", "emoji": True},
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "plain_text",
                        "text": 'This will not be shown to users.\nUse "?macro name" to execute it, case insensitive.',
                        "emoji": True,
                    }
                ],
            },
            {
                "type": "input",
                "block_id": "message",
                "element": {"type": "rich_text_input", "action_id": "message"},
                "label": {
                    "type": "plain_text",
                    "text": "Message to send (as you)",
                    "emoji": True,
                },
            },
            {
                "type": "input",
                "block_id": "behaviour",
                "element": {
                    "type": "static_select",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Behaviour",
                        "emoji": True,
                    },
                    "options": [
                        {
                            "text": {
                                "type": "plain_text",
                                "text": ":white_check_mark: Keep thread open",
                                "emoji": True,
                            },
                            "value": "keep",
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": ":no_entry: Close thread after execution",
                                "emoji": True,
                            },
                            "value": "close",
                        },
                    ],
                    "action_id": "behaviour",
                },
                "label": {"type": "plain_text", "text": "Behaviour", "emoji": True},
            },
        ],
    }
