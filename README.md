# SupportBot

## Development

1. `python3 -m venv .venv`
2. `source .venv/bin/activate`
3. `python3 -m pip install -r requirements.txt`
4. `python3 main.py`

The following environment variables are required:

- `SLACK_BOT_TOKEN` - _Get this from Slack app dash_
- `SLACK_USER_TOKEN` - _Get this from Slack app dash_
- `SLACK_SIGNING_SECRET` - _Get this from Slack app dash_
- `SLACK_SUPPORT_CHANNEL` - _Get this from the channel link_
- `SLACK_REQUEST_CHANNEL` - _Get this from the channel link_
- `AIRTABLE_API_KEY` - _Get this from the [Airtable Builder Hub](https://airtable.com/create/tokens)_
- `AIRTABLE_BASE_ID` - _Get this from the Airtable Base URL (app...)_

The following environment variables are optional:
- `PORT` - _Defaults to 3000 if not specified_

## Deployment

Add notes on gunicorn (Don't use the dev server)