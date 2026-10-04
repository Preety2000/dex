import json
import time

from includes.core.globals.entry import app_context
from includes.database.models.secondary import Terms
from includes.core.security import _Security
from includes.schemas.terms import get_terms_json


class Conversation:
    def __init__(self):
        app_context.response = {}
        self.request = app_context.request

    def sessioncr(self):
        # Sample data

        while True:
            create_time = time.time()
            yield f"data: create_time: {create_time}\n\n  "  # Use json.dumps to manually create a JSON string
            time.sleep(1)

    def session(self):
        # Get the JSON data from the request
        data = self.request.get_json()
        return self.sessioncr()

    @classmethod
    def query_return(cls, time, id, conversation_id):
        return {
            "message": {
                "id": id,
                "author": {"role": "assistant", "name": None, "metadata": {}},
                "create_time": time.time(),
                "content": {"content_type": "text", "parts": []},
                "status": "in_progress",
                "end_turn": None,
                "weight": 1.0,
            },
            "conversation_id": conversation_id
            or "3e4c3b73-8474-442b-a045-852162f58549",
            "error": None,
        }

    @classmethod
    def generate_typing_message_with_null(cls):

        message = f"## 😒 Sorry."
        data = cls.query_return(time, "null")
        text = ""
        for word in message.split(" "):
            text = word + " "
            data["message"]["content"]["parts"] = text
            yield "data: " + json.dumps(
                data, ensure_ascii=False
            ) + "\n\n"  # Use json.dumps to manually create a JSON string
            time.sleep(0.08)

    @classmethod
    async def index(cls):
        data = await app_context.request.json()
        try:
            # Get the JSON data from the request

            # Extract the 'path' value
            path = _Security.short_decode(data.get("key", None))
            # Extract the 'search' value
            search_value = data.get("search", None)

            if path == "search":
                category = (
                    app_context.db.query(Terms)
                    .filter(Terms.name == search_value)
                    .first()
                )
                category = get_terms_json(category)
                short_encode = _Security.short_encode(search_value)
                return cls.generate_typing_message(category, short_encode)
        except:
            pass

        return cls.generate_typing_message_with_null()

    @classmethod
    def generate_typing_message(cls, category, short_encode):

        message = f'## {category["name"]}\n\n {category["description"]} [{app_context.function.utc("Show related")}]({app_context.request.host_url}questions/tagged/{category["slug"]}).'
        # Sample data
        data = cls.query_return(
            time, short_encode, "3e4c3b73-8474-442b-a045-852162f58549"
        )
        text = ""
        for word in message.split(" "):
            text = word + " "
            data["message"]["content"]["parts"] = text
            # Use json.dumps to manually create a JSON string
            yield "data: " + json.dumps(data, ensure_ascii=False) + "\n\n"
            time.sleep(0.08)
