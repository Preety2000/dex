import os
import json
import random
import string

def random_string(length):
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


async def load_json(folder, filename):
    filepath = os.path.join(folder.static_json, f"{filename}.json")

    if os.path.exists(filepath):
        with open(filepath, encoding="utf-8") as file:
            data = json.load(file)
            return data

    return None
