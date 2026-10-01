import os
import json

from includes.core.repo.dir_manager import folder


class JsonHandler:
    def __init__(self, filename):
        self.filename = filename
        self.filepath = os.path.join(folder.static_json, f"{self.filename}.json")

    async def get(self):

        try:
            if os.path.exists(self.filepath):
                with open(self.filepath, encoding="utf-8") as file:
                    return json.load(file)
            else:
                await self.save({})
                return {}

        except json.JSONDecodeError:
            os.remove(self.filepath)

            await self.save({})
            return {}

    async def save(self, data):
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
        with open(self.filepath, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
