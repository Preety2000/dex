from includes.src.request import Request
from user_agents import parse
from dataclasses import dataclass
from typing import Optional, Union
from dataclasses import asdict, dataclass


@dataclass
class DeviceInfo:
    device_type: Optional[str] = None
    platform: Optional[str] = None
    browser: Optional[str] = None
    device: Optional[str] = None
    platform_version: Optional[str] = None
    browser_version: Optional[str] = None

    is_mobile: bool = False
    is_pc: bool = False
    is_tablet: bool = False
    is_bot: bool = False

    accept_language: Optional[str] = None
    client_timezone: Optional[str] = None

    def __init__(self, request: Union[Request, str, None] = None):
        """Directly instantiate using: device_info = DeviceInfo(request)"""
        if request is not None:
            self.load_config(request)

    def load_config(self, request: Union[Request, str]) -> "DeviceInfo":
        """Load client information from the current HTTP request or User-Agent string."""

        # FastAPI Request Object handling
        if isinstance(request, Request):
            self.accept_language = request.headers.get("Accept-Language", "")
            self.client_timezone = request.headers.get("X-Timezone", "")
            user_agent_string = request.headers.get("User-Agent", "")
        else:
            # Direct User-Agent String handling (Testing or manual pass)
            user_agent_string = str(request)
            self.accept_language = ""
            self.client_timezone = ""

        ua = parse(user_agent_string)

        # Device information
        self.device = ua.device.family
        self.device_type = self._get_device_type(ua)

        # Platform information
        self.platform = ua.os.family
        self.platform_version = ua.os.version_string

        # Browser information
        self.browser = ua.browser.family
        self.browser_version = ua.browser.version_string

        # Device flags
        self.is_mobile = ua.is_mobile
        self.is_pc = ua.is_pc
        self.is_tablet = ua.is_tablet
        self.is_bot = ua.is_bot

        return self

    @staticmethod
    def _get_device_type(ua) -> str:
        """Helper method to derive device type string."""
        if ua.is_mobile:
            return "mobile"

        elif ua.is_tablet:
            return "tablet"

        elif ua.is_pc:
            return "desktop"

        elif ua.is_bot:
            return "bot"

        return "unknown"

    def to_dict(self) -> dict:
        """Convert the _DeviceInfo dataclass instance into a clean Python dictionary."""
        return asdict(self)
