from pyairtable import Api


class AirtableManager:
    def __init__(self, api_key: str, base_id: str):
        api = Api(api_key)
        self.people_table = api.table(base_id, "people")
        self.help_table = api.table(base_id, "help")
        print("Connected to Airtable")

    def create_person(self, first_name: str, last_name: str, email: str, slack_id: str):
        self.people_table.create(
            {
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "slack_id": slack_id,
                "preexisting_user": False,
            }
        )

    def get_person(self, user_id: str):
        user = self.people_table.first(formula=f'{{slack_id}} = "{user_id}"')
        return user

    def get_request(
        self, pub_thread_ts: str | None = None, priv_thread_ts: str | None = None
    ):
        if pub_thread_ts:
            req = self.help_table.first(formula=f'{{identifier}} = "{pub_thread_ts}"')
        elif priv_thread_ts:
            req = self.help_table.first(
                formula=f'{{internal_thread}} = "{priv_thread_ts}"'
            )

        return req

    def create_request(
        self, pub_thread_ts: str, content: str, user_id: str, priv_thread_ts: str
    ):
        print(f"Creating help request for user: {user_id}")
        linked_record = self.get_person(user_id)
        if not linked_record:
            print("User not found in airtable - HANDLE THIS")
            return None

        self.help_table.create(
            {
                "identifier": pub_thread_ts,
                "content": content,
                "person": [linked_record["id"]],
                "internal_thread": priv_thread_ts,
            }
        )
        return True

    def update_request(self, pub_thread_ts: str, **updates: dict):
        req = self.get_request(pub_thread_ts=pub_thread_ts)
        if not req:
            return
        self.help_table.update(req["id"], updates)

    def resolve_request(self, priv_thread_ts: str, resolver: str):
        resolver_item = self.get_person(resolver)
        if not resolver_item:
            return
        id = resolver_item.get("id")
        req = self.get_request(priv_thread_ts=priv_thread_ts)
        if not req:
            return
        return self.help_table.update(req["id"], {"resolver": [id]})

    def delete_req(self, pub_thread_ts: str):
        req = self.get_request(pub_thread_ts)
        if not req:
            return
        self.help_table.delete(req["id"])
