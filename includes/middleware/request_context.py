import datetime as dt
from fastapi import Request, WebSocket


from includes.function import load_svg_files
from includes.core.ip import IP
from includes.core.globals.entry import app_context
from includes.core.metadata import MetaData
from includes.core.globals.fun import load_json
from includes.schemas.cookie import Cookie
from includes.schemas.router_schema import DynamicURLRoute
from includes.src.request import Requests
from includes.src.setting import Setting
from starlette.middleware.base import BaseHTTPMiddleware


class DataBaseConnectionMiddleware(BaseHTTPMiddleware):

    def __init__(self, app):
        super().__init__(app)
        self.app = app

    async def _load_setup_context(self):
        app_context.route = DynamicURLRoute.parse(app_context.request.path)

    # Shared Context Setup
    async def _setup_context(self, request_or_ws):
        app_context.request = Requests(request_or_ws)
        app_context.cookie = Cookie(request_or_ws)
        app_context.setting = Setting(request_or_ws)
        app_context.client_info = IP.get_info()

        await MetaData.reset()
        await self._load_app_context()
        await self._load_setup_context()

    async def _load_app_context(self):
        app_context.cookie.start()
        app_context.response = {"start_time": dt.datetime.now()}

        if not hasattr(app_context, "svg_lists"):
            app_context.svg_lists = await load_svg_files(app_context)

        if not hasattr(app_context, "config"):
            app_context.config = await load_json(app_context.folder, "config")

        if not hasattr(app_context, "language"):
            app_context.language = await load_json(app_context.folder, "lang")

    # HTTP Response Wrapper
    async def _http_send_wrapper(self, send):
        async def wrapper(message):
            if message["type"] == "http.response.start":
                headers = message.setdefault("headers", [])

                headers_dict = {k.decode().lower(): v.decode() for k, v in headers}

                if headers_dict.get("content-type") == "image/x-icon":
                    headers.append((b"cache-control", b"public, max-age=86400"))

                headers.extend(
                    [
                        (
                            b"strict-transport-security",
                            b"max-age=31536000; includeSubDomains; preload",
                        ),
                        (b"x-content-type-options", b"nosniff"),
                        (b"x-frame-options", b"SAMEORIGIN"),
                        (
                            b"content-security-policy",
                            b"object-src 'none'; base-uri 'self'",
                        ),
                    ]
                )

                await app_context.cookie.setcookie(headers)

                # print(headers)

            await send(message)

        return wrapper

    # Reject Request
    async def _reject_request(
        self, send, status_code: int = 403, detail: str = "Access denied"
    ):

        await send(
            {
                "type": "http.response.start",
                "status": status_code,
                "headers": [(b"content-type", b"application/json")],
            }
        )

        await send(
            {
                "type": "http.response.body",
                "body": (f'{{"success":false,"detail":"{detail}"}}').encode("utf-8"),
            }
        )

        return True

    # Client Verification
    async def _verify_client(self, send) -> tuple[bool, str]:

        reason = None
        client_info = app_context.client_info or {}
        device = client_info.get("device", {})
        security = client_info.get("security", {})
        classification = client_info.get("classification", {})

        risk_score = security.get("risk_score", 0)

        # print(device)

        # Known bot
        if device.get("is_bot"):
            reason = "Bot detected"

        # High risk traffic
        if risk_score >= 80:
            reason = "High risk request"

        # Datacenter + suspicious
        if classification.get("connection_type") == "datacenter" and risk_score >= 50:
            reason = "Datacenter traffic blocked"

        return (
            await self._reject_request(send=send, status_code=403, detail=reason)
            if reason
            else None
        )

    # Main Entry
    async def __call__(self, scope, receive, send):

        scope_type = scope["type"]

        if scope_type == "http":
            request = Request(scope, receive)
            await self._setup_context(request)

            if await self._verify_client(send):
                return

            await self.app(scope, receive, await self._http_send_wrapper(send))

        elif scope_type == "websocket":
            websocket = WebSocket(scope, receive, send)
            await self._setup_context(websocket)
            if await self._verify_client(send):
                return

            await self.app(scope, receive, send)

        else:
            request = Request(scope, receive)
            await self._setup_context(request)

            if await self._verify_client(send):
                return

            await self.app(scope, receive, send)
