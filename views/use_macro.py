import itertools
from typing import Any, Dict
from utils.env import env


def get_modal(ts: str, user_id: str) -> Dict[str, Any]:
    macros = env.airtable.get_macros(user_id)

    return {
        "type": "modal",
        "title": {"type": "plain_text", "text": "Execute a macro", "emoji": True},
        "close": {"type": "plain_text", "text": "Cancel", "emoji": True},
        "blocks": [
            {"type": "header", "text": {"type": "plain_text", "text": "Your macros"}},
            *itertools.chain.from_iterable(
                [
                    [
                        {
                            "type": "section",
                            "text": {"type": "mrkdwn", "text": f"*{macro.name}*"},
                        },
                        macro.message,
                        {
                            "type": "context",
                            "elements": [
                                {
                                    "type": "mrkdwn",
                                    "text": ":no_entry: Closes thread"
                                    if macro.close
                                    else ":white_check_mark: Leaves thread open",
                                }
                            ],
                        },
                        {
                            "type": "actions",
                            "elements": [
                                {
                                    "type": "button",
                                    "text": {
                                        "type": "plain_text",
                                        "text": f"Execute{" and close" if macro.close else ""}",
                                        "emoji": True,
                                    },
                                    "value": f"{i};{ts}",
                                    "action_id": "execute-macro",
                                },
                                {
                                    "type": "button",
                                    "text": {
                                        "type": "plain_text",
                                        "text": "Delete macro",
                                        "emoji": True,
                                    },
                                    "style": "danger",
                                    "value": f"{i};{ts}",
                                    "action_id": "delete-macro",
                                    "confirm": {
                                        "title": {
                                            "type": "plain_text",
                                            "text": "Confirm",
                                        },
                                        "text": {
                                            "type": "plain_text",
                                            "text": f"Do you want to delete {macro.name}?",
                                        },
                                        "confirm": {
                                            "type": "plain_text",
                                            "text": "Go on",
                                        },
                                        "deny": {
                                            "type": "plain_text",
                                            "text": "Nevermind actually",
                                        },
                                    },
                                },
                            ],
                        },
                        {"type": "divider"},
                    ]
                    for i, macro in enumerate(macros)
                ]
            ),
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Create a new macro",
                            "emoji": True,
                        },
                        "value": "love you slack",
                        "style": "primary",
                        "action_id": "create-macro",
                    }
                ],
            },
        ],
    }
