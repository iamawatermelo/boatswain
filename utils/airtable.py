from pyairtable import Api


class AirtableManager:
    def __init__(self, api_key, base_id):
        api = Api(api_key)
        self.people_table = api.table(base_id, "people")
        self.help_table = api.table(base_id, "help")
        print("Connected to Airtable")

    def get_person(self, user_id):
        user = self.people_table.first(formula=f'{{slack_id}} = "{user_id}"')
        return user
    
    def get_request(self, pub_thread_ts):
        user = self.help_table.first(formula=f'{{identifier}} = "{pub_thread_ts}"')
        return user

    def create_request(
        self,
        pub_thread_ts,
        content,
        user_id,
        priv_thread_ts
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
                "person": [linked_record['id']],
                "internal_thread": priv_thread_ts
            }
        )

    def update_request(self, pub_thread_ts, **updates):
        req = self.get_request(pub_thread_ts=pub_thread_ts)
        if not req:
            return
        self.help_table.update(req["id"], updates)

    def delete_req(self, pub_thread_ts):
        req = self.get_request(pub_thread_ts)
        if not req:
            return
        self.help_table.delete(req["id"])
