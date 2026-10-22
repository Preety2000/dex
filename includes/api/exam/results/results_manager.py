from urllib.parse import urlparse

from includes.src.referer import Referer
from includes.src.request import Request
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

    def __init__(self, request: Request = None):
        self.request = request

    async def get_self_result(self, keys):
        self_result = SELF_RESULTS()
        return await self_result.index(keys)

    async def get_result(self, keys):
        self_result = IS_RESULTS(self.request)
        return await self_result.index(keys)

    async def result_manager(self):
        # Safely extract referer and params
        referer = getattr(self.request, "referer", Referer)

        # Get session member from cookies
        self.session_user = await self.request.state.setting.member()
        [a, b, option_keys, keys_private] = extract_url_parts(referer.path)

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

        if referer.path == "/exam/result":
            return json_response({"ss": "haha"})

        return json_response(
            {
                "url": keys_private,
                "path": referer.path,
                "params": referer.params,
            }
        )
