import json
import base64
from dataclasses import dataclass

from fastapi import Request
from includes.utils._sub import configure_page
from includes.core.client_session import KS
from includes.core.config import MASTER_KEY, app_context
from includes.schemas.cache.member import MemberCache
from includes.core.security import _Security


from includes.utils.meb import serialize_member


@dataclass
class AuthAefValue:
    lang: int = 0
    theme: int = 0
    ckey: str = MASTER_KEY


class AUTH_TOKEN:

    @staticmethod
    def encode(data: dict) -> str:
        raw = json.dumps(data, separators=(",", ":")).encode("utf-8")
        encoded = base64.urlsafe_b64encode(raw).decode("utf-8")

        return encoded.rstrip("=")

    @staticmethod
    def decode(token: str) -> "AuthAefValue":
        try:
            padding = "=" * (-len(token) % 4)
            raw = base64.urlsafe_b64decode(token + padding)
            data = json.loads(raw.decode("utf-8"))

            if not isinstance(data, dict):
                return AuthAefValue()

            return AuthAefValue(**data)

        except Exception:
            return AuthAefValue()


class Setting:
    COOKIE_NAME = "_cf_bm"
    COOKIE_TTL = 60
    THEME_LIST = ["default", "light", "dark"]
    LANG_LIST = ["English", "Hindi", "Sanskrit", "Tamil", "Telugu"]

    def __init__(self, request: Request):
        self.request = request
        self._member = None
        self.setting_session = None

    # -------------------------------
    # Session Logic
    # -------------------------------

    async def initialize_settings(self) -> dict:
        auth_token = app_context.cookie.get(self.COOKIE_NAME)
        # self.setting_session = KS.get(app_context.request.ip)

        if not self.setting_session:
            auth_token_dict = AUTH_TOKEN.decode(auth_token)
            self.setting_session = {
                "theme": Setting.THEME_LIST[auth_token_dict.theme],
                "language": Setting.LANG_LIST[auth_token_dict.lang],
                "themeCode": auth_token_dict.theme,
                "languageCode": auth_token_dict.lang,
                "MASTER_KEY": auth_token_dict.ckey,
            }

            await self._attach_active_member(self.setting_session)
            self._sync_global_state(self.setting_session)

        if not auth_token:
            self.update_cookie()

        return self.setting_session

    async def _attach_active_member(self, session: dict) -> None:
        master_key = session.get("MASTER_KEY")

        if master_key and master_key != MASTER_KEY:
            member_info = await self._attach_member_with_d(master_key)
            if member_info:
                member_id = member_info.get("id")
                session.update(
                    {
                        "user_id": member_id,
                        "auth_session": member_info,
                        "id": _Security.short_encode(member_id),
                    }
                )

    async def _attach_member_with_d(self, master_key: str) -> None:
        query_parts = master_key.split("///")
        member_secret_key = query_parts[0]
        device_key = query_parts[1]

        member = await MemberCache.get_with_secret(member_secret_key)
        if not member:
            return {}

        member = serialize_member(member)
        return member if device_key in member.get("device", []) else {}

    def _sync_global_state(self, session: dict) -> None:
        self.request.state.theme = session.get("theme")
        self.request.state.language = session.get("language")
        self.request.state.themeCode = session.get("themeCode")
        self.request.state.languageCode = session.get("languageCode")
        self.request.state.auth_session = session.get("auth_session")

    # -------------------------------
    # Public API
    # -------------------------------
    async def preferences(self):
        q = await self.initialize_settings()
        return q

    async def get(self, key: str | None = None, default=None):
        session = await self.initialize_settings()
        return session.get(key, default) if key else session

    async def member(self, key: str | None = None, default=None):
        if self._member is None:
            session = await self.initialize_settings()
            self._member = session.get("auth_session", None)

        if self._member and key:
            return self._member.get(key, default)

        return self._member

    def update_cookie(self) -> bool:

        if not self.setting_session:
            return False

        auth_token = AUTH_TOKEN.encode(
            {
                "lang": self.setting_session.get("languageCode"),
                "theme": self.setting_session.get("themeCode"),
                "ckey": self.setting_session.get("MASTER_KEY"),
            }
        )

        app_context.cookie.domain(self.COOKIE_NAME, auth_token, self.COOKIE_TTL)
        return True

    # -------------------------------
    # Controller Entry
    # -------------------------------

    def handle_request(self, parameter: str):
        app_context.response["active"] = {parameter: "active"}
        if parameter == "profiles" and self.request.method == "POST":
            # self.profiles(parameter)
            return app_context.settingparams.json
        
        configure_page(template="query/setting", title="Setting", suffix=True)
        return {}
