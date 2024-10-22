from utils.env import env

def get_modal(thread_id):
    return {
        "type": "modal",
        "callback_id": "create_issue",
        "title": {
            "type": "plain_text",
            "text": "Create Issue",
            "emoji": True
        },
        "submit": {
            "type": "plain_text",
            "text": "Submit",
            "emoji": True
        },
        "close": {
            "type": "plain_text",
            "text": "Cancel",
            "emoji": True
        },
        "blocks": [
            {
                "type": "input",
                "block_id": "title",
                "element": {
                    "type": "plain_text_input",
                    "action_id": "title"
                },
                "label": {
                    "type": "plain_text",
                    "text": "Title",
                    "emoji": True
                }
            },
            {
                "type": "input",
                "block_id": "body",
                "element": {
                    "type": "plain_text_input",
                    "multiline": True,
                    "action_id": "body"
                },
                "label": {
                    "type": "plain_text",
                    "text": "Description",
                    "emoji": True
                }
            },
            {
			"type": "input",
			"block_id": "labels",
			"element": {
				"type": "static_select",
				"placeholder": {
					"type": "plain_text",
					"text": "Select a label",
					"emoji": True
				},
				"options": [
					{
						"text": {
							"type": "plain_text",
							"text": "*Bug*",
							"emoji": True
						},
						"value": "bug"
					},
					{
						"text": {
							"type": "plain_text",
							"text": "*Enhancement*",
							"emoji": True
						},
						"value": "enhancement"
					}
				],
				"action_id": "labels"
			},
			"label": {
				"type": "plain_text",
				"text": "Labels",
				"emoji": True
			}
		},
            {
                "type": "context",
                "block_id": thread_id,
                "elements": [
                    {
                        "type": "plain_text",
                        "text": f"This will be created as an issue on {env.github_repo}. Please make sure it is not a duplicate issue. If it's a duplicate, please cancel and mark as resolved.",
                        "emoji": True
                    }
                ]
            }
        ]
    }