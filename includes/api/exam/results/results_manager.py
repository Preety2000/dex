from urllib.parse import urlparse

from includes.api.exam.results.results_conducted import IS_RESULTS
from includes.api.exam.results.results_practice import SELF_RESULTS
from includes.core.globals.entry import app_context
from includes.utils.utils import json_null_response, json_response


def extract_url_parts(url):
    """Extract up to three path segments from a given URL."""
    path = urlparse(url).path.strip("/")
    parts = path.split("/")
    return parts[:4] + [None] * (4 - len(parts))


class API_RESULTS_MANAGER:
    def __init__(self):
        self.request = app_context.request
        self.function = app_context.function

    async def get_self_result(self, keys):
        self_result = SELF_RESULTS()
        return await self_result.index(keys)

    async def get_result(self, keys):
        self_result = IS_RESULTS()
        return await self_result.index(keys)

    async def result_manager(self):
        # Safely extract referer and params
        referer = getattr(app_context.request, "referer", {})
        path = referer.path
        params = referer.params
        # Get session member from cookies

        self.session_user = await app_context.setting.member()
        [a, b, option_keys, keys_private] = extract_url_parts(path)

        if keys_private:
            response = await self.get_self_result(keys_private)
            if response is None:
                return json_null_response()

            return json_response(response)

        elif option_keys:
            response = await self.get_result(option_keys)
            if response is None:
                return json_null_response()

            return json_response(response)

        if path == "/exam/result":
            return json_response({"ss": "haha"})

        return json_response(
            {
                "url": keys_private,
                "path": path,
                "params": params,
            }
        )
