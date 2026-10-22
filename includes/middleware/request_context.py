import datetime as dt
from starlette.middleware.base import BaseHTTPMiddleware


from includes.function import load_svg_files
from includes.schemas.cookie import Cookie

from includes.core.ip import IP
from includes.core.metadata import MetaData
from includes.core.deviceinfo import DeviceInfo
from includes.core.globals.fun import load_json
from includes.core.globals.entry import app_context, fetchTime
from includes.core.globals.route_context import Route

from includes.src.referer import Referer
from includes.src.setting import Setting
from includes.src.request import Request
from includes.src.request import WebSocket


class DataBaseConnectionMiddleware(BaseHTTPMiddleware):

    def __init__(self, app):
        super().__init__(app)

    async def _load_setup_context(self, request):
        request.state.metadata = await request.state.metadata.get()

    # Shared Context Setup
    async def _setup_context(self, request):
        fetchTime.resate(dt.datetime.now())

        request.state.roote = Route(request)
        request.state.cookie = Cookie(request)
        request.state.setting = Setting(request)
        request.state.referer = Referer(request)
        request.state.metadata = MetaData(request)
        request.state.divice_info = DeviceInfo(request)

        await self._load_app_context(request)
        await self._load_setup_context(request)

        IP.get_info(request)

    async def _load_app_context(self, request):
        request.state.cookie.start()
        request.state.response = {"start_time": dt.datetime.now()}

        if not hasattr(app_context, "svg_lists"):
            app_context.svg_lists = await load_svg_files()

        if not hasattr(app_context, "config"):
            app_context.config = await load_json(app_context.folder, "config")

        if not hasattr(app_context, "language"):
            app_context.language = await load_json(app_context.folder, "lang")

    # HTTP Response Wrapper
    async def _http_send_wrapper(self, send, request):
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

                await request.state.cookie.setcookie(headers)
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
    async def _verify_client(self, send, request: Request) -> tuple[bool, str]:

        reason = None
        client_info = request.state.client_info or {}
        security = client_info.get("security", {})
        classification = client_info.get("classification", {})

        risk_score = security.get("risk_score", 0)

        # Known bot
        if request.state.divice_info.is_bot:
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

            if await self._verify_client(send, request):
                return

            await self.app(scope, receive, await self._http_send_wrapper(send, request))

        elif scope_type == "websocket":
            websocket = WebSocket(scope, receive, send)
            await self._setup_context(websocket)
            if await self._verify_client(send, websocket):
                return

            await self.app(scope, receive, send)

        else:
            request = Request(scope, receive)
            await self._setup_context(request)

            if await self._verify_client(send, request):
                return

            await self.app(scope, receive, send)
