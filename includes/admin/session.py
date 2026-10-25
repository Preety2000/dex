from dataclasses import dataclass, field
from datetime import datetime

from includes.core.deviceinfo import DeviceInfo


@dataclass
class LoginSession:
    divice: DeviceInfo = None
    timestamp: datetime = field(default_factory=datetime.utcnow)