from dataclasses import asdict, dataclass, fields
from typing import Any

from fastapi import Request
from user_agents import parse

from includes.core.metadata import Metadata


@dataclass
class _DeviceInfo:
    device_type: str | None = None
    platform: str | None = None
    browser: str | None = None
    device: str | None = None
    platform_version: str | None = None
    browser_version: str | None = None

    is_mobile: bool = False
    is_pc: bool = False
    is_tablet: bool = False
    is_bot: bool = False

    accept_language: str | None = None
    client_timezone: str | None = None

    def load_config(self, request: Request) -> "_DeviceInfo":
        """Load client information from the current HTTP request."""

        self.accept_language = request.headers.get("Accept-Language", "")
        self.client_timezone = request.headers.get("X-Timezone", "")

        user_agent_string = request.headers.get("User-Agent", "")

        ua = parse(user_agent_string)

        # -------------------------
        # Device information
        # -------------------------
        self.device = ua.device.family
        self.device_type = self._get_device_type(ua)

        # -------------------------
        # Platform information
        # -------------------------
        self.platform = ua.os.family
        self.platform_version = ua.os.version_string

        # -------------------------
        # Browser information
        # -------------------------
        self.browser = ua.browser.family
        self.browser_version = ua.browser.version_string

        # -------------------------
        # Device flags
        # -------------------------
        self.is_mobile = ua.is_mobile
        self.is_pc = ua.is_pc
        self.is_tablet = ua.is_tablet
        self.is_bot = ua.is_bot

        return self

    @staticmethod
    def _get_device_type(ua: Any) -> str:
        """Return a normalized device type."""

        if ua.is_mobile:
            return "mobile"

        if ua.is_tablet:
            return "tablet"

        if ua.is_pc:
            return "desktop"

        return "unknown"

    def reset(self, request: Request) -> "_DeviceInfo":
        """Reset all values and reload them from the request."""

        default_instance = type(self)()

        for field_info in fields(self):
            setattr(
                self,
                field_info.name,
                getattr(default_instance, field_info.name),
            )

        return self.load_config(request)

    def update_from_dict(self, data: dict[str, Any]) -> "_DeviceInfo":
        """Update only fields that exist in this dataclass."""

        if not isinstance(data, dict):
            return self

        valid_fields = {field_info.name for field_info in fields(self)}

        for key, value in data.items():
            if key in valid_fields:
                setattr(self, key, value)

        return self

    def to_dict(self) -> dict[str, Any]:
        """Return client information as a dictionary."""

        return asdict(self)


# Global instance
DeviceInfo = _DeviceInfo()
